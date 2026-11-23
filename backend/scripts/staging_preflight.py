"""Read-only SQL security/schema/knowledge checks. Does not verify cloud settings."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import select, text
from app.core.config import settings
from app.db.session import engine
from app.db.models.chunk import Chunk
from app.modules.knowledge.verification import vector_storage_bytes
from sqlalchemy.orm import Session

TABLES = ('users','resumes','resume_analyses','interview_sessions','interview_turns',
          'interview_reports','practice_sessions','practice_questions','practice_attempts',
          'chunks','alembic_version','staging_ai_usage')
DEFAULT_MANIFEST = Path(__file__).resolve().parents[1] / 'deployment/software-engineer-reviewed.json'


def check_knowledge(db, manifest, expected_total=30):
    failures = []
    rows = list(db.scalars(select(Chunk)))
    expected = {row['source_name']: row for row in manifest['rows']}
    scoped = [row for row in rows if row.role == 'software_engineer']
    if len(rows) != expected_total or len(scoped) != 30 or len(expected) != 30:
        failures.append('Knowledge count/scope does not match the reviewed initialization.')
    if Counter(row.difficulty for row in scoped) != {'easy':10,'medium':10,'hard':10}:
        failures.append('Knowledge difficulty coverage differs.')
    if {row.source_name for row in scoped} != set(expected):
        failures.append('Knowledge source identities differ.')
    for row in scoped:
        exp = expected.get(row.source_name)
        if exp is None:
            continue
        keys = ('source_name','role','topic','subtopic','difficulty','source_url','license','content_hash')
        if any(getattr(row, key) != exp[key] for key in keys) or hashlib.sha256(row.content.encode()).hexdigest() != exp['content_sha256']:
            failures.append(f'Knowledge metadata/content mismatch: {row.source_name}')
        try:
            actual = hashlib.sha256(vector_storage_bytes(row.embedding, 768)).hexdigest()
            if actual != exp['vector_float32_sha256']:
                raise ValueError()
        except (TypeError, ValueError):
            failures.append(f'Knowledge vector mismatch: {row.source_name}')
    # Exercise the actual SQL operator/search path and role/difficulty filters,
    # without requesting a new query embedding or claiming a semantic evaluation.
    from app.modules.knowledge.retriever import _query_chunks_by_embedding
    for difficulty in ('easy','medium','hard'):
        sample = next((row for row in scoped if row.difficulty == difficulty), None)
        if sample is not None:
            hits = _query_chunks_by_embedding(db, sample.embedding, 3, role='software_engineer', difficulty=difficulty)
            if len(hits) != 3 or any(row.role != 'software_engineer' or row.difficulty != difficulty for row in hits):
                failures.append(f'Scoped pgvector probe failed: {difficulty}')
    return failures


def check_security(db):
    failures = []
    role = db.execute(text('SELECT rolsuper, rolbypassrls, rolcreatedb, rolcreaterole, rolreplication FROM pg_roles WHERE rolname=current_user')).one()
    if any(role):
        failures.append('Runtime login has privileged role attributes.')
    if db.scalar(text("SELECT count(*) FROM pg_roles WHERE (rolsuper OR rolbypassrls OR rolcreatedb OR rolcreaterole OR rolreplication) AND pg_has_role(current_user,oid,'MEMBER')")):
        failures.append('Runtime login inherits a privileged role.')
    if not db.scalar(text("SELECT pg_has_role(current_user,'prepmate_runtime','USAGE')")):
        failures.append('Runtime login does not inherit the dedicated runtime group.')
    relations = db.execute(text("SELECT c.relname,c.relrowsecurity,c.relforcerowsecurity,pg_has_role(current_user,c.relowner,'MEMBER') AS owned FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND c.relkind IN ('r','p','v','m','f')")).all()
    if {row.relname for row in relations} != set(TABLES):
        failures.append('Unexpected/missing public relations; review all exposed views/tables.')
    for row in relations:
        if row.relname in TABLES and (not row.relrowsecurity or not row.relforcerowsecurity or row.owned):
            failures.append(f'Unsafe runtime ownership/RLS: {row.relname}')
    api_roles = db.scalars(text("SELECT rolname FROM pg_roles WHERE rolname IN ('anon','authenticated','service_role')")).all()
    for table in TABLES:
        if not db.scalar(text('SELECT to_regclass(:name)'), {'name':f'public.{table}'}):
            continue
        if table in ('chunks','alembic_version') and db.scalar(text("SELECT has_table_privilege(current_user,:name,'INSERT,UPDATE,DELETE,TRUNCATE,TRIGGER,REFERENCES') OR has_any_column_privilege(current_user,:name,'INSERT,UPDATE,REFERENCES')"), {'name':f'public.{table}'}):
            failures.append(f'Runtime retains write privileges on read-only table: {table}')
        policies = db.execute(text("SELECT policyname,roles,cmd,qual,with_check FROM pg_policies WHERE schemaname='public' AND tablename=:name"), {'name':table}).all()
        if len(policies) != 1 or list(policies[0]) != ['prepmate_backend_only',['prepmate_runtime'],'ALL','true','true']:
            failures.append(f'Unexpected policy: {table}')
        for role_name in api_roles:
            values = {'role':role_name, 'name':f'public.{table}'}
            allowed = db.scalar(text("SELECT has_table_privilege(:role,:name,'SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER') OR has_any_column_privilege(:role,:name,'SELECT,INSERT,UPDATE,REFERENCES')"), values)
            if allowed:
                failures.append(f'Data API role retains table/column privileges: {role_name}/{table}')
    for role_name in api_roles:
        if db.scalar(text("SELECT has_schema_privilege(:role,'public','CREATE')"), {'role':role_name}):
            failures.append(f'Data API role can create public objects: {role_name}')
        for sequence in db.scalars(text("SELECT c.oid::regclass::text FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND c.relkind='S'")):
            if db.scalar(text("SELECT has_sequence_privilege(:role,:name,'USAGE,SELECT,UPDATE')"), {'role':role_name,'name':sequence}):
                failures.append(f'Data API role retains sequence privileges: {role_name}/{sequence}')
    if db.scalar(text("SELECT count(*) FROM pg_default_acl d CROSS JOIN LATERAL aclexplode(d.defaclacl) a LEFT JOIN pg_roles r ON r.oid=a.grantee WHERE d.defaclnamespace IN (0,'public'::regnamespace::oid) AND d.defaclobjtype IN ('r','S') AND d.defaclrole IN (SELECT relowner FROM pg_class WHERE oid='public.users'::regclass) AND (a.grantee=0 OR r.rolname IN ('anon','authenticated','service_role'))")):
        failures.append('Migration owner retains unsafe default table/sequence grants.')
    # Public RPC defaults and security-definer functions need explicit review even
    # when Data API is disabled. Extensions belong in their provider schema.
    if db.scalar(text("SELECT count(*) FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='public' AND (p.prosecdef OR NOT EXISTS (SELECT 1 FROM pg_depend d JOIN pg_extension e ON e.oid=d.refobjid WHERE d.classid='pg_proc'::regclass AND d.objid=p.oid AND d.refclassid='pg_extension'::regclass AND e.extname='vector' AND d.deptype='e'))")):
        failures.append('Public routines exist: review RPC/security-definer exposure separately.')
    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--knowledge-manifest', type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    if settings.app_env != 'production' or not settings.staging_enabled:
        parser.error('Use the intended restricted production-mode staging runtime environment.')
    manifest = json.loads(args.knowledge_manifest.read_text())
    try:
        with Session(engine) as db:
            db.execute(text('SET TRANSACTION READ ONLY'))
            failures = check_security(db)
            expected_head = ScriptDirectory.from_config(Config(str(Path(__file__).resolve().parents[1] / 'alembic.ini'))).get_current_head()
            if db.scalar(text('SELECT version_num FROM alembic_version')) != expected_head:
                failures.append('Migrations are not at the single current head.')
            if not db.scalar(text("SELECT 1 FROM pg_extension WHERE extname='vector'")):
                failures.append('pgvector extension is missing.')
            failures += check_knowledge(db, manifest)
        print(json.dumps({'read_only':True,'passed':not failures,'failures':failures,'cloud_data_api_setting_verified':False}, indent=2))
        return int(bool(failures))
    except Exception:
        # Do not dump connection URLs, rows or provider details to operator logs.
        print(json.dumps({'read_only':True,'passed':False,'failures':['Preflight could not complete. Inspect the target/roles/migrations securely.']}))
        return 1
    finally:
        engine.dispose()


if __name__ == '__main__':
    raise SystemExit(main())
