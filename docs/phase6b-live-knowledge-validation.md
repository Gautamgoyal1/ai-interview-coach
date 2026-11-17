# PrepMate Phase 6B: controlled Software Engineer validation

> Subsequent execution: the single approved Approval A run is complete. See [actual semantic results](phase6b-semantic-evaluation-results.md). The embedding command below is an historical preparation record and must not be rerun under the consumed approval. Approval B remains unauthorized.

Date: 15 November 2026. Decision: **HOLD live ingestion. Ready to review an isolated semantic-evaluation request; neither evaluation spend nor rollout has been approved.**

No paid embedding or generation call, live knowledge write, schema change, score change, user-data operation, commit, push or merge was performed. Backend application code and taxonomy were left unchanged. The subsequent content-readiness pass corrected the reviewed source notes; see [final input review](phase6b-evaluation-readiness.md). The existing PostgreSQL container was started to permit the read-only snapshot; the backend/voice application was not used for testing.

## 1. Fresh state and ingestion preview

The runtime catalog validates at 12 canonical roles and 54 skills. The configured embedding path is the **Gemini Developer API**, `gemini-embedding-001`, 768 dimensions; Azure Speech is not the embedding provider. Key presence was checked without printing credentials. Account tier/quota was not queried.

The database was inspected in an explicitly read-only, repeatable-read transaction. All 31 rows are legacy `ml_engineer` knowledge. Row identifiers, metadata, text, hashes and vector values were snapshotted. Their digest matched before and after the preview. No ingestion was applied.

| Preview scope | Inserts | Updates | Retirements | New unique embedding inputs | Expected total after approval |
| --- | ---: | ---: | ---: | ---: | ---: |
| Entire knowledge base | 183 | 0 | 0 | 45 | 214 |
| `software_engineering/` folder | 156 | 0 | 0 | 30 | 187 |
| **Actual `software_engineer` role only** | **30** | **0** | **0** | **30** | **61** |

The folder scope is NOT a Software Engineer-only rollout: its records are assigned to other roles too. The recommended initial scope filters compiled items by the canonical role while preserving the original source metadata and hashes. Do not make a staging copy that rewrites the `roles` front matter: that changes hashes and causes avoidable updates on a later full rollout.

The full preview reports 31 unchanged selected legacy sources. The role-only preview reports zero unchanged selected sources because it selects only the 30 new items; the 31 pre-existing rows remain outside its mutation scope and are retained. There are no orphaned managed identities in the fresh database.

Review artifacts (local, ignored by Git):

- [Full preview](../storage/phase6b/preview-all.json)
- [Folder preview](../storage/phase6b/preview-software-folder.json)
- [Recommended role-only preview](../storage/phase6b/preview-software-only.json)
- [Frozen 30-row manifest](../storage/phase6b/software-manifest.json)
- [Read-only summary](../storage/phase6b/review-summary.json)
- [Legacy knowledge snapshot](../storage/phase6b/legacy-snapshot.json) — knowledge text/vectors only; no resume, interview or authentication data.

The frozen role-only approval token is `5b7b004975edfd5ae85ef47943e725bf4b5e252bc7c26735a46395efd2d84070`. This is a plan identifier, **not authorization**. Refresh it after any correction or database/source change.

## 2. Software Engineer content quality review

All ten source records and all 30 easy/medium/hard examples were inspected against their primary references. The core explanations are technically sound. The four wording/assumption clarifications below have now been applied at source revision 2, with regenerated previews and hashes.

