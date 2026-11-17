"""Internal Hard problem contracts and their candidate-safe projection.

Validation checks structured relationships, not solution keywords. Prose can
still contain semantic errors; a bounded rubric screen remains necessary.
"""

import re
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.interview.calibration import ExperienceLevel


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


Text = Annotated[str, Field(min_length=3, max_length=240)]
Identifier = Annotated[str, Field(pattern=r"^[A-Za-z_][A-Za-z_0-9]*$")]


class ColumnRef(ContractModel):
    table: Identifier
    column: Identifier

    def key(self) -> str:
        return f"{self.table}.{self.column}"


class TableDefinition(ContractModel):
    name: Identifier
    columns: list[Identifier] = Field(min_length=1, max_length=9)
    primary_key: list[Identifier] = Field(min_length=1, max_length=2)

    @model_validator(mode="after")
    def keys_exist(self):
        if len(set(self.columns)) != len(self.columns) or not set(
            self.primary_key
        ) <= set(self.columns):
            raise ValueError("SQL table keys must be defined, unique columns")
        return self


class QueryOutput(ContractModel):
    name: Identifier
    sources: list[ColumnRef] = Field(min_length=1)
    meaning: Text


class Ranking(ContractModel):
    order_by: list[ColumnRef] = Field(min_length=1, max_length=3)
    selected_row_identity: ColumnRef
    output_name: Identifier


class SQLContract(ContractModel):
    kind: Literal["sql"]
    tables: list[TableDefinition] = Field(min_length=1, max_length=4)
    row_identity: ColumnRef
    references: list[ColumnRef] = Field(min_length=1)
    outputs: list[QueryOutput] = Field(min_length=1, max_length=4)
    ranking: Ranking | None = None
    # Required, candidate-visible: no implicit time/missing/empty semantics.
    eligibility_and_time_scope: Text
    missing_rows_and_nulls: Text
    join_and_aggregation_rule: Text

    @model_validator(mode="after")
    def coherent_relations(self):
        tables = {t.name: t for t in self.tables}
        if len(tables) != len(self.tables) or len(
            {o.name for o in self.outputs}
        ) != len(self.outputs):
            raise ValueError("SQL tables and output names must be unique")
        refs = (
            self.references
            + [self.row_identity]
            + [r for o in self.outputs for r in o.sources]
        )
        if self.ranking:
            refs += self.ranking.order_by + [self.ranking.selected_row_identity]
        for ref in refs:
            if ref.table not in tables or ref.column not in tables[ref.table].columns:
                raise ValueError(f"Undefined SQL reference: {ref.key()}")
        grain = self.row_identity
        if tables[grain.table].primary_key != [grain.column]:
            raise ValueError(
                "SQL result row identity must be a defined unique parent key"
            )
        if not any(grain.key() in {r.key() for r in o.sources} for o in self.outputs):
            raise ValueError("SQL output must include its declared result row identity")
        if self.ranking:
            rank = self.ranking
            identity = rank.selected_row_identity
            table = tables[identity.table]
            if table.primary_key != [identity.column]:
                raise ValueError("Ranked identity must be the defined unique row key")
            if identity.key() not in {r.key() for r in rank.order_by}:
                raise ValueError(
                    "Tie-break ordering must include the selected unique key"
                )
            output = next((o for o in self.outputs if o.name == rank.output_name), None)
            if output is None or identity.key() not in {
                r.key() for r in output.sources
            }:
                raise ValueError(
                    "Tie-breaking must affect a returned selected-row identity, not just its tied date"
                )
        return self


class OOPContract(ContractModel):
    kind: Literal["oop"]
    interface_guarantee: Text
    caller_workflow: Text
    failure_observation: Text
    capability: Literal["achievable", "capability_split_required"]
    unavailable_capability: Text | None = None
    # At least two caller steps: not just spotting an incompatible implementation.
    caller_steps: list[Text] = Field(min_length=2, max_length=4)

    @model_validator(mode="after")
    def capability_boundary(self):
        if (
            self.capability == "capability_split_required"
            and not self.unavailable_capability
        ):
            raise ValueError("An impossible capability must be explicitly identified")
        if self.capability == "achievable" and self.unavailable_capability:
            raise ValueError(
                "Cannot promise an achievable contract while declaring its capability unavailable"
            )
        return self


