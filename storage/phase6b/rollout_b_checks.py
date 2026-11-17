"""Read-only integrity helpers for the separately approved one-off rollout."""
import hashlib,json,math,struct,sys
from pathlib import Path
from collections import Counter
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
if (ROOT/'backend').exists(): sys.path.insert(0,str(ROOT/'backend'))
TOKEN='5b7b004975edfd5ae85ef47943e725bf4b5e252bc7c26735a46395efd2d84070'
CACHE='fbf87e80d48c2c0f2926316aa451760791a5994ecf47a75e4cf854d89cde40c9'
MANIFEST='fcf5c52bc3e86222832dca72c98146272f762b7f1bd4c73028e3c4f495c8780d'
REQUEST='2808da2d365ad56b943629b1777c9c82b07cb55c77665506050f25b25e77f79b'
OUT=BASE/'rollout-b'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def canonical(value): return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def ident(value): return '"'+value.replace('"','""')+'"'
def frozen():
    from dataclasses import asdict
    from app.core.config import settings
    from app.modules.knowledge.ingestion import load_items
    assert sha(BASE/'approved-vectors.json')==CACHE,'Vector cache hash changed'
    assert sha(BASE/'software-manifest.json')==MANIFEST,'Source manifest hash changed'
    assert sha(BASE/'embedding-request-manifest.json')==REQUEST,'Request changed'
    inventory=read(BASE/'approval-a-artifact-inventory.json')
    assert all(sha(BASE/name)==h for name,h in inventory['files'].items()),'Frozen evidence changed'
    ready=read(BASE/'evaluation-readiness.json')
    assert all(sha(ROOT/s['file'])==s['source_sha256'] for s in ready['sources']),'Source file changed'
    assert sha(ROOT/'eval_data/phase6b_software_semantic.json')==ready['dataset_sha256'],'Dataset changed'
    manifest=read(BASE/'software-manifest.json');cache=read(BASE/'approved-vectors.json');preview=read(BASE/'preview-software-only.json')
    assert preview['approval_token']==TOKEN and len(preview['changes'])==30 and all(c['action']=='insert' and c['old_id'] is None for c in preview['changes'])
    assert settings.embedding_model==cache['model']==manifest['model']=='gemini-embedding-001'
    assert settings.embedding_dimensions==cache['dimensions']==768
    assert cache['document_task_type']=='RETRIEVAL_DOCUMENT'
    items=[asdict(i) for i in load_items(ROOT/'knowledge_base',settings.embedding_model,768) if i.role=='software_engineer']
    assert items==manifest['rows'] and len(items)==30
    for r in items:
        h=hashlib.sha256(r['content'].encode()).hexdigest();v=cache['documents'][h]
        assert len(v)==768 and all(math.isfinite(x) for x in v) and any(v)
    return manifest,cache,preview
TABLES="SELECT schemaname,tablename FROM pg_tables WHERE schemaname NOT IN ('pg_catalog','information_schema') AND schemaname NOT LIKE 'pg_toast%' AND schemaname NOT LIKE 'pg_temp%' ORDER BY schemaname,tablename"
SCHEMA_SQL="""SELECT n.nspname AS schema,c.relname AS relation,c.relkind,a.attnum,a.attname,format_type(a.atttypid,a.atttypmod) AS type,a.attnotnull,a.attidentity,a.attgenerated,pg_get_expr(d.adbin,d.adrelid) AS default_expr FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace JOIN pg_attribute a ON a.attrelid=c.oid LEFT JOIN pg_attrdef d ON d.adrelid=c.oid AND d.adnum=a.attnum WHERE c.relkind IN ('r','p') AND n.nspname NOT IN ('pg_catalog','information_schema') AND n.nspname NOT LIKE 'pg_%' AND a.attnum>0 AND NOT a.attisdropped ORDER BY n.nspname,c.relname,a.attnum"""
CONSTRAINT_SQL="""SELECT n.nspname AS schema,c.relname AS relation,k.conname,pg_get_constraintdef(k.oid) AS definition FROM pg_constraint k JOIN pg_class c ON c.oid=k.conrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname NOT IN ('pg_catalog','information_schema') AND n.nspname NOT LIKE 'pg_%' ORDER BY n.nspname,c.relname,k.conname"""
INDEX_SQL="SELECT schemaname,tablename,indexname,indexdef FROM pg_indexes WHERE schemaname NOT IN ('pg_catalog','information_schema') AND schemaname NOT LIKE 'pg_%' ORDER BY schemaname,tablename,indexname"
SEQUENCES="SELECT schemaname,sequencename FROM pg_sequences WHERE schemaname NOT IN ('pg_catalog','information_schema') AND schemaname NOT LIKE 'pg_%' ORDER BY schemaname,sequencename"
def jsonquery(sql): return 'SELECT row_to_json(q)::text FROM ('+sql+') q'
def state(fetch):
    tables=[json.loads(x) for x in fetch(jsonquery(TABLES))]
    result={'tables':{},'sequences':{},'schema':{}}
    for t in tables:
        s,n=t['schemaname'],t['tablename']
        rows=fetch('SELECT row_to_json(t)::text FROM '+ident(s)+'.'+ident(n)+' t ORDER BY row_to_json(t)::text COLLATE "C"')
        result['tables'][s+'.'+n]={'rows':len(rows),'digest':hashlib.sha256(('\n'.join(rows)+'\n').encode()).hexdigest()}
    for label,sql in [('columns',SCHEMA_SQL),('constraints',CONSTRAINT_SQL),('indexes',INDEX_SQL)]: result['schema'][label]=canonical(fetch(jsonquery(sql)))
    for s in [json.loads(x) for x in fetch(jsonquery(SEQUENCES))]:
        name=s['schemaname']+'.'+s['sequencename']
        result['sequences'][name]=json.loads(fetch(jsonquery('SELECT last_value,is_called FROM '+ident(s['schemaname'])+'.'+ident(s['sequencename'])))[0])
    return result

