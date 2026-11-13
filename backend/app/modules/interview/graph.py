"""LangGraph StateGraph construction and checkpointing for interviews."""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from sqlalchemy.orm import Session

from app.integrations.llm.base import LLMProvider
from app.modules.interview.nodes import InterviewNodes
from app.modules.interview.state import InterviewState

# Shared in-memory checkpointer for active threads; DB graph_state provides
# durable recovery across backend restarts.
_SHARED_CHECKPOINTER = MemorySaver()


def clear_session_checkpoints(
    session_ids: list[str],
    checkpointer: MemorySaver | None = None,
) -> None:
    """Remove in-memory LangGraph checkpoints for deleted interview sessions."""
    cp = checkpointer or _SHARED_CHECKPOINTER
    storage = getattr(cp, "storage", None)
    writes = getattr(cp, "writes", None)
    for sid in session_ids:
        if isinstance(storage, dict):
            storage.pop(sid, None)
        if isinstance(writes, dict):
            stale_keys = [k for k in writes if isinstance(k, tuple) and k and k[0] == sid]
            for k in stale_keys:
                writes.pop(k, None)


def _route_after_decision(state: InterviewState) -> str:
    action = state.get("next_action", "complete")
    if action == "follow_up":
        return "generate_follow_up"
    if action == "next_question":
        return "advance_question"
    return "complete_interview"


def _route_after_advance(state: InterviewState) -> str:
    if state["question_index"] > state["max_questions"]:
        return "complete_interview"
    return "select_topic"


def build_interview_graph(
    db: Session | None = None,
    llm_provider: LLMProvider | None = None,
    checkpointer: MemorySaver | None = None,
):
    """Compile the LangGraph interview state machine with checkpointing."""
    nodes = InterviewNodes(db=db, llm_provider=llm_provider)

    builder = StateGraph(InterviewState)
    builder.add_node("load_candidate_context", nodes.load_candidate_context)
    builder.add_node("select_topic", nodes.select_topic)
    builder.add_node("retrieve_knowledge", nodes.retrieve_knowledge)
    builder.add_node("generate_question", nodes.generate_question)
    builder.add_node("wait_for_answer", nodes.wait_for_answer)
    builder.add_node("evaluate_answer", nodes.evaluate_answer)
    builder.add_node("decide_next_step", nodes.decide_next_step)
    builder.add_node("generate_follow_up", nodes.generate_follow_up)
    builder.add_node("advance_question", nodes.advance_question)
    builder.add_node("complete_interview", nodes.complete_interview)

    builder.add_edge(START, "load_candidate_context")
    builder.add_edge("load_candidate_context", "select_topic")
    builder.add_edge("select_topic", "retrieve_knowledge")
    builder.add_edge("retrieve_knowledge", "generate_question")
    builder.add_edge("generate_question", "wait_for_answer")
    builder.add_edge("wait_for_answer", "evaluate_answer")
    builder.add_edge("evaluate_answer", "decide_next_step")

    builder.add_conditional_edges(
        "decide_next_step",
        _route_after_decision,
        {
            "generate_follow_up": "generate_follow_up",
            "advance_question": "advance_question",
            "complete_interview": "complete_interview",
        },
    )

    builder.add_edge("generate_follow_up", "wait_for_answer")

    builder.add_conditional_edges(
        "advance_question",
        _route_after_advance,
        {
            "select_topic": "select_topic",
            "complete_interview": "complete_interview",
        },
    )

    builder.add_edge("complete_interview", END)

    return builder.compile(
        checkpointer=checkpointer or _SHARED_CHECKPOINTER,
    )