| Record | Easy review | Medium review | Hard review / clarification |
| --- | --- | --- | --- |
| Data Structures | Membership, expected hash lookup and ordering are distinguished correctly. | First-occurrence deduplication includes identity, ordering, space and edge cases. | Correctly asks about durable/bounded state, replay windows and guarantees after expiry. |
| Algorithms | Sorted input, comparison consistency and progress are appropriate foundations. | Two-element non-progress and duplicate handling are realistic debugging tasks. | **Corrected:** the prompt specifies a balanced binary search tree and asks for balance/worst-case assumptions. Expected concepts explain linear degradation without balance. |
| OOP | **Corrected:** shared versus instance state may be explained using the preferred language or a language-neutral example; Python lookup rules are not universal. | Provider interfaces, composition, error translation and fakes fit intermediate application reasoning. | **Corrected:** the base contract explicitly promises same-key/same-amount deduplication across timeouts and outcome lookup. An incapable adapter must be rejected or expose a weaker workflow. |
| SQL | Join preservation/null/filter behavior is correct. **Corrected** the follow-up string literal: `WHERE orders.status = 'paid'`. | Atomic conditional updates and affected-row checks correctly address overselling at the described boundary. | Locks, lock ordering, serialization retries and non-retryable external effects are appropriately advanced. |
| HTTP | Correctly separates idempotent intended effects from identical responses or log side effects. | Timeout uncertainty, idempotency keys and outcome lookup are appropriate. | Cross-system partial failure/reconciliation is genuinely advanced; no exactly-once guarantee is invented. |
| REST APIs | Resources, GET, errors and access checks are appropriate. | Validators and conditional updates address lost writes. | Pagination consistency and compatibility trade-offs are advanced. The note correctly avoids claiming that JSON/noun URLs prove full REST compliance. |
| Git | Revert/shared ancestry explanation is correct. | Conflict intent, dependent changes and forward fixes are realistic. | Merge mainline interpretation and application/data compatibility are advanced; code reversal is correctly distinguished from operational recovery. |
| Testing | Fixture isolation and teardown are appropriate. | Controlled clocks/dependencies and mock-contract drift are practical. | Multi-service failure injection and idempotency assertions are appropriate, with limits of tests acknowledged. |
| Debugging | Reproduction facts and sensitive-data minimization are appropriate. | Controlled concurrency/state leakage is a meaningful debugging scenario. | Production traces, hypotheses and safe mitigation are advanced; root cause is not inferred from correlation alone. |
| Security Fundamentals | Authentication and resource authorization are correctly distinguished. | Two-user read/mutation tests are appropriate. | Background principals, sharing revocation and caching require advanced policy reasoning. |

