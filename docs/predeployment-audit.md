# Final pre-deployment audit

Restricted-staging preparation addendum: see
[private-staging-checklist.md](private-staging-checklist.md). Local access/budget,
SQL isolation and initialization controls have been added; the original evidence
below is preserved. **Cloud-console and live deployment gates remain unverified.**

23 November 2026. **Verdict: NOT READY — BLOCKERS REMAIN.**

The locally tested application can complete synthetic Technical and HR interview
journeys with real PostgreSQL persistence. Confirmed workflow defects and a High
development-tool advisory were addressed. This does not clear a public launch:
cloud isolation, real provider/Voice acceptance, spending controls and a real
cloud backup procedure still require verification. No cloud resources were created.
No Git commit, push, merge or production deployment was performed.

## Scope and existing protections

Reviewed README/configuration, React routes and hooks, FastAPI routers/services,
SQLAlchemy ownership filters, migrations, LangGraph recovery, provider adapters,
resume parsing, Speech, report/practice persistence and container configuration.
Existing uncommitted security/theme work was preserved. Some protections below
were implemented in the earlier security checkpoint, not reimplemented here.

- HS256 JWT verification with required claims, startup secret checks, bcrypt and
  bounded passwords; protected routes resolve the authenticated database user.
- Parameterized ORM queries and owner-scoped resume/interview/report/practice
  retrieval. No confirmed SQL injection or cross-user content read in tested paths.
- Bounded pre-parser bodies/readers, PDF bytes/pages/text/decompression work and
  filename handling. Earlier shared AI quotas/concurrency admission remain intact.
- Speech authentication, private/no-store responses, supported voices, SSML
  escaping, token renewal/final-drain lifecycle and explicit transcript submission.
- Provider timeouts, bounded outputs/calls, structured validation, honest grading
  unavailability, preserved answers and generation-only retry/restart recovery.
- React text rendering and the reviewed application paths do not execute model
  output as code or SQL. Prompt-injection controls are not a guarantee of model
  judgment quality; no action-taking tool integration was introduced.

## Confirmed findings and local fixes

| Priority / severity | Finding | Resolution |
|---|---|---|
| P1 workflow | A slow older interview GET could replace a newer session or surface its obsolete error | Request identity/unmount guards; both regressions failed before the fix and pass afterward |
| P1 availability | Session restoration cleared tokens on any network/503 failure, forcing logout during cold starts | Only 401 clears credentials; protected workspace presents an accessible retry and verifies authentication before entry |
| P1 deployment | CORS allowed only localhost and could not be configured for a cloud frontend | Exact configurable origin list; production rejects wildcard/path/local/plain-HTTP frontend origins and requires a TLS PostgreSQL URL |
| P2 resource/privacy | Checkpoint cleanup omitted LangGraph blob storage; completed sessions retained transient checkpoints | Use public thread deletion, cover legacy stores, and release completed state after durable commit; no graph transitions or grading changes |
| P2 authorization | Practice could associate a foreign report ID and a mismatched interview track | Owner-filtered lookup and track validation before generation or persistence; foreign and missing IDs both return controlled 404 |
| High package advisory, development server | Vite 5.4.21 was affected by advisory ranges | Compatible supported Vite 6.4.6 update; existing React plugin retained; active local frontend also updated to patched Node 24 image |
| P2 deployment/resource | Fixed 20+30 database pool, floating image dependencies, root backend and weak readiness visibility | Configurable default 5+5 pool/timeouts, SQL parameter hiding, Linux dependency lock, non-root single worker, connection disposal and readiness endpoint |
| P2 hardening | Missing response/security policies and ambiguous production defaults | Private API caching/security headers, production docs disabled, startup error inputs hidden, Pages headers/CSP and deployment templates |
| Verification defect | Default test runner could select an older running Compose image | Added explicit `--image`; documented commands select the newly built image; PostgreSQL evaluation-persistence opt-in enabled |

None of these changes alters interview rubrics/weights, historical scores,
question-generation architecture, schemas, Azure credentials or avatar identity.
The photographic animation remains disabled. Hash checks preserved 71 avatar,
knowledge and grading source/assets exactly across this task.

## Regression and security results

