"""Preview-first, reviewed 30-record seed for a NEW staging database, no API calls."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import engine
from app.db.models.chunk import Chunk
from app.modules.knowledge.verification import vector_storage_bytes
from scripts.staging_preflight import DEFAULT_MANIFEST, check_knowledge


def validate_bundle(bundle, manifest):
    if bundle.get('model') != manifest['model'] or bundle.get('dimensions') != 768:
        raise ValueError('Unreviewed embedding identity')
    rows = bundle.get('rows', [])
    expected = {row['source_name']:row for row in manifest['rows']}
    if len(rows) != 30 or {row['source_name'] for row in rows} != set(expected):
        raise ValueError('Unreviewed knowledge scope')
    for row in rows:
        exp = expected[row['source_name']]
        if set(row) != {'source_name','topic','subtopic','difficulty','role','content','source_url','license','content_hash','embedding'}:
            raise ValueError('Unexpected knowledge fields')
        if row['role'] != 'software_engineer' or any(row[key] != value for key,value in exp.items() if key not in ('content_sha256','vector_float32_sha256')):
            raise ValueError('Unreviewed metadata')
        if hashlib.sha256(row['content'].encode()).hexdigest() != exp['content_sha256'] or hashlib.sha256(vector_storage_bytes(row['embedding'])).hexdigest() != exp['vector_float32_sha256']:
            raise ValueError('Unreviewed content/vector')
    return rows


def initialize(db, rows, manifest, apply=False):
    if apply:
        db.execute(text('SELECT pg_advisory_xact_lock(634220061)'))
    existing = db.scalar(select(text('count(*)')).select_from(Chunk))
    if existing:
        failures = check_knowledge(db, manifest, expected_total=30)
        if failures:
            raise ValueError('Refusing nonempty/unreviewed knowledge database')
        return {'inserts':0,'updates':0,'deletions':0,'existing_reviewed':30}
    if apply:
        db.add_all(Chunk(**row) for row in rows)
        db.flush()
        db.expire_all()
        if check_knowledge(db, manifest, expected_total=30):
            raise ValueError('Stored knowledge verification failed; transaction must roll back')
    return {'inserts':30,'updates':0,'deletions':0,'existing_reviewed':0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--sha256', required=True, help='Reviewed bundle SHA-256, required even for preview')
    parser.add_argument('--apply', action='store_true', help='Explicitly authorized new-staging initialization only')
    args = parser.parse_args()
    data = args.bundle.read_bytes()
    if hashlib.sha256(data).hexdigest() != args.sha256:
        parser.error('Bundle hash differs from reviewed input')
    manifest = json.loads(DEFAULT_MANIFEST.read_text())
    rows = validate_bundle(json.loads(data), manifest)
    if args.apply and (settings.app_env != 'production' or not settings.staging_enabled):
        parser.error('Apply requires an explicitly configured restricted staging environment')
    try:
        with Session(engine) as db, db.begin():
            if not args.apply:
                db.execute(text('SET TRANSACTION READ ONLY'))
            result = initialize(db, rows, manifest, apply=args.apply)
        print(json.dumps({**result,'applied':args.apply,'embedding_calls':0,'bundle_sha256':args.sha256}))
        return 0
    except Exception:
        print(json.dumps({'applied':False,'error':'Initialization refused or rolled back. Inspect target, schema and reviewed inputs securely.'}))
        return 1
    finally:
        engine.dispose()


if __name__ == '__main__':
    raise SystemExit(main())
