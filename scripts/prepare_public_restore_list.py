"""Skip only an existing public-schema creation entry in a pg_restore TOC.

Use solely for a reviewed public-schema dump and a NEW disposable restore DB.
Does not connect to PostgreSQL, run a restore, or ignore restore errors.
"""
import argparse
from pathlib import Path
import re


def prepare(lines: str) -> str:
    pattern = re.compile(r'^\d+; \d+ \d+ SCHEMA - public \S+\s*$')
    result = []
    skipped = 0
    for line in lines.splitlines(keepends=True):
        if pattern.fullmatch(line.rstrip('\r\n')):
            result.append('; Existing empty-target public schema: ' + line)
            skipped += 1
        else:
            result.append(line)
    if skipped != 1:
        raise ValueError('Expected exactly one SCHEMA - public TOC entry; inspect this dump manually.')
    return ''.join(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = prepare(args.input.read_text(encoding='utf-8'))
    with args.output.open('x', encoding='utf-8') as file:
        file.write(result)
    print('Prepared restore list: skipped exactly one public SCHEMA creation; all other entries preserved.')


if __name__ == '__main__':
    main()
