
"""Metrics for evaluating evidence-grounding classifications."""

from collections.abc import Iterable
from typing import TypedDict


class GroundingLabel(TypedDict):
    expected_supported: bool
    predicted_supported: bool


def calculate_grounding_metrics(
    evaluations: Iterable[GroundingLabel],
) -> dict:
    """Compare predicted support labels against reference labels.

    A supported claim is positive for the support-class metrics.
    An unsupported claim is positive for the unsupported-detection metrics.
    Undefined metrics are returned as None rather than treated as zero.
    """
    rows = list(evaluations)

    if any(
        type(row.get("expected_supported")) is not bool
        or type(row.get("predicted_supported")) is not bool
        for row in rows
    ):
        raise ValueError("Grounding labels must be booleans.")

    tp_supported = sum(
        row["expected_supported"] and row["predicted_supported"]
        for row in rows
    )
    fp_supported = sum(
        not row["expected_supported"] and row["predicted_supported"]
        for row in rows
    )
    fn_supported = sum(
        row["expected_supported"] and not row["predicted_supported"]
        for row in rows
    )
    tn_supported = sum(
        not row["expected_supported"] and not row["predicted_supported"]
        for row in rows
    )

    total = len(rows)
    correct = tp_supported + tn_supported

    def ratio(numerator: int, denominator: int) -> float | None:
        if denominator == 0:
            return None
        return round(numerator / denominator, 4)

    support_precision = ratio(
        tp_supported, tp_supported + fp_supported
    )
    support_recall = ratio(
        tp_supported, tp_supported + fn_supported
    )

    unsupported_tp = tn_supported
    unsupported_fp = fn_supported
    unsupported_fn = fp_supported

    unsupported_precision = ratio(
        unsupported_tp, unsupported_tp + unsupported_fp
    )
    unsupported_recall = ratio(
        unsupported_tp, unsupported_tp + unsupported_fn
    )

    if (
        support_precision is None
        or support_recall is None
        or support_precision + support_recall == 0
    ):
        support_f1 = 0.0 if (
            support_precision == 0 or support_recall == 0
        ) else None
    else:
        support_f1 = round(
            2 * support_precision * support_recall
            / (support_precision + support_recall),
            4,
        )

    if (
        unsupported_precision is None
        or unsupported_recall is None
        or unsupported_precision + unsupported_recall == 0
    ):
        unsupported_f1 = 0.0 if (
            unsupported_precision == 0 or unsupported_recall == 0
        ) else None
    else:
        unsupported_f1 = round(
            2 * unsupported_precision * unsupported_recall
            / (unsupported_precision + unsupported_recall),
            4,
        )

    return {
        "total": total,
        "correct": correct,
        "accuracy": ratio(correct, total),
        "supported_claims": {
            "precision": support_precision,
            "recall": support_recall,
            "f1": support_f1,
        },
        "unsupported_claims": {
            "precision": unsupported_precision,
            "recall": unsupported_recall,
            "f1": unsupported_f1,
        },
        "confusion_matrix": {
            "true_supported": tp_supported,
            "false_supported": fp_supported,
            "missed_supported": fn_supported,
            "correctly_rejected_unsupported": tn_supported,
        },
    }