class PermissionState(ContractModel):
    principal: Identifier
    resource: Identifier
    action: Literal["read", "write", "download", "execute"]
    before: Literal["allowed", "denied"]
    after: Literal["allowed", "denied"]
    transition: Text


class SecurityContract(ContractModel):
    kind: Literal["security"]
    tested_permission: PermissionState
    enforcement_boundary: Text
    freshness_rule: Text

    @model_validator(mode="after")
    def meaningful_revocation(self):
        permission = self.tested_permission
        if permission.before != "allowed" or permission.after != "denied":
            raise ValueError(
                "Revocation must remove a permission the same principal previously possessed"
            )
        return self


class HTTPContract(ContractModel):
    kind: Literal["http"]
    mutation: Text
    side_effects: list[Text] = Field(min_length=1, max_length=2)
    retry_identity: Text
    identity_scope: Text
    same_key_different_body: Text
    concurrent_or_lost_response_outcome: Text
    guarantee_boundary: Text


class SecurityBoundaryContract(ContractModel):
    """Security tasks other than revocation must not fabricate a revoked grant."""

    kind: Literal["security_boundary"]
    assets: Text
    untrusted_inputs: Text
    safety_invariant: Text
    allowed_behavior: Text
    failure_case: Text


class Hypothesis(ContractModel):
    cause: Text
    predicted_observation: Text


class DebuggingContract(ContractModel):
    kind: Literal["debugging"]
    hypotheses: list[Hypothesis] = Field(min_length=2, max_length=2)
    controlled_experiment: Text
    shared_causes_policy: Text

    @model_validator(mode="after")
    def discriminating_predictions(self):
        causes = {h.cause.casefold() for h in self.hypotheses}
        predictions = {h.predicted_observation.casefold() for h in self.hypotheses}
        if len(causes) != 2 or len(predictions) != 2:
            raise ValueError(
                "Debugging requires different causes and discriminating observations"
            )
        return self


class GeneralContract(ContractModel):
    kind: Literal["general"]
    input_rules: Text
    required_observation: Text
    boundary_rule: Text


TechnicalContract = Annotated[
    SQLContract
    | OOPContract
    | SecurityContract
    | SecurityBoundaryContract
    | HTTPContract
    | DebuggingContract
    | GeneralContract,
    Field(discriminator="kind"),
]


def materialize_problem(
    data: dict, role: str, topic: str, level: str
) -> "ProblemSpecification":
    """Build the full internal spec without asking the provider to repeat facts.

    The model authors each technical fact once. Derived indexes are internal;
    the compiler projects the same facts, without a second paraphrasing call.
    Full specifications remain accepted for deterministic fixtures/replay.
    """
    value = {
        "role": role,
        "topic": topic,
        "experience_level": level,
        "requested_difficulty": "hard",
        **data,
    }
    c = value["technical_contract"]
    kind = c["kind"]
    if kind == "sql":
        assumption, constraints, goal, edge = (
            c["eligibility_and_time_scope"],
            [c["missing_rows_and_nulls"], c["join_and_aggregation_rule"]],
            c["join_and_aggregation_rule"],
            c["missing_rows_and_nulls"],
        )
    elif kind == "oop":
        assumption, constraints, goal, edge = (
            c["interface_guarantee"],
            [c["caller_workflow"], c["failure_observation"]],
            c["interface_guarantee"],
            c["failure_observation"],
        )
    elif kind == "security":
        assumption, constraints, goal, edge = (
            c["enforcement_boundary"],
            [c["freshness_rule"], c["tested_permission"]["transition"]],
            c["freshness_rule"],
            c["tested_permission"]["transition"],
        )
    elif kind == "security_boundary":
        assumption, constraints, goal, edge = (
            c["assets"],
            [c["untrusted_inputs"], c["allowed_behavior"]],
            c["safety_invariant"],
            c["failure_case"],
        )
    elif kind == "http":
        assumption, constraints, goal, edge = (
            c["guarantee_boundary"],
            [c["identity_scope"], c["same_key_different_body"]],
            c["concurrent_or_lost_response_outcome"],
            c["concurrent_or_lost_response_outcome"],
        )
    elif kind == "debugging":
        assumption, constraints, goal, edge = (
            c["shared_causes_policy"],
            [c["controlled_experiment"], c["shared_causes_policy"]],
            "Distinguish the causes with a bounded experiment.",
            c["shared_causes_policy"],
        )
    else:
        assumption, constraints, goal, edge = (
            c["input_rules"],
            [c["input_rules"], c["boundary_rule"]],
            c["required_observation"],
            c["boundary_rule"],
        )
    defaults = dict(
        assumptions=[assumption],
        constraints=constraints,
        observable_goal=goal,
        edge_case=edge,
    )
    for key, default in defaults.items():
        value.setdefault(key, default)
    return ProblemSpecification.model_validate(value)


