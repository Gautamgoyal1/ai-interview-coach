import hashlib
import json

import pytest

from scripts.export_staging_knowledge import reviewed_bundle
from scripts.initialize_staging_knowledge import validate_bundle
from app.modules.knowledge.verification import vector_storage_bytes


def inputs():
    rows, expected = [], []
    for number in range(30):
        content = f'Synthetic reviewed knowledge {number}'
        row = dict(source_name=f'synthetic:{number}',topic='SQL',subtopic='Transactions',difficulty=['easy','medium','hard'][number//10],
                   role='software_engineer',content=content,source_url='https://www.postgresql.org/docs/current/',license='test fixture',
                   content_hash=hashlib.sha256(content.encode()).hexdigest(),retired=False)
        exp = {key:value for key,value in row.items() if key not in ('content','retired')}
        exp.update(content_sha256=hashlib.sha256(content.encode()).hexdigest(),vector_float32_sha256=hashlib.sha256(vector_storage_bytes([1.0]*768)).hexdigest())
        rows.append(row); expected.append(exp)
    source = json.dumps({'rows':rows}).encode()
    cache = json.dumps({'model':'gemini-embedding-001','dimensions':768,'documents':{r['content_hash']:[1.0]*768 for r in rows}}).encode()
    manifest = dict(model='gemini-embedding-001', dimensions=768, rows=expected,
                    frozen_inputs={'source_manifest':hashlib.sha256(source).hexdigest(),'vector_cache':hashlib.sha256(cache).hexdigest()})
    return manifest,source,cache


def test_export_frozen_scope_and_correct_vectors_without_provider_calls():
    manifest,source,cache = inputs()
    bundle = reviewed_bundle(manifest,source,cache)
    assert len(validate_bundle(bundle,manifest)) == 30
    with pytest.raises(ValueError, match='hash changed'):
        reviewed_bundle(manifest,source+b' ',cache)


@pytest.mark.parametrize('change', ['vector','content','role','extra','missing','duplicate'])
def test_initializer_refuses_corruption_or_scope_changes(change):
    manifest,source,cache = inputs()
    bundle = reviewed_bundle(manifest,source,cache)
    if change=='vector': bundle['rows'][0]['embedding'][0]=1.5
    elif change=='content': bundle['rows'][0]['content']+='changed'
    elif change=='role': bundle['rows'][0]['role']='ml_engineer'
    elif change=='extra': bundle['rows'][0]['id']=123
    elif change=='missing': bundle['rows'].pop()
    elif change=='duplicate': bundle['rows'][-1]=bundle['rows'][0]
    with pytest.raises(ValueError): validate_bundle(bundle,manifest)
