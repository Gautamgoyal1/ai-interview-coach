import math
import struct

import pytest

from app.modules.knowledge.verification import verify_stored_vector


def sample():
    return [0.123456789, -0.234567891] + [0.0] * 766


def f32(value):
    return struct.unpack("!f", struct.pack("!f", value))[0]


def test_accepts_exact_float32_and_shortest_roundtrip_decoding():
    expected = sample()
    rounded = [f32(x) for x in expected]
    decoded = [float(format(x, ".9g")) for x in rounded]
    assert decoded != rounded  # Reproduces the original faulty equality check.
    verify_stored_vector(rounded, expected)
    verify_stored_vector(decoded, expected)


def test_rejects_a_single_float32_ulp_change():
    expected = sample()
    actual = expected.copy()
    bits = struct.unpack("!I", struct.pack("!f", actual[0]))[0]
    actual[0] = struct.unpack("!f", struct.pack("!I", bits + 1))[0]
    with pytest.raises(ValueError, match="differs"):
        verify_stored_vector(actual, expected)


@pytest.mark.parametrize(
    "corruption", ["sign", "dimension", "nan", "infinity", "overflow"]
)
def test_rejects_invalid_or_corrupted_vectors(corruption):
    expected = sample()
    actual = expected.copy()
    if corruption == "sign":
        actual[1] = -actual[1]
    elif corruption == "dimension":
        actual.pop()
    elif corruption == "nan":
        actual[0] = math.nan
    elif corruption == "infinity":
        actual[0] = math.inf
    else:
        actual[0] = 1e100
    with pytest.raises(ValueError):
        verify_stored_vector(actual, expected)


def test_rejects_nonfinite_expected_vector():
    with pytest.raises(ValueError, match="nonfinite"):
        verify_stored_vector(sample(), [math.nan] + [0.0] * 767)
