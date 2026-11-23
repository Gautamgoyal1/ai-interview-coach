"""Offline export of exactly 30 reviewed documents/vectors; no DB or API calls."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.modules.knowledge.verification import vector_storage_bytes


def reviewed_bundle(manifest, source_bytes, vector_bytes):
    frozen = manifest['frozen_inputs']
    for name, data in [('source_manifest',source_bytes),('vector_cache',vector_bytes)]:
        if hashlib.sha256(data).hexdigest() != frozen[name]:
            raise ValueError('Frozen reviewed input hash changed')
    source, cache = json.loads(source_bytes), json.loads(vector_bytes)
    if cache['model'] != 'gemini-embedding-001' or cache['dimensions'] != 768:
        raise ValueError('Embedding identity changed')
    expected = {row['source_name']:row for row in manifest['rows']}
    rows = []
    for row in source['rows']:
        exp = expected[row['source_name']]
        if row['role'] != 'software_engineer' or row['retired']:
            raise ValueError('Unapproved role or retired content')
        item = {key:value for key,value in row.items() if key != 'retired'}
        content_hash = hashlib.sha256(item['content'].encode()).hexdigest()
        if content_hash != exp['content_sha256']:
            raise ValueError('Reviewed content changed')
        for key,value in exp.items():
            if key not in ('content_sha256','vector_float32_sha256') and item[key] != value:
                raise ValueError('Reviewed metadata changed')
        item['embedding'] = cache['documents'][content_hash]
        if hashlib.sha256(vector_storage_bytes(item['embedding'])).hexdigest() != exp['vector_float32_sha256']:
            raise ValueError('Reviewed vector changed')
        rows.append(item)
    if len(rows) != 30 or len({row['source_name'] for row in rows}) != 30:
        raise ValueError('Expected exactly 30 distinct reviewed records')
    return {'model':'gemini-embedding-001','dimensions':768,'rows':rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-manifest', type=Path, required=True)
    parser.add_argument('--vector-cache', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads((Path(__file__).resolve().parents[1] / 'deployment/software-engineer-reviewed.json').read_text())
    bundle = reviewed_bundle(manifest, args.source_manifest.read_bytes(), args.vector_cache.read_bytes())
    # Refuse overwriting prior export/evidence.
    with args.output.open('x', encoding='utf-8') as file:
        file.write(json.dumps(bundle, separators=(',',':'))+'\n')
    print(json.dumps({'rows':30,'embedding_calls':0,'sha256':hashlib.sha256(args.output.read_bytes()).hexdigest()}))


if __name__ == '__main__':
    main()
