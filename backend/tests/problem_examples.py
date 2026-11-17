"""Small deterministic authoring fixtures, not paid evaluation examples."""

from app.modules.interview.problem_spec import ProblemSpecification


def sql_problem():
    return ProblemSpecification.model_validate(
        {
            "role": "Software Engineer",
            "experience_level": "experienced",
            "topic": "SQL",
            "requested_difficulty": "hard",
            "competency": "Stable row selection with missing parents",
            "scenario": "Return the latest eligible event per user.",
            "assumptions": ["Use PostgreSQL 16."],
            "constraints": ["Timestamps may tie.", "Do not drop users."],
            "observable_goal": "Emit exactly one row per user.",
            "edge_case": "Some users have only failed events.",
            "reasoning_decision": "How would you implement the query without duplicate winners?",
            "valid_alternative_approaches": [
                "LEFT JOIN LATERAL with ordered limit",
                "Window rank then outer join",
            ],
            "follow_up_direction": "Index choice and null timestamps",
            "technical_contract": {
                "kind": "sql",
                "tables": [
                    {"name": "users", "columns": ["id"], "primary_key": ["id"]},
                    {
                        "name": "events",
                        "columns": ["id", "user_id", "created_at", "status"],
                        "primary_key": ["id"],
                    },
                ],
                "row_identity": {"table": "users", "column": "id"},
                "references": [{"table": "events", "column": "user_id"}],
                "outputs": [
                    {
                        "name": "user_id",
                        "sources": [{"table": "users", "column": "id"}],
                        "meaning": "user ID",
                    },
                    {
                        "name": "event_id",
                        "sources": [{"table": "events", "column": "id"}],
                        "meaning": "selected event ID",
                    },
                ],
                "ranking": {
                    "order_by": [
                        {"table": "events", "column": "created_at"},
                        {"table": "events", "column": "id"},
                    ],
                    "selected_row_identity": {"table": "events", "column": "id"},
                    "output_name": "event_id",
                },
                "eligibility_and_time_scope": "Only successful events, all time; created_at is non-NULL.",
                "missing_rows_and_nulls": "Return NULL event_id for no eligible event.",
                "join_and_aggregation_rule": "Keep every user, including unmatched users.",
            },
        }
    )


def general_problem():
    p = sql_problem().model_dump()
    p.update(
        topic="Algorithms",
        experience_level="fresher",
        scenario="Find peak simultaneous meetings.",
        competency="Sweep events with tied endpoints",
        technical_contract={
            "kind": "general",
            "input_rules": "Unsorted half-open [start,end) intervals; start<=end.",
            "required_observation": "Count duplicate/nested meetings separately.",
            "boundary_rule": "Touching endpoints do not overlap; empty intervals count zero.",
        },
        observable_goal="Return the largest overlap count.",
        edge_case="Several starts and ends can have the same time.",
        constraints=["Input may contain duplicates.", "Do not expand each time unit."],
        assumptions=["Times are integers."],
        reasoning_decision="How would you order and process the events?",
        valid_alternative_approaches=[
            "Sorted event sweep",
            "Separately sorted starts and ends",
        ],
        follow_up_direction="Streaming input",
    )
    return ProblemSpecification.model_validate(p)