Supporting primary references include [Python data structures](https://docs.python.org/3/tutorial/datastructures.html), [binary-search implementation notes](https://docs.python.org/3/library/bisect.html), [classes](https://docs.python.org/3/tutorial/classes.html), [PostgreSQL isolation](https://www.postgresql.org/docs/16/transaction-iso.html), [join/filter semantics](https://www.postgresql.org/docs/16/queries-table-expressions.html), [index types](https://www.postgresql.org/docs/16/indexes-types.html), [HTTP semantics](https://www.rfc-editor.org/rfc/rfc9110.html), [Git revert](https://git-scm.com/docs/git-revert), [pytest fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html), [Python debugging](https://docs.python.org/3/library/pdb.html) and [OWASP authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html).

Additional review observations:

- SQL provenance now maps joins, isolation, conditional updates, aggregates, index predicates and string literals to relevant PostgreSQL 16 documentation; the supporting-reference registry matches.
- New notes explicitly distinguish their own CC-BY-4.0 material from linked documentation. No proprietary question bank or imported third-party prose was found. This inspection is not an independent legal provenance audit.
- The compiler validates IDs, exact duplicate bodies, aliases, assigned-role relevance, metadata and section completeness. Shared content across role rows is intentional; semantic near-duplicates are not automatically prevented. HTTP and REST have related but distinct intended scopes.
- Every difficulty chunk shares the definition/scenario/trade-off sections. Consequently an easy SQL or HTTP chunk still contains advanced operational context. The question examples are calibrated, but **generated-question difficulty still needs an approved end-to-end check**; field equality alone does not prove appropriate cognitive demand.
- The irrelevant repeated Python/OOP sentence was removed from all ten Software Engineer notes. Each affected record is revision 2. The embedding recipe is unchanged; all affected compiled hashes were refreshed.

This is an agent technical review, not independent subject-matter-expert sign-off. Expected concepts are reference directions, not exhaustive rubrics or mandatory phrasing. Existing interview grading rules have not changed.

## 3. Semantic evaluation registered before provider calls

New dataset: [32 realistic cases](../eval_data/phase6b_software_semantic.json), version 1.0. There are 30 positives (three per topic, one per difficulty) plus explicit unknown-role and out-of-scope-topic policy cases. Queries cover conceptual reasoning, debugging, transaction races, API design, algorithmic trade-offs and operational recovery. They include paraphrases and assumptions beyond verbatim reference questions. They are author-curated fixtures, not an independent human holdout.

Frozen dataset SHA-256: `6f4f43b0734bafb783209c1735e046c3c4a7293f0e3160ed0a22cc7fe473d424`.

Use three comparisons in an isolated copy:

1. **Historical unfiltered baseline:** the 31 original knowledge documents, without role/topic/difficulty gates. This measures the cross-role failure the expansion is intended to address.
2. **Current runtime with the live corpus:** current role/topic/difficulty policy over the same 31 rows. Every Software Engineer positive has zero eligible live candidates; safe empty context is expected.
3. **Expanded isolated corpus:** original 31 plus only the 30 Software Engineer candidates. The primary semantic arm applies role and difficulty but **omits the topic SQL predicate** and embeds the raw query without its gold topic label. Each positive must rank ten eligible topics. The exact-topic runtime arm is a separate functional check, normally with one candidate; it cannot establish semantic-search quality.

Legacy role tags are not a semantic relevance judgment. The dataset separately grades the legacy text (including useful Python data-structure/OOP notes) and binds those grades to the snapshot digest. Five queries have substantial available legacy support under the frozen judgments. Baseline graded nDCG is reported only when some relevant legacy content exists; an empty ideal set is not misreported as bad ranking. Independent human confirmation of these annotations is required before paid evaluation. The lexical surrogate retrieved substantial legacy support in zero of those five cases; this is not a measured Gemini baseline.

The original rows do not persist embedding-model provenance. Their dimensions alone do not prove model compatibility. For a fair before/after comparison, the recommended paid evaluation regenerates the 31 baseline document embeddings **only in the isolated cache**, with the same model/task/dimensions used for the 30 new documents. It does not regenerate or overwrite the live legacy vectors. The historical subtopic prefix is retained in baseline embedding inputs. Reusing stored legacy vectors is a cheaper diagnostic alternative but must be labelled model-provenance-unverified.

Gold relevance is fixed before evaluation: primary family = 3, listed related family = 1, irrelevant = 0, within the eligible role/difficulty scope. Reviewers must also check whether returned text supports the required concepts; topic labels alone do not prove usefulness. Harder/easier variants are not used to fill a strict-level candidate shortage. No similarity threshold will be tuned on this set.

| Gate | Required result |
| --- | --- |
| Primary hit@1 | At least 23/30 (76.7%) |
| Primary hit@3 | At least 27/30 (90%) |
| Mean reciprocal rank | At least 0.85 |
| Graded nDCG@3 | At least 0.80 |
| Per-topic primary hit@3 | At least 2 of 3 cases for each of ten topics |
| Runtime role/difficulty violations | Zero |
| Explicit policy negatives | Both abstain, with no query embedding request needed |
| Human support check | No unsupported critical technical conclusion; review all misses and the ten hard results |

Do not interpret raw nearest-neighbor ranking as an out-of-domain detector: the current retriever has no learned semantic abstention threshold. Negative cases here exercise explicit role/topic policy. No result on this set independently establishes generalization to all interview queries.

### What was actually run

An in-memory isolated lexical-surrogate diagnostic was run against copies, with **no provider or database calls**. Current production metadata functions determine eligibility; expected labels do not determine whether a case abstains. The scorer/preparation suite has nine focused tests for metric arithmetic, gold-independent policy behavior, malformed cached vectors and exact role-only source selection.

| Measurement | Offline result |
| --- | --- |
| Primary hit@1 | 19/30 (63.3%) |
| Primary hit@3 | 23/30 (76.7%) |
| MRR | 0.7220 |
| nDCG@3 | 0.6960 |
| Policy abstentions | 2/2 |
| Eligible candidates per semantic positive | 10 |
| Eligible current-live Software Engineer candidates | 0 for all 30 positives |
| Scorer/preparation tests | 9 passed |
| Real Gemini semantic evaluation | NOT RUN |

The surrogate misses the registered numeric gates. This demonstrates why the prior 24/24 narrowly filtered cases were insufficient evidence for semantic rollout; it does **not** predict the result of Gemini embeddings. The gates were not weakened after seeing these scores. [Raw diagnostic](../storage/phase6b/surrogate-diagnostic.json).

## 4. Expected embedding usage and cost

Pricing checked 15 November 2026: [Google's standard rate](https://ai.google.dev/gemini-api/docs/pricing#gemini-embedding) is **USD 0.15 per million input tokens** for `gemini-embedding-001`. Free-tier eligibility is unverified. The synchronous `batchEmbedContents` implementation is not the discounted asynchronous Batch API. Azure embedding/STT/TTS requests in this plan: zero.

| Operation | Inputs | Measured text | Heuristic tokens (characters / 4) | Estimated standard charge |
| --- | ---: | ---: | ---: | ---: |
| Software-only rollout, if re-embedded | 30 documents | 61,230 characters | 15,308 | $0.00230 |
| Full 183-row rollout, not recommended yet | 45 unique documents | 91,700 characters | 22,925 | $0.00344 |
| Fair isolated semantic evaluation | 61 documents + 30 queries | 114,289 characters | 28,572 | $0.00429 |
| Evaluation plus software rollout without cache reuse | 121 total inputs | Sum of the relevant rows above | About 43,880 | $0.00658 |

These are estimates, not provider token counts or a bill. The fair evaluation is three HTTP batch calls under the current 50-input batching, with no automatic retry. Reserve **$0.05 for one approved evaluation/rollout attempt**, excluding generation, infrastructure, taxes and any separately approved retry. Actual usage must be recorded. The model's [input limit is 2,048 tokens](https://ai.google.dev/gemini-api/docs/models/gemini-embedding-001); verify token fit after approval and do not silently truncate a frozen input. The largest new input is 2,687 UTF-8 bytes; the largest baseline input is 4,464 bytes, which is not a token count.

The prepared apply command reuses evaluated document vectors, so a successful evaluation need not pay to embed the same 30 Software Engineer texts again. That cache reuse is explicit; the ordinary ingestion CLI would embed pending texts again. [Measured cost inputs](../storage/phase6b/cost-estimate.json).

## 5. Exact changes requiring separate approvals

**Approval A — isolated paid evaluation:** freeze/review the 61 document and 30 query inputs, authorize one Gemini run, save vectors with task/model/dimension and source/dataset digests. No database writes are needed. Input request SHA-256: `2808da2d365ad56b943629b1777c9c82b07cb55c77665506050f25b25e77f79b`.

**Approval B — live rollout, only after the real semantic and manual gates pass:** insert the 30 named `software_engineer` records (ten easy, ten medium, ten hard). Preserve all 31 existing rows, including identifiers, text, metadata and vector values. No updates, retirement, reindex, model change, schema migration, historical rescoring, resume/interview/practice write or Azure operation is included.

**Approval C — recovery, only if needed:** retire only the 30 exact receipt rows. Preserve their text/vectors/IDs and the legacy 31 rows. Restoring their original role is a separately approved operation; do not rely on an unchanged-content apply plan to reactivate a row whose role alone was set to `retired`.

The broader 156-row folder and 183-row full plans are outside Approval B. A source correction, changed input manifest, failed run or changed database plan requires fresh review and tokens.

## 6. Safe rollout and verification

[Exact commands and guarded recovery procedure](phase6b-rollout-commands.md) are prepared. Paid/live command files are local ignored review artifacts; their syntax and no-approval exit guards were checked, but their approved paths have **not** been executed or live-tested.

Before approval: review the corrected revision-2 notes and refreshed source manifest, previews and costs. The requested editorial changes are complete. Confirm model/account availability and token fit without substituting a different embedding model.

After Approval A: generate the isolated cache, score against the registered criteria, review support and difficulty, and retain raw misses. Passing numeric gates alone does not authorize rollout. Any generation smoke check would require its own provider budget; it is not hidden in the embedding estimate.

After Approval B: acquire the ingestion advisory lock, verify the legacy snapshot, verify the exact 30-insert preview and cache digests, insert in one transaction, verify legacy integrity again, then commit and write a receipt. Confirm total rows = 61, new active Software Engineer rows = 30, and ten of each difficulty. A repeated scoped preview must show no changes and no embedding inputs. Exercise only read-only retrieval with approved cached vectors first; do not create real user interviews or call Azure Voice to validate ingestion.

If verification fails before commit, roll back the transaction. If a committed rollout must be disabled, use receipt-scoped retirement after Approval C; never truncate `chunks`, delete the legacy rows or retire all `prepmate:` rows. Restore from the receipt only after diagnosing the failure and obtaining separate approval. No migration or destructive database rollback is needed.

Phase 6B added the review/report, 32-case dataset, read-only snapshot helper, offline scorer and preparation tests. The content-readiness pass revised ten source notes and SQL attribution only; application code and taxonomy remain unchanged. See the final readiness report for current regression results. No frontend changes were made in this pass.
