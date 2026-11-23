# PrepMate backend security audit

18 November 2026. Local code review and bounded security regression checkpoint.
No production deployment, Git commit/push, cloud configuration change, database
migration, or application-data modification was performed. Existing frontend
work is preserved; all 96 frontend source hashes match the audit-start snapshot.

## Existing protections inspected

- JWT signatures use a pinned HS256 algorithm, required subject/issue/expiry/type
  claims, access-token type checking and a database lookup for the authenticated
  user. Startup rejects missing, short and known placeholder signing secrets.
- Passwords use bcrypt, with the 72-byte UTF-8 limit checked. Login errors are
  generic. An existing failed-login IP throttle was present, but bypassable as
  described below.
- SQLAlchemy expressions bind request values. The reviewed web paths do not build
  SQL from request strings. Raw SQL in the knowledge ingestion CLI is separate
  from public HTTP routes. Bounded SQL-injection login probes return 401.
- Resume, interview, report, practice-session, question, hint, reference and
  attempt access generally check ownership. Cross-user access tests return 404.
  There is a lower-severity foreign-key association gap noted below.
- Existing upload checks include MIME, PDF signature, 10 MiB file size,
  filename sanitization and rejection of encrypted or unreadable PDFs. Uploaded
  documents are parsed, not executed; filenames are not used as storage paths.
- CORS uses explicit local frontend origins. Public auth responses exclude
  password hashes. Provider credentials remain in backend configuration.
- Speech already has authenticated token/TTS routes, per-user request limits,
  a voice allowlist, XML text/attribute escaping, controlled Azure errors and
  private/no-store responses. The XML utility is used for escaping, not parsing.

## Confirmed findings and fixes

Severity is contextual to exposing this development API to untrusted clients.
Package-advisory severity is distinguished from a proven exploitable web path.

| Finding | Severity | Evidence and local fix |
|---|---|---|
| Unrestricted paid AI work and registration abuse | High | Public registration and authenticated resume, interview, practice and report mutations lacked shared quotas. Added atomic per-user, client-IP and process-wide rolling quotas, plus concurrency admission, across all 12 paid endpoint/method combinations, including existing Speech endpoints. Registration is bounded before hashing or persistence. Gemini output is capped at 4,000 tokens, matching the existing Azure output bound. |
| Login throttle reset bypass | High | Successful authentication cleared the IP failure counter, so an attacker could interleave guesses against a victim with logins to an owned account. Added independent incoming-attempt limits keyed by account digest, client IP and process. Success cannot erase these counters. Added password-change throttling and cleanup of expired legacy IP entries. |
| Upload limits applied too late; parser resource exhaustion | High availability risk | The endpoint's file-size check ran after multipart processing and temporary-file allocation. PDF extraction also ran synchronously in the async route, without application page/text bounds. Added a pre-parser body guard, reader concurrency/time limits, bounded PDF decoding/page/text work, fail-closed parsing, thread offload, and reuse of extracted text instead of parsing twice. |
| Public development ports and weak database-password fallback | High if default Compose ports are reachable | Compose published PostgreSQL, API and frontend on every host interface and provided a known database-password fallback. Published ports now bind to loopback and a nonempty database password is required. The backend image defaults to one worker without development reload. No running containers or existing database passwords were changed. |
| Advisory-affected installed packages | Critical/High-rated dependency advisories among other findings; web reachability varies | The initial inventory produced 91 advisory entries across five packages, including duplicates. Upgraded pypdf, Pillow, certifi, OpenTelemetry API and pip. Added security floors for runtime packages and the image's pip bootstrap. The updated 77-package inventory has no known advisory matches. A critical Pillow decoder advisory is not evidence that PrepMate exposes that decoder through its current PDF text-only path. |