class ProblemSpecification(ContractModel):
    role: str = Field(min_length=2, max_length=100)
    experience_level: ExperienceLevel
    topic: str = Field(min_length=2, max_length=100)
    requested_difficulty: Literal["hard"]
    competency: Text
    scenario: Text
    assumptions: list[Text] = Field(min_length=1, max_length=2)
    constraints: list[Text] = Field(min_length=2, max_length=3)
    observable_goal: Text
    edge_case: Text
    reasoning_decision: Text
    valid_alternative_approaches: list[Text] = Field(min_length=2, max_length=3)
    follow_up_direction: Text
    technical_contract: TechnicalContract

    @model_validator(mode="after")
    def references_in_prose(self):
        if isinstance(self.technical_contract, SQLContract):
            allowed = {
                f"{t.name}.{c}"
                for t in self.technical_contract.tables
                for c in t.columns
            }
            known_tables = {t.name for t in self.technical_contract.tables}
            # All qualified identifiers must resolve; no preferred SQL strategy.
            prose = " ".join(
                [
                    self.scenario,
                    *self.assumptions,
                    *self.constraints,
                    self.observable_goal,
                    self.edge_case,
                    self.reasoning_decision,
                ]
            )
            for table, column in re.findall(
                r"\b([A-Za-z_]\w*)\.([A-Za-z_]\w*)\b", prose
            ):
                explicitly_marked = f"`{table}.{column}`" in prose
                if (
                    table in known_tables or explicitly_marked
                ) and f"{table}.{column}" not in allowed:
                    raise ValueError(
                        f"Undefined SQL reference in question: {table}.{column}"
                    )
        if len({a.casefold() for a in self.valid_alternative_approaches}) < 2:
            raise ValueError("Preserve at least two distinct valid approaches")
        return self


def contract_kind(topic: str) -> str:
    from app.modules.knowledge.retriever import retrieval_topics

    topics = set(retrieval_topics(topic))
    for key, kind in (
        ("sql", "sql"),
        ("object_oriented_programming", "oop"),
        ("security_fundamentals", "security"),
        ("http", "http"),
        ("debugging", "debugging"),
    ):
        if key in topics:
            return kind
    return "general"


def question_character_limit(topic: str) -> int:
    # Schema declarations are part of a SQL question's correctness contract.
    # Allow their explicit names without forcing a second phrasing call or
    # removing NULL/time/tie semantics to meet an arbitrary prose-only ceiling.
    return 1200 if contract_kind(topic) == "sql" else 900


