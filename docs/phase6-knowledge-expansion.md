# PrepMate Phase 6: taxonomy and knowledge foundation

Date: 15 November 2026. Status: code/source expansion implemented and tested offline; live ingestion remains approval-gated. No commit, push or merge.

## Stage A: baseline audit

Before modification, Resume Analyzer had four static role profiles and ten canonical skills. The exact roles were machine learning engineer, data scientist, ai engineer and python developer. The exact skills were machine learning, python, sql, numpy, pandas, scikit-learn, data preprocessing, model evaluation, docker and cloud platforms. Software Developer existed as an interview alias, not a resume default profile. PostgreSQL had saved free-text Software Developer/SDE analyses and Software Engineer practice sessions, but no role/skill master tables.

Live PostgreSQL contained 31 knowledge chunks, all role `ml_engineer`: Python 6, machine_learning 7, deep_learning 6, llm_rag 6, agentic_ai 6. Difficulty coverage was easy 2, medium 28, hard 1. Twelve chunks cited Claude-assisted study notes and nineteen cited Own study notes; all had `source_url=n/a`, `license=own work`. Existing Python/OOP/data-structure and ML content was retained rather than bulk-recreated.

The configured embedding model was `gemini-embedding-001`; all stored vectors and the SQLAlchemy column were 768-dimensional. Indexes were primary key, unique content_hash, role and topic B-tree indexes. No HNSW/IVFFlat vector index existed. No vector model, dimension, index or schema change is necessary for this initial corpus size.

The old ingestion script hashed role/topic/body and inserted unseen hashes. It had no managed identity, revision lifecycle, explicit preview gate or whole-input validation. The root script was not inside the backend bind mount, so a new backend module entrypoint makes the documented command executable without changing Compose mounts.

Interview retrieval passed neither role nor difficulty. On the original corpus an unfiltered Software Engineer search could only return ML-tagged material. Practice passed a display role such as Software Engineer to a database field storing IDs such as ml_engineer, and used display topics as exact database tags. Both gaps are covered by isolated regression tests before introducing targeted filtering.

## Stage B: taxonomy and rollout policy

The existing two JSON dictionary/list formats remain compatible. The versioned catalog adds stable role IDs, exact aliases, classifications, rationale and role-specific internship/fresher/intermediate/experienced expectations. Skill metadata adds stable IDs, related concepts and prerequisites. No new weights or numeric proficiency thresholds were introduced.

The existing four default denominators are unchanged. New required lists are minimal generic coverage profiles, not universal hiring standards. Recommended/advanced skills do not enter default matching scores. In particular, multiple programming languages are recommendations/alternatives rather than simultaneous mandatory requirements. Supply a job description when hiring for a specific stack. The catalog records role-specific depth expectations for review and curation. Existing runtime experience-calibration prompts remain authoritative; no new per-role scoring thresholds or adaptive difficulty distributions were introduced.

| Canonical role (ID) | Required default skills | Recommended | Advanced | Proposed new chunks |
| --- | --- | --- | --- | ---: |
| machine learning engineer (`ml_engineer`) | python, machine learning, numpy, pandas, scikit-learn, data preprocessing, model evaluation, docker, cloud platforms | testing, ci/cd, observability, sql | None | 9 |
| data scientist (`data_scientist`) | python, machine learning, numpy, pandas, scikit-learn, data preprocessing, model evaluation | statistics, sql, data visualization, experiment design | None | 6 |
| ai engineer (`ai_engineer`) | python, machine learning, docker, cloud platforms | rest apis, testing, observability | None | 6 |
| python developer (`python_developer`) | python, sql, docker | testing, debugging, git, object-oriented programming | None | 15 |
| software engineer (`software_engineer`) | data structures, algorithms, object-oriented programming, git, sql, testing, debugging | http, rest apis, security fundamentals, python, javascript, java | concurrency, system design | 30 |
| frontend developer (`frontend_developer`) | html, css, javascript, http, git, testing, accessibility | typescript, react, rest apis, debugging, data structures | web performance, security fundamentals, system design | 24 |
| backend developer (`backend_developer`) | sql, http, rest apis, git, testing, debugging, security fundamentals | python, java, javascript, postgresql, redis, docker, object-oriented programming | concurrency, system design, message queues | 24 |
| full stack developer (`full_stack_developer`) | html, css, javascript, http, rest apis, sql, git, testing | react, typescript, python, security fundamentals, accessibility, object-oriented programming | system design, web performance, concurrency | 24 |
| data analyst (`data_analyst`) | sql, statistics, data visualization, spreadsheets, data cleaning | python, pandas, business intelligence, etl | experiment design, model evaluation | 6 |
| devops engineer (`devops_engineer`) | linux, networking, git, ci/cd, docker, cloud platforms, observability | terraform, security fundamentals, python | kubernetes, site reliability, system design, cloud security | 9 |
| cybersecurity analyst (`cybersecurity_analyst`) | networking, linux, security fundamentals, incident response, log analysis | python, threat modeling, cloud platforms | digital forensics, cloud security, system design | 6 |
| qa engineer (`qa_engineer`) | testing, test design, git, debugging, http | test automation, sql, python, javascript | performance testing, security fundamentals, ci/cd | 24 |