These resource-control findings align with [OWASP API4 unrestricted resource
consumption](https://api-security.owasp.org/editions/2023/en/0xa4-unrestricted-resource-consumption/).
Upstream evidence reviewed includes the [pypdf malformed-xref advisory](https://github.com/py-pdf/pypdf/security/advisories/GHSA-5849-834g-hvw5),
the [critical Pillow decoder advisory](https://github.com/python-pillow/Pillow/security/advisories/GHSA-5x8w-8jj5-q52h),
the [certifi trust-store advisory](https://github.com/certifi/python-certifi/security/advisories/GHSA-6q48-6c7w-9gw2),
and [pypdf's resource-limit guidance](https://pypdf.readthedocs.io/en/stable/user/security.html).
No SQL injection, authentication-token forgery, cross-user content disclosure,
or exposed real secret was confirmed in the inspected/tested paths.

## Implemented admission policy

Limits are deliberately local and process-wide, not a distributed billing system.
The limiter ignores user-supplied forwarded-IP headers; deployment proxy trust
must still be configured correctly.

| Operation | Limits |
|---|---|
| Login attempts | 5/account/minute; 20/IP/minute; 200/process/minute |
| Registration attempts | 5/IP/hour; 50/process/hour |
| Password changes | 5/authenticated user/minute |
| Shared AI endpoint requests | 12/user/minute and 200/day; 30/IP/minute and 500/day; 60/process/minute and 2,000/day |
| Concurrent AI requests | 2/user; 4/IP; 8/process |
| Incoming POST/PUT/PATCH bodies | 11 MiB including form overhead; 8 simultaneous readers, at most 2/IP; 60-second read deadline |
| Resume PDFs | Existing 10 MiB file cap; 30 pages; 100,000 extracted characters; 2 MiB decoded-stream limits and additional bounded decoding/tree/form work |
| Generation output | Gemini 4,000 tokens; existing Azure cap remains 4,000 |

All applicable quota checks are consumed atomically under a lock. Storage is
bounded and stale buckets are pruned. Rejections include controlled 429 responses
with Retry-After. AI permits are released after failures; body-reader permits are
released before slow downstream work. Oversized or incomplete bodies are rejected
before multipart parsing; accepted request bytes are replayed unchanged.

The preexisting Speech limits remain in place beneath shared admission. Requests
that hit cached results also count toward admission. Quotas may need tuning for
real user traffic, particularly shared office IPs. No grading, question-selection,
LangGraph, schema or historical-score changes were made.

## Verification

- **Focused security/auth/upload tests: 67 passed.**
- **Full backend suite: 463 passed, 10 skipped, one existing Starlette deprecation
  warning.** Skips are opt-in PostgreSQL/pgvector cases. The suite uses disposable
  SQLite databases, dummy provider credentials and a test-only external-socket
  guard. No live user database or paid provider call is involved.
- New regressions cover concurrent atomic admission, quota expiry/key bounds,
  account/IP switching, permit cleanup, body-size enforcement with missing or
  false Content-Length, timeout/busy handling, valid-body replay, login-reset
  bypass, registration limits, shared endpoint quotas, anonymous rejection,
  dependency coverage for all paid routes, SQL injection payloads, malformed PDFs,
  page/text/decompression limits and bounded Gemini output in JSON/text modes.
- Existing Technical/HR flow, ownership, persistence, report, practice, recovery
  and Speech tests pass. Parser success fixtures now use real PDFs. An older
  deduplication test now uses a scripted provider and verifies that a repeated
  draft is rejected and retried, instead of depending on a real cloud provider.
- The first full run hit Windows temp-directory permissions and fixture issues.
  Those logs are preserved. The final run uses a unique workspace temp directory.
- **Bandit: zero High/Medium findings; 17 Low findings triaged.** Sixteen are test
  assertions in legacy test modules under app; one flags the XML escaping import.
  The raw scan exits nonzero for these Low findings; it was not relabeled as clean.
- **pip-audit/OSV: no known vulnerabilities in the updated 77-package inventory.**
  Before/after outputs are preserved. This is advisory matching, not exploitability
  proof or a guarantee against undisclosed vulnerabilities.
- **pip check, Python compilation, Compose configuration validation and Git
  whitespace checks pass.** Compose validation used the installed Compose binary
  with a task-local empty Docker config; no Docker daemon action was needed.
- **Redacted secret scan: no matches in 1,336 text objects**, including reachable
  historical blobs and current backend source. It checks provider/private-key
  patterns and exact configured private values. Matching values are never printed.
  This heuristic scan excludes binary and over-2-MiB objects and is not a guarantee
  against unknown or revoked secret formats.

Patched local versions tested: pypdf **7.1.0**, Pillow **13.0.0**, certifi
**2026.10.23**, opentelemetry-api **1.45.2**, pip **26.3**. Runtime requirement floors
permit patched compatible releases; a complete hashed dependency lock is not
introduced by this checkpoint.

## Remaining findings and limits

1. **Process-local quota persistence/distribution:** limits reset on restart and
   are not shared across replicas. The default is explicitly one worker. A shared
   store and durable usage accounting are needed before scaling or relying on
   daily quotas as financial protection.
2. **Provider-side spend and concurrency controls:** application request counts
   are not a dollar spending guarantee. In particular, short-lived browser Speech
   tokens authorize the resource directly during their validity; API issuance
   throttling cannot meter all direct SDK use. Configure provider quotas/budgets
   before public rollout. No production/cloud settings were changed.
3. **Medium: practice report-reference ownership.** A caller can store a
   source_report_id association without an independent owner check. Current
   practice code does not read or modify the referenced foreign report's content;
   this is an integrity/validation gap, not a confirmed foreign-report disclosure.
   This lower-severity issue remains outside the high-severity checkpoint.
4. **Medium: immediate JWT revocation is absent.** Previously issued tokens can
   remain valid until their short expiry after password changes. Token versioning
   or revocation is a separate authentication change.
5. PDF parsing has finite library/input limits and thread offload, but is not an
   OS process sandbox with a hard CPU deadline. Container CPU/memory/file-system
   isolation remains appropriate defense in depth.
6. No PostgreSQL-specific integration run, container build/image/OS/interpreter
   vulnerability scan, production penetration test, distributed load test or live
   AI/Speech acceptance test was performed. No aggressive external traffic was sent.
7. Running Docker images and published bindings were not rebuilt/recreated. The
   local environment was updated, but containers must be rebuilt/recreated before
   relying on package and Compose hardening. No volumes were deleted or passwords
   rotated. Public production readiness is not claimed.

## Files modified

- `backend/app/core/rate_limit.py`, new `backend/app/core/body_limit.py`
- `backend/app/api/dependencies.py`, `backend/app/main.py`
- `backend/app/modules/{auth,interview,practice,reports,resume,speech}/router.py`
- `backend/app/modules/resume/parser.py`
- `backend/app/integrations/llm/gemini.py`
- `backend/requirements.txt`, `backend/Dockerfile`, `docker-compose.yml`
- `backend/tests/conftest.py`
- New `backend/tests/unit/test_http_resource_limits.py`
- New `backend/tests/unit/test_gemini_output_limit.py`
- New `backend/tests/integration/test_security_admission.py`
- `backend/tests/unit/test_parser.py`, `backend/tests/unit/test_adaptive_interview.py`
- `backend/tests/integration/test_resume_router.py`, `test_user_isolation.py`,
  `test_phase395_history_and_deletion.py`
- `.gitignore` excludes the private tools, disposable databases and scan output
- This report

The exact manifest and machine-readable verification receipt are in ignored
`storage/security-audit/changed-files.json` and `storage/security-audit/verification.json`.
That directory also preserves original source hashes, scan outputs, package
inventories and test logs. No Git index changes, commits, pushes or deployments
were made.
