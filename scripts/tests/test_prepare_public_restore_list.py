import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location('restore_list', Path(__file__).resolve().parents[1] / 'prepare_public_restore_list.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_preserves_every_other_restore_entry():
    original = '; Archive\n12; 2615 2200 SCHEMA - public owner\n13; 1259 123 TABLE public users owner\n14; 0 0 POLICY public users backend owner\n'
    actual = module.prepare(original)
    assert actual.splitlines()[2:] == original.splitlines()[2:]
    assert actual.splitlines()[1] == '; Existing empty-target public schema: ' + original.splitlines()[1]


@pytest.mark.parametrize('lines', ['', '12; 2615 2200 SCHEMA - other owner\n', '12; 2615 2200 SCHEMA - public owner\n13; 2615 2200 SCHEMA - public owner\n'])
def test_refuses_unexpected_or_duplicate_schema_entries(lines):
    with pytest.raises(ValueError): module.prepare(lines)
