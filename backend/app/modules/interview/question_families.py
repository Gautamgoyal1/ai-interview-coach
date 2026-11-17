"""Private session coverage markers, separate from solution choice and grading."""

from app.modules.interview.calibration import normalize_experience_level
import re


def covered_topic_key(topic: str) -> str | None:
    # Retrieval aliases are broader than pedagogical coverage. A SQL reservation
    # is not automatically a valid fallback for "Database Indexing".
    normalized = re.sub(r"[^a-z0-9]", "", topic.casefold())
    return {
        "datastructures": "data_structures",
        "algorithms": "algorithms",
        "objectorientedprogramming": "oop",
        "oop": "oop",
        "sql": "sql",
        "http": "http",
        "restapis": "rest_apis",
        "restapi": "rest_apis",
        "rest": "rest_apis",
        "git": "git",
        "testing": "testing",
        "debugging": "debugging",
        "securityfundamentals": "security",
    }.get(normalized)


ENTRY_FAMILY_IDS = {
    "data_structures": ["recency_eviction", "maximum_stack", "circular_resize"],
    "algorithms": ["peak_overlap", "covered_event_count", "earliest_free_slot"],
    "oop": ["validated_import", "staged_writer", "listener_snapshot"],
    "sql": ["independent_aggregates", "latest_eligible_identity", "owned_shared_union"],
    "http": ["idempotent_create", "versioned_retry"],
    "rest_apis": ["live_cursor", "field_patch_merge"],
    "git": ["dependent_revert", "merge_recovery"],
    "testing": ["stale_expiry", "out_of_order_response"],
    "debugging": ["cache_vs_shared_state", "listener_vs_upstream"],
    "security": ["authorization_transition", "authorization_transition"],
}
SENIOR_FAMILY_IDS = {
    "data_structures": ["durable_dedup", "inflight_cache_publication"],
    "algorithms": ["burst_range_index", "external_exact_topk"],
    "oop": ["bounded_reader_rollback", "plugin_cleanup"],
    "sql": ["reservation_outbox", "snapshot_aggregates"],
    "http": ["idempotent_create", "versioned_retry"],
    "rest_apis": ["snapshot_cursor", "sync_retention"],
    "git": ["migration_recovery", "security_revert_chain"],
    "testing": ["crash_outbox_oracle", "generation_swap_oracle"],
    "debugging": ["pool_lease_hypotheses", "cache_refresh_hypotheses"],
    "security": ["revoked_export_principal", "revoked_export_principal"],
}


def family_marker(topic_key: str, level: str, family: str) -> str:
    profile = normalize_experience_level(level)
    profile = "entry" if profile in {"internship", "fresher"} else profile
    return f"hard_family:{profile}:{topic_key}:{family}"


def family_ids(level: str):
    return (
        ENTRY_FAMILY_IDS
        if normalize_experience_level(level) in {"internship", "fresher"}
        else SENIOR_FAMILY_IDS
    )
