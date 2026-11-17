"""Compare pgvector values at their actual float32 storage precision."""

import math
import struct
from collections.abc import Sequence


def vector_storage_bytes(values: Sequence[float], dimensions: int = 768) -> bytes:
    """Canonical float32 bytes, independent of a client's decimal decoding."""
    if len(values) != dimensions:
        raise ValueError("Vector dimension mismatch")
    numbers = [float(value) for value in values]
    if not all(math.isfinite(value) for value in numbers):
        raise ValueError("Vector contains nonfinite values")
    try:
        return struct.pack(f"!{dimensions}f", *numbers)
    except (OverflowError, struct.error) as exc:
        raise ValueError("Vector component exceeds float32 range") from exc


def verify_stored_vector(
    actual: Sequence[float], expected: Sequence[float], dimensions: int = 768
) -> None:
    """Reject even a one-ULP change while accepting valid text round-trips.

    Some clients parse PostgreSQL's shortest-roundtrip float32 text into Python
    float64 values. Numeric equality with the exact float32 value is therefore
    inappropriate; compare the float32 bits each value actually represents.
    """
    if vector_storage_bytes(actual, dimensions) != vector_storage_bytes(
        expected, dimensions
    ):
        raise ValueError("Stored float32 vector differs from the evaluated vector")
