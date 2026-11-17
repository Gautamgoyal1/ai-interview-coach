# Architecture

PrepMate is a React/TypeScript/Vite frontend and a FastAPI modular-monolith backend
with PostgreSQL 16 and pgvector. See the [README](../README.md) for setup and status.

## Runtime boundaries

The browser calls authenticated REST endpoints for resume analyses, interviews,
reports and practice. Authentication uses JWT bearer tokens. Resume processing
combines PDF extraction, predefined role/skill metadata, evidence classification
and model feedback; saved analyses seed interview/practice context.

LangGraph controls the interview loop: select topic/difficulty, retrieve knowledge,
generate a primary question, wait for the answer, evaluate, decide follow-up/advance,
and complete. Technical and HR generation/evaluation have separate paths. Grading
dimensions are model-assisted; overall scoring/report calculations are backend
logic. Missing grading stays unavailable rather than becoming a zero or invented
score.

Generation uses the selected Azure OpenAI or Gemini provider. Retrieval embeddings
use Gemini independently, with a 768-dimensional pgvector column. Queries scope
knowledge by role, topic, difficulty and experience; HR skips technical RAG.
Knowledge is ingested explicitly from versioned Markdown with source identities,
provenance, preview tokens, transactional updates and duplicate prevention.

## Persistence and recovery

SQLAlchemy models/Alembic migrations cover users, resumes/analyses, interview
sessions/turns/reports and practice sessions/questions/attempts. LangGraph's active
checkpointer is in memory. Persisted session state supports recovery of saved
progress; it is not a distributed checkpoint service.

An answer's available evaluation is persisted against its turn before subsequent
generation can overwrite transient state. Generation failure after saving an
answer exposes a pending state and explicit retry, without resubmitting/regrading
the same answer. Unsubmitted browser drafts and active audio are temporary.

## Speech

Azure subscription credentials stay on the backend. The browser receives a
short-lived STT token and uses Microsoft's Speech SDK. Backend TTS returns audio;
the browser owns playback cancellation/replay and microphone coordination. Voice
submission requires final transcript review/edit followed by explicit submission.

Real prerecorded Azure/browser checks are documented; physical microphone and
human listening acceptance remain outstanding. Speech and generation are separate
integrations, and Text Mode remains available without Speech credentials.

## Development constraints

Run one serving backend worker: interview locks, speech rate limits and caches
are process-local. The supplied images run development reload servers. CORS is
limited to the two localhost Vite origins. Tracing/background-task/strict-camera
files include scaffolding, not an implemented distributed worker or proctoring
service. No production infrastructure profile is claimed.