def render_question(spec: ProblemSpecification) -> str:
    """Project ONLY candidate-safe fields; solutions and follow-ups stay private.

    Essential topic contracts are included verbatim. Generation must keep prose
    short enough for 900 characters, or 1200 when explicit SQL schema is needed.
    """
    contract = spec.technical_contract
    parts = [spec.scenario]
    if isinstance(contract, SQLContract):
        tables = "; ".join(
            f"{t.name}({', '.join(t.columns)}; PK {','.join(t.primary_key)})"
            for t in contract.tables
        )

        parts += [
            f"Tables: {tables}.",
            f"One result row per {contract.row_identity.key()}.",
            "Return: "
            + "; ".join(f"{o.name}: {o.meaning}" for o in contract.outputs)
            + ".",
            contract.eligibility_and_time_scope,
            contract.missing_rows_and_nulls,
            contract.join_and_aggregation_rule,
        ]
        if contract.ranking:
            parts.append(
                "Choose the latest by "
                + ", ".join(r.key() for r in contract.ranking.order_by)
                + " descending; return "
                + contract.ranking.output_name
                + "."
            )
    elif isinstance(contract, OOPContract):
        parts += [
            contract.interface_guarantee,
            contract.caller_workflow,
            contract.failure_observation,
        ]
        if contract.unavailable_capability:
            parts.append("Unavailable capability: " + contract.unavailable_capability)
    elif isinstance(contract, SecurityContract):
        p = contract.tested_permission
        parts += [
            f"{p.principal} can {p.action} {p.resource} before this change: {p.transition} Afterward that action must be denied.",
            contract.enforcement_boundary,
            contract.freshness_rule,
        ]
    elif isinstance(contract, SecurityBoundaryContract):
        parts += [
            contract.assets,
            contract.untrusted_inputs,
            contract.safety_invariant,
            contract.allowed_behavior,
            contract.failure_case,
        ]
    elif isinstance(contract, HTTPContract):
        parts += [
            contract.mutation,
            "Effects: "
            + "; ".join(p.rstrip(". ") for p in contract.side_effects)
            + ".",
            contract.retry_identity,
            contract.identity_scope,
            contract.same_key_different_body,
            contract.concurrent_or_lost_response_outcome,
            contract.guarantee_boundary,
        ]
    elif isinstance(contract, DebuggingContract):
        parts += [
            "Compare: " + " versus ".join(h.cause for h in contract.hypotheses) + ".",
            contract.controlled_experiment,
            contract.shared_causes_policy,
        ]
    else:
        parts += [
            contract.input_rules,
            contract.required_observation,
            contract.boundary_rule,
        ]
    parts += [
        *spec.assumptions,
        *spec.constraints,
        spec.observable_goal,
        spec.edge_case,
        spec.reasoning_decision,
    ]
    # Repetition is removed only for exact same facts, never by shortening away a constraint.
    unique = list(dict.fromkeys(p.strip() for p in parts if p.strip()))

    # Lossless compaction: drop only a verbatim fact already contained in another
    # visible fact. No semantic similarity or preferred-solution keyword filter.
    def normalized(value):
        return value.rstrip(".?! ").casefold()

    retained = [
        p
        for p in unique
        if not any(
            normalized(p) != normalized(other) and normalized(p) in normalized(other)
            for other in unique
        )
        # This is a derived internal index, not an additional candidate fact.
        and not (
            isinstance(contract, DebuggingContract)
            and p == "Distinguish the causes with a bounded experiment."
        )
    ]

    # One setting, one coherent contract, one ask. The same text is safe for
    # text display and plain-text TTS; no SSML or playback changes are involved.
    def sentence(p):
        return p if p.endswith((".", "?", "!")) else p + "."

    body = " ".join(
        sentence(p)
        for p in retained
        if p not in {spec.scenario, spec.reasoning_decision}
    )
    return "\n\n".join(
        p for p in [sentence(spec.scenario), body, spec.reasoning_decision] if p
    )


def validate_problem(
    spec: ProblemSpecification, role: str, topic: str, level: str
) -> str:
    if (spec.role, spec.topic, spec.experience_level) != (role, topic, level):
        raise ValueError(
            "Problem identity must match the selected role, topic and experience"
        )
    expected = contract_kind(topic)
    allowed = (
        {expected, "security_boundary"}
        if expected == "security"
        else {expected, "general"} if expected == "debugging" else {expected}
    )
    if spec.technical_contract.kind not in allowed:
        raise ValueError("Topic requires its corresponding technical contract")
    question = render_question(spec)
    limit = question_character_limit(topic)
    if len(question) > limit:
        raise ValueError(
            f"Rendered question has {len(question)} characters; shorten duplicate prose, keep essential contract facts (maximum {limit})"
        )
    return question