def check_rows(db,post):
    from sqlalchemy import select
    from app.db.models.chunk import Chunk
    manifest=read(BASE/'software-manifest.json');cache=read(BASE/'approved-vectors.json');snapshot=read(BASE/'legacy-snapshot.json')
    rows=list(db.scalars(select(Chunk).order_by(Chunk.id)))
    legacy=[r for r in rows if r.id in {x['id'] for x in snapshot['rows']}]
    values=[{**{key:getattr(r,key) for key in ('id','topic','subtopic','difficulty','role','content','source_name','source_url','license','content_hash')},'embedding':[float(x) for x in r.embedding],'created_at':str(r.created_at)} for r in legacy]
    assert len(legacy)==31 and canonical(values)==snapshot['digest'],'Legacy data changed'
    expected={r['source_name']:r for r in manifest['rows']}
    new=[r for r in rows if r.id not in {x['id'] for x in snapshot['rows']}]
    assert len(rows)==(61 if post else 31) and len(new)==(30 if post else 0),'Unexpected corpus scope'
    if post:
        assert {r.source_name for r in new}==set(expected)
        assert Counter(r.difficulty for r in new)=={'easy':10,'medium':10,'hard':10}
        for r in new:
            exp=expected[r.source_name]
            assert all(getattr(r,k)==v for k,v in exp.items() if k!='retired'),'New row metadata/content mismatch'
            vector=cache['documents'][hashlib.sha256(exp['content'].encode()).hexdigest()]
            verify_storage_vector(r.embedding,vector)
    return {'total_rows':len(rows),'legacy_rows_verified':len(legacy),'new_rows_verified':len(new),'new_vectors_match_evaluated_float32':len(new),'legacy_digest':snapshot['digest']}

def unchanged_other_data(before,after):
    assert before['schema']==after['schema'],'Schema changed'
    assert before['tables'].keys()==after['tables'].keys(),'Table set changed'
    assert all(v==after['tables'][k] for k,v in before['tables'].items() if k!='public.chunks'),'Non-knowledge data changed'
    assert before['sequences'].keys()==after['sequences'].keys()
    assert all(v==after['sequences'][k] for k,v in before['sequences'].items() if k!='public.chunks_id_seq'),'Other sequence changed'


def compare_restored_backup(baseline,restored,live_indexes,restored_indexes):
    # Preserve substantive index checks. Normalize only the exact fixed two-element
    # varchar-to-text array representation observed in the verified dump restore.
    before="((ARRAY['processing'::character varying, 'completed'::character varying])::text[])"
    after="(ARRAY[('processing'::character varying)::text, ('completed'::character varying)::text])"
    normalize=lambda rows:[{**r,'indexdef':r['indexdef'].replace(before,after)} for r in rows]
    assert baseline['tables']==restored['tables'],'Restored table data differs'
    assert baseline['sequences']==restored['sequences'],'Restored sequences differ'
    assert baseline['schema'].keys()==restored['schema'].keys()
    assert all(baseline['schema'][k]==restored['schema'][k] for k in baseline['schema'] if k!='indexes'),'Restored schema differs'
    assert normalize(live_indexes)==normalize(restored_indexes),'Substantive index mismatch'


def verify_storage_vector(actual, expected):
    from app.modules.knowledge.verification import verify_stored_vector
    verify_stored_vector(actual, expected)