| Check | Result |
|---|---|
| Complete maintained backend suite | **488 passed, zero failures/errors/skips**; fresh migrations and opt-in PostgreSQL/pgvector tests |
| Frontend suite | **145 passed, 14 files**, on native Node and again in Node 24 container |
| TypeScript / Vite production build | Passed natively and in Node 24; existing large-chunk warning remains |
| Tooling tests | **16 passed**; Windows temporary-directory ACL issue resolved using an owned workspace basetemp |
| Python compile / pip consistency | Passed; no separate configured Ruff/mypy gate found |
| Bandit | Zero High/Medium; 17 Low entries: legacy test assertions and XML escaping import, not an XML parser |
| Python advisories | Zero known matches among 77 Windows packages and 75 pinned Linux packages |
| npm advisory inventory | Before: 1 High + 3 Moderate; after: **0 High/Critical, 2 Moderate** |
| Secrets | No configured/provider-secret match; 21 password-literal findings manually triaged as synthetic auth fixtures |
| Whitespace | `git diff --check` passed |

Secret/advisory scans are heuristic snapshots, not certification. No OS/base-image
CVE scan, external penetration test or aggressive public traffic test was performed.
No test assertions were weakened and no failures were hidden by skips.

## Actual browser and persistence verification

The production frontend was served locally with its security policy, plus an
exact loopback HTTP API exception confined to the test server. It talked to an
actual non-root, single-worker FastAPI container and disposable PostgreSQL.
Model responses were deterministic fixtures; provider HTTP transports were blocked.
This was not live AI generation, grading or cloud TLS verification.

- Both Technical and HR: UI registration/login, dashboard, synthetic PDF upload
  and parsing, analysis, setup, five primary questions plus one follow-up, answer
  submission, completion, report generation, refresh and sign-out/sign-in passed.
- Both selected sessions have all six answers and all six evaluations stored
  against their turns, with the correct Technical/HR rubric. Reports persisted.
- One injected session-restoration 503 retained the token; Retry recovered.
- All 28 main-content layout/bounds cases passed across dashboard, analyzer,
  setup, history, report, practice hub and profile at 320/375/768/1440px.
- No uncaught page exceptions. Expected console HTTP entries were two initial
  report-not-found responses preceding generation and the injected 503. Two
  favicon requests were cancelled during navigation; no unexplained app crash.
- Earlier synthetic failures are retained as evidence: an intentionally unsuitable
  model draft produced a controlled 503 with **four answers/four evaluations
  already saved**; a rapid repeated-follow-up run correctly hit the request quota.
  Browser harness assumptions about the HR heading and sign-out destination were
  corrected; they were not product fixes.

The seven fresh Voice browser groups passed using a previously cached Azure MP3,
native HTMLAudio/Web Audio, synthetic microphone tracks and a mocked Azure
recognizer. Coverage includes playback, replay, pause/resume, mute, simulated
buffering, silence/disabled tracks, final-drain review, editing, single submission,
Text Mode, reduced motion, TTS failure and navigation cleanup. Permission-denial,
token-expiry and background lifecycle have deterministic regression coverage.
No physical microphone, acoustic synchronization or live Azure interview was tested.
The real Speech SDK against production CSP/HTTPS remains an external acceptance gate.

An actual disposable API restart preserved the complete synthetic data digest;
restart-to-ready measured **3.21 seconds**. A synthetic pg_dump was restored into
another disposable database and **all public-table contents matched**. The restore
contained 52 answered fixture turns, including preserved earlier cases.

Observed post-restart idle memory was **135.8 MiB with a 512 MiB limit**, one CPU.
That is not a peak/concurrency test or Render's throttled CPU allocation. The main
browser bundle is about **770 kB / 194 kB gzip**; route/SDK splitting is follow-up
work. Live AI latency and public-user capacity were not measured.

## Development data and environment safety

The original database was accessed read-only. All **11 public-table digests and
61 knowledge records** match the captured baseline. The baseline was captured
after the first Docker engine interruption/restoration; no migration or mutation
was run against that database. No historical evaluation or private user record
was edited. Backups/restores in this audit used synthetic data only.