The full aliases and level expectations are in `role_catalog.json`; all 54 canonical skills and their aliases are in `skills_taxonomy.json`. `skill_metadata.json` provides relationships without inferring that a candidate possesses prerequisite skills.

## Stages C and E: source expansion

The initial Software Engineer slice was verified before adding other role profiles and shared applicability. It adds ten source records: data structures, algorithms, object-oriented programming, SQL, HTTP, REST APIs, Git, testing, debugging and security fundamentals. Five later shared records cover accessibility, CI/CD, statistics, test automation and incident response. They include concept definitions, principles, practical uses, misconceptions, realistic scenarios, trade-offs, three difficulty examples, expected answer concepts, follow-ups and primary references.

Primary references were checked from Python documentation, PostgreSQL 16 documentation, RFC 9110, Git, pytest, OWASP, W3C/WAI, GitHub Actions, NIST and Playwright. The notes and interview scenarios are original, AI-assisted material; no proprietary question bank or copied documentation prose is imported. The source list and authorship/license boundary are recorded in `knowledge_base/sources.yaml` and README.

Shared source text compiles to explicitly scoped rows rather than being reauthored for each role. The proposed expansion is 183 managed rows: 61 easy, 61 medium, 61 hard, requiring 45 unique embedding inputs. The 31 legacy rows are unchanged. This gives structured coverage to 15 of the 54 canonical skills; it does not establish a complete curriculum for all ten role families.

Examples:

- HTTP medium: a timed-out order POST may already have committed. Expected concepts include unknown outcomes, application idempotency keys and reconciliation; a follow-up asks about reusing a key with a different payload.
- SQL medium: avoid selling the last inventory item twice. Expected concepts include an atomic conditional update, affected-row checks and transaction scope; the follow-up considers multi-item reservations.
- Accessibility medium: test a confirmation dialog using only a keyboard. Expected concepts include initial focus, Tab order, Escape and focus restoration.
- Statistics hard: analyze repeatedly monitored user-assigned experiments without treating a p-value as a posterior probability or claiming causality from mere association.

## Ingestion architecture and approval boundary

No database structure changed. Existing `chunks.source_name` carries stable managed identities; existing `content_hash` tracks source metadata/content plus model/dimension identity. Approved updates retain IDs; explicit retirement keeps source rows and historical citations but marks them unavailable to retrieval. Missing files/assignments are reported, never silently deleted. User analyses, interviews, turns, reports and practice records are not part of ingestion.

Metadata, identifiers, canonical skill references, per-role relevance, URLs, review dates, body sections, difficulty examples and exact duplicate records are validated before preview. Malformed input blocks the preview. PostgreSQL advisory locking prevents concurrent managed ingestion, and all embeddings must have the expected count, finite nonzero values and exact dimension before mutation. An error rolls the transaction back. Repeated unchanged ingestion performs no writes or embedding calls.

The default CLI is read-only. Apply requires `--apply --approve-plan <reviewed-token>`, and the token is recomputed against the current source/database plan. Model/dimension changes are refused pending a separately approved regeneration design. The actual vector column is verified before embeddings. No paid embedding operation or live ingestion was executed.

The preview and raw measured coverage are in ignored `storage/phase6/ingestion-preview.json` and `source-coverage.json`. The live corpus remains 31 rows. Test schemas were uniquely named and removed; no public user tables were modified.

## Retrieval and resume integration

Retrieval now resolves exact role aliases to stored IDs, maps display topics separately from resume aliases, filters difficulty, excludes retired rows and avoids inappropriate hard context for internship/fresher levels. HR continues to skip technical RAG. Unknown roles and empty eligible scopes safely return no context; eligible-row checks avoid paying for a query embedding when nothing can match. Existing curated/generative fallback behavior remains available.

The interview embedding query now includes experience, difficulty, question type and bounded recent question/answer context. The LangGraph transitions, question mix, adaptive rules, grader dimensions and Practice assistance rules are unchanged. Practice/report retrieval uses the same role normalization, while the generators continue to produce their own adaptive questions.

Resume role selection resolves exact aliases, including Software Developer/SWE/SDE. Unknown roles still need a JD. Expanded aliases use longest non-overlapping matches: React.js does not independently award JavaScript, and automated testing does not independently award its parent testing concept. No prerequisite or proficiency is inferred. Evidence classifications remain separate. The match formula is unchanged; unrelated newly detected resume skills do not alter the fixed required denominator. New JD terms can legitimately change future JD-specific denominators.

Scoring interpretation is versioned as 1.1 and the taxonomy as 2.0. Fingerprints include the taxonomy, role catalog and skill metadata; catalog edits change the digest without requiring a restart. New saved results record scoring/taxonomy version and digest internally without changing response schemas. Old saved JSON and historical scores are not rewritten or recalculated.

## Verification

Final results:

| Check | Measured result |
| --- | --- |
| Complete backend pytest suite | 291 passed, 2 opt-in PostgreSQL cases skipped; one pre-existing HTTP 422 constant deprecation warning |
| Opt-in PostgreSQL/pgvector tests | Both passed separately, using disposable schemas and fake embeddings |
| Frontend tests | 47 passed |
| TypeScript/Vite production build | Passed; existing large-bundle warning remains |
| Retrieval cases | 24/24 passed |
| Positive cases: hit at rank 1 | 21/21, using exact metadata scope and lexical test vectors |
| Safe abstention cases | 3/3; no query embedding requested for empty/ineligible scopes |
| Wrong-role/difficulty results | None observed in the 24 cases |
| Baseline control | 3/3 unfiltered results from a copy of the original corpus were ML-tagged for a Software Engineer query |
| Live knowledge after verification | 31 rows, unchanged; zero remaining test schemas |
| Live paid embeddings / Gemini semantic evaluation | Not run; explicit approval still required |

The initial 20 Software Engineer unit cases passed before other role expansion. Final coverage adds 32 unit tests plus two opt-in PostgreSQL integration tests. PostgreSQL tests cover repeated imports, changed content, stable row IDs, explicit non-destructive retirement, stale/missing approval, invalid embedding output and real cosine SQL filtering. Representative technical checks also execute order-preserving deduplication, tuple hashability and LEFT JOIN filter semantics rather than relying solely on prose checks.

Raw results: `storage/phase6/retrieval-evaluation.json`, `source-coverage.json`, and `ingestion-preview.json`. The final preview contains 183 inserts, 31 unchanged rows and 45 unique embedding inputs; there are no proposed legacy updates or retirements. Run a fresh preview before any eventual approval because its token is tied to the source/database state.

 The retrieval dataset contains 24 cases: 21 positive role/topic/difficulty cases and three safe-abstention cases. The PostgreSQL tests exercise the actual pgvector cosine operator using deterministic hashed lexical vectors. They validate metadata filtering, alias resolution, difficulty selection and ingestion lifecycle; they are not evidence of Gemini semantic-search quality or production generalization. A live semantic benchmark remains approval-gated.

Commands:

```sh
# Full suite; PostgreSQL tests are opt-in.
cd backend
python -m pytest -q

# Disposable PostgreSQL schemas and fake embeddings.
docker compose exec -T -e PREPMATE_KNOWLEDGE_POSTGRES=1 backend pytest -q -s tests/integration/test_phase6_knowledge.py

# Read-only live preview; no embeddings.
docker compose exec -T backend python -m app.modules.knowledge.ingest_cli
```

Windows verification used the existing `.venv`, a unique writable `storage/phase6/pytest-<uuid>` basetemp and `-p no:cacheprovider`, since the default temp/cache paths had permission restrictions. Docker containers exited during initial full-suite attempts; the suite was completed locally instead. The isolated PostgreSQL checks ran separately. These environment interruptions are not counted as passing test runs.

## Rollout and remaining gaps

1. Review and approve the Software Engineer/source preview before spending embedding quota. Check fresh Gemini semantic retrieval and generated questions after approved ingestion.
2. Frontend: deepen HTML/CSS/JavaScript/React and browser debugging; accessibility and shared HTTP/testing are initial coverage only.
3. Backend: deepen indexing, caching, concurrency and service boundaries beyond the shared SQL/HTTP material.
4. Full Stack: add end-to-end state/data consistency and integration scenarios after the two specialized tracks are reviewed.
5. Data Analyst: expand SQL analysis, cleaning, chart interpretation and spreadsheets; current statistics is a focused starting point.
6. Data Scientist: strengthen experimental design and inference alongside preserved ML notes.
7. AI/ML: review legacy provenance and evaluate deployment/serving/observability coverage; do not clone existing ML notes.
8. DevOps/Cloud: add Linux, networking, containers, cloud operations and infrastructure recovery; the initial release-pipeline record is not full coverage.
9. Cybersecurity: add log triage, threat modeling and cloud-access scenarios beyond incident response and authorization.
10. QA/Automation: deepen test-design techniques, performance and contract testing alongside the automation record.

The initial role profiles are usable, but the 39 skills without a new structured record remain a curation backlog (some appear in legacy notes). No claim is made that every skill now has equal depth. Exact alias matching remains conservative; no fuzzy job-title inference is added. Default matching measures documented canonical coverage, not job readiness or demonstrated expertise.

## Files

- Resume: existing roles/taxonomy/scoring/service/router/fingerprint modules; new `catalog.py`, `role_catalog.json`, `skill_metadata.json`.
- Knowledge: existing retriever; new `ingestion.py`, `ingest_cli.py`; compatibility wrapper `scripts/ingest_knowledge.py`.
- Interview: role fundamentals and retrieval inputs only (`question_bank.py`, `nodes.py`).
- Practice/reports: role-scoped retrieval calls only (`practice/generator.py`, `reports/service.py`).
- Sources: existing README/source index plus fifteen new Markdown records under the two new source directories.
- Verification: `test_phase6_taxonomy.py`, `test_phase6_knowledge.py`, `eval_data/phase6_retrieval.json` and this report.

No frontend source, database model, migration, Azure speech integration or grading weights changed.