A parallel Docker build suffered an engine interruption, stopping local services.
The existing PostgreSQL volume remained intact. Services were restored, builds
were verified sequentially, and the frontend was finally recreated alone to
replace its old dependency volume with patched Vite. PostgreSQL was not recreated.
All identified disposable audit containers/networks were removed. The local
backend/frontend/database services are running; the database is healthy.

Routine API testing used **zero paid provider requests, zero provider tokens and
USD $0 estimated usage**. Existing cached audio was reused. Provider credentials
were never displayed; live model access and actual billing were not verified.

## Remaining blockers and limitations

| Priority | Required before widening access |
|---|---|
| P0 conditional cloud exposure | Secure/disable Supabase Data API access to application tables before private data is loaded; backend authorization cannot protect that separate access path. No remote breach was observed or claimed. |
| P1 release control | Review/commit the intended local security and deployment fixes before deploying GitHub; the current remote avatar commit does not include these uncommitted changes. |
| P1 operating/cost gate | Configure provider quotas/budgets and access-controlled ingress for both frontend and API. Process-local counters reset on restart; Speech authorization can be used directly while valid. No durable monetary cap is implemented. |
| P1 live verification | Validate actual cloud TLS, CORS, trusted proxy identity, database pool/extension/migration setup, reviewed knowledge initialization, provider model access and complete real Technical/HR journeys. |
| P1 Voice acceptance | Perform human microphone permission, 60–90-second final-word capture, transcript editing, replay and single-submit checks on the actual HTTPS deployment. |
| P1 recovery gate | Establish encrypted offsite backups and a real cloud restore drill; the synthetic local restore is insufficient proof for private production data. |
| P2 package maintenance | Two Moderate React Router advisories remain. No SSR hydration or untrusted full navigation target was found in reviewed application paths; a reviewed Router 7 upgrade is still needed to clear the package findings. |
| P2 operational limits | One-worker/process-local coordination; abandoned active checkpoints; no long-session/concurrent-user stress test; browser-stored JWTs without refresh or immediate revocation; password changes do not invalidate issued tokens. |
| P3 performance | Large eagerly loaded browser bundle; broader route/SDK splitting and cosmetic polish deferred. |

React Router references: [open redirect](https://github.com/advisories/GHSA-wrjc-x8rr-h8h6),
[SSR hydration](https://github.com/advisories/GHSA-337j-9hxr-rhxg).

## Files and deployment prerequisites

Current-task changes are grouped below; earlier dirty security/theme files remain
preserved separately. The local evidence manifest lists every path and hash.

- Backend: `core/config.py`, new `core/response_headers.py`, `db/session.py`,
  `main.py`, interview `graph.py`/`service.py`, practice `service.py`.
- Packaging: both Dockerfiles, `requirements.txt`, new `requirements-linux.lock`,
  frontend `package.json`/lock, new `public/_headers`, root `.env.example`/`render.yaml`.
- Frontend recovery: `hooks/AuthContext.tsx`, `components/ProtectedRoute.tsx`,
  `features/interview/useInterview.ts`.
- Regressions/tooling: new backend deployment/checkpoint/ownership tests, new
  frontend session-recovery/load-race tests, `run_offline_tests.py` and the isolated
  runner's explicit-image option.
- Documentation: README, this report and [deployment runbook](deployment.md).

Follow the runbook for exact environment names, migration/health commands, Pages
build settings, Supabase isolation and knowledge-scope restrictions. The prepared
Render template creates no database or disk and disables automatic deployments.
Free-tier use is conditional; no zero-cost or public-production guarantee is made.

### Launch checklist

- [ ] Approve the intended Git revision and fresh images.
- [ ] Lock down cloud database/Data API privileges and verify unauthenticated denial.
- [ ] Configure secrets, HTTPS origins, TLS database URL, one worker and trusted ingress.
- [ ] Apply reviewed migrations and a separately reviewed knowledge-only scope.
- [ ] Configure hard service quotas/operational spending controls and private access.
- [ ] Verify actual Technical/HR and human Voice journeys after restart.
- [ ] Complete encrypted cloud backup/restore and capacity checks.
- [ ] Resolve or explicitly accept the remaining Moderate package findings.

Private evidence/screenshots/logs are under ignored
`storage/security-audit/final-readiness/`; do not commit those runtime artifacts.
