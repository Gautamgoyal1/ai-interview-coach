# Restricted free-tier staging checklist

23 November 2026. **Not yet cleared for private tester access.** Local preparation
is complete; cloud security, configuration and live acceptance gates below remain
unverified. This is not public-production approval. No cloud resources, private-data
uploads, cloud writes, paid calls, deployments, Git commits or pushes were performed.

## Completed code tasks

- Exact backend tester-email allowlist enforced at registration, login and every
  authenticated request, including the direct Render hostname. Removing an email
  blocks its existing JWTs on subsequent API calls. CORS is not the access boundary.
- Closed registration by default. Operator enablement allows only exact invited
  addresses. There is no email-ownership verification: coordinate account creation
  with trusted testers and close registration promptly, so somebody else cannot
  claim a known invited address during onboarding.
- Independent AI/Speech kill switches, disabled in the prepared Render template.
  Saved work/authentication and owned End Interview actions remain available when
  AI is disabled. Provider construction for resume analysis is lazy, allowing boot
  without usable provider credentials. No automatic POST retries were added.
- Durable UTC-day endpoint reservations: defaults 30/tester/day and 100 globally;
  at most two concurrent AI endpoints. Reservations commit before endpoint work,
  survive Render restarts and count provider/endpoint failures. A failed user
  reservation rolls back the global increment. Ledger failure returns controlled
  503; exhaustion returns 429/Retry-After. Existing short-term IP/user limits remain.
- Additive migration `b8c9d0e1f2a3` adds only `staging_ai_usage`. Original development
  data/schema were not migrated. Grading, source knowledge and Voice lifecycle were
  not changed. Staging readiness also requires the ledger table.
- Production HTTPS CORS/headers, no-store API responses, non-root single-worker
  image, explicit proxy trust, bounded connection attempts and small pool. Restricted
  cloud staging requires **`sslmode=verify-full`**, not encryption-only `require`.
- Tested Supabase hardening SQL, read-only security/schema/knowledge checks, an
  offline frozen-cache exporter and guarded reviewed 30-record seed procedure.

Reservations count endpoints, not provider calls, tokens, dollars or audio minutes.
One answer can invoke several model operations. A resource-scoped browser Speech
token can be used outside this ledger until expiry. These controls reduce abuse;
they are **not a hard monetary ceiling**. Start with one supervised tester.

## Operator cloud-console steps (not executed)

### Supabase access boundary

- [ ] Separately approve a **new dedicated Free staging project**; import no private
  development users, resumes, answers or historical reports.
- [ ] **Disable the Data API**. PrepMate uses SQL and its own JWTs, not Supabase Auth
  or its browser SDK. Disable automatic exposure of new tables. Inspect REST,
  GraphQL, RPC, exposed schemas, views and security-definer functions. Keeping a
  publishable key out of the frontend is not a security control. If another product
  requires the API, use a separately reviewed schema/project for that product.
- [ ] Check actual PostgreSQL/pgvector versions, genuine provider CA and SQL
  endpoint. Use the session pooler if IPv4 requires it. Transaction-pooler prepared
  statement compatibility has not been certified. Enforce SSL in provider settings
  where available; use `verify-full` with the actual endpoint's CA/hostname.
- [ ] Migrate and initialize only reviewed knowledge, then harden as the actual
  migration owner, **before tester accounts/private data**. Commands below.
- [ ] Create a separate `prepmate_api` runtime login, no ownership/elevated attributes:

  ```sql
  CREATE ROLE prepmate_api LOGIN INHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
  GRANT prepmate_runtime TO prepmate_api;
  ```

  Set its password using interactive `psql` `\password prepmate_api`, not SQL history
  or command arguments. Use the provider's custom-user pooler username format.
  Keep migration credentials on the operator machine, never in the running API.
  For Supabase's `extensions` pgvector schema, set the login's search path to
  `pg_catalog, public, extensions` and verify it on an actual runtime connection:
  `ALTER ROLE prepmate_api SET search_path = pg_catalog, public, extensions;`.
  The hardening SQL grants extension-schema USAGE when vector is installed there.
- [ ] Run `python scripts/staging_preflight.py` from `backend` with the restricted
  production-mode **runtime** environment. Require `passed: true`. It is read-only;
  it cannot prove that the console's Data API switch is off.
  It also exercises the actual role/difficulty-filtered pgvector operator using
  stored vectors, without new embeddings or a claim of a fresh semantic evaluation.
- [ ] Make external read/write denial checks with no key, the publishable/anon key,
  and a synthetic Supabase authenticated identity if enabled. Include
  `/rest/v1/users?select=id&limit=1`, all resume/interview/report/practice tables and
  `staging_ai_usage`; check GraphQL/RPC routes too. Require denial/unavailability,
  **not `200 []`**. Use synthetic payloads, not private rows. A PrepMate JWT is not
  a Supabase identity. Never expose a service-role key to the browser.

Run hardening in one operator `psql` session, after reviewing the connection target:

```sh
psql 'service=prepmate_staging_migration' -X -v ON_ERROR_STOP=1 -c "SET prepmate.reviewed_dedicated_project = 'yes'" -f backend/scripts/sql/restrict_supabase.sql
```

The script atomically enables/forces RLS on 12 named tables; revokes PUBLIC, anon,
authenticated and service_role table, column and owned-sequence privileges; removes
public schema CREATE from those roles; and revokes future table/sequence grants for
the actual migration owner. Unknown policies/owners, unsafe existing runtime group
or unsafe global default grants cause an abort rather than silent broad changes.
Inspect the failure before retrying. Future migrations require the same review.

The only application policy permits the runtime group to access business rows.
**Per-user ownership is enforced by FastAPI**, not `auth.uid()` RLS, because PrepMate
JWTs and integer user IDs are independent of Supabase Auth. Runtime has business
CRUD, SELECT-only chunks/migration versions, and SELECT/INSERT/UPDATE-only quota
history. Never grant runtime ownership, BYPASSRLS or migration-owner membership.
The script does not globally rewrite RPC privileges: keep Data API disabled and
review routines. The preflight rejects unreviewed public functions/views and unsafe
default ACLs; pgvector's non-security-definer extension routines are recognized.

[Supabase API security](https://supabase.com/docs/guides/api/securing-your-api),
[SQL-created tables and RLS](https://supabase.com/docs/guides/database/postgres/row-level-security),
[TLS/poolers](https://supabase.com/docs/guides/database/connecting-to-postgres).

### Render, Pages and environment

- [ ] Approve the intended Git revision and resource/deployment actions separately.
  `render.yaml` uses Free, no paid disk, one worker and auto-deploy off.
- [ ] Set `APP_ENV=production`, `STAGING_ENABLED=true`,
  `STAGING_ALLOWED_EMAILS=["exact-tester@example.com"]`, registration/AI/Speech
  flags **false** initially. Sample addresses must be replaced, not copied literally.
- [ ] Set a fresh stable JWT secret >=32 bytes and retain the 15-minute token TTL.
  Password changes do not revoke already-issued JWTs; allowlist removal does block
  subsequent requests. Long interviews may require reauthentication; test recovery.
- [ ] Runtime SQL URL: `postgresql+psycopg://.../postgres?sslmode=verify-full&sslrootcert=/etc/secrets/supabase-ca.crt`.
  Put the genuine CA in that Render secret-file path. Confirm `pg_stat_ssl` on the
  actual runtime connection; wrong CA/hostname must fail. Do not print the URL.
- [ ] Pool 4+2, connect/pool timeout 10 seconds; `AI_GLOBAL_CONCURRENCY=2` maximum
  (use 1 for initial testing). Include operator/pooler clients in connection limits.
- [ ] Leave `FORWARDED_ALLOW_IPS` empty unless exact ingress addresses are verified.
  Never use `*`/all-address CIDRs. Prove spoofed headers cannot change rate-limit
  identity. Without proxy trust, testers may share an IP limit; user/day budgets
  and authentication are independent of forwarded IP headers.
- [ ] Set exact HTTPS `CORS_ORIGINS`, no preview wildcards/paths/trailing slashes.
  Test allowed/foreign OPTIONS, HTTP-to-HTTPS redirects, certificates, no mixed
  content, no-store headers and disabled production API docs. CORS is not auth.
- [ ] Pages: root `frontend`, `npm ci && npm run build`, output `dist`, Node 24.
  Set both `VITE_API_BASE_URL` and `VITE_API_URL` to the same HTTPS API origin.
  Vite variables are public: no provider/database/Supabase secrets. Confirm copied
  `_headers`, deep-link refresh, correct API target and secret-free downloaded JS.
  Without a top-level `404.html`, Pages supplies SPA fallback.
- [ ] The static shell can remain public while data/AI are restricted by the backend.
  If it must also be private, separately configure/test supported Pages access
  controls on canonical and preview hosts. Protecting Pages alone does not protect
  the public Render API URL.

### AI spending controls (manual)

- [ ] Use dedicated staging keys/projects, least privileges, low request/token quotas,
  actual available model names and usage alerts. Do not enable billing, upgrade
  plans or add a paid gateway. Leave a feature disabled if approved free allowances
  cannot support it. AI-enabled hosting is not automatically zero-cost.
- [ ] Gemini: verify free-tier availability of the configured models. On any already
  approved billable project, inspect project/service spend-cap availability and
  enforcement status. Current caps can have lag and billable overages; alerts-only
  budgets are not caps. A default billing-tier ceiling is not a safe testing budget.
- [ ] Azure: minimal TPM/RPM and Cost Management alerts. Inspect whether Foundry
  blocking cost controls actually cover this endpoint/resource; availability and
  preview restrictions matter. Plain Cost Management budgets only alert.
- [ ] Speech remains off until resource quotas/free allowances and human testing
  are approved. The kill switch blocks new tokens, not in-flight/previously
  authorized browser requests. Backend quotas do not bound Speech minutes.
- [ ] Review provider data-use terms and consent before submitting resumes; free and
  paid model terms can differ. Begin with synthetic users and resumes only.

[Gemini billing](https://ai.google.dev/gemini-api/docs/billing),
[cap limitations](https://docs.cloud.google.com/billing/docs/how-to/budgets-spend-caps),
[Azure controls vs alerts](https://learn.microsoft.com/en-us/azure/foundry/concepts/manage-costs),
[Azure throughput quotas](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/quota).

## Explicit migrations and reviewed seed

After Data API is disabled, run migrations explicitly with migration credentials,
not during web startup. Confirm single current/head `b8c9d0e1f2a3`, pgvector and
768-dimensional columns. Operator files/CA paths below are placeholders to configure:

```sh
docker compose build backend
docker run --rm --env-file .env.staging.migration --mount type=bind,source=<ABS_CA_PATH>,target=/etc/secrets/supabase-ca.crt,readonly ai-interview-coach-backend:latest alembic upgrade head
# Repeat using `alembic current` and `alembic heads`; compare IDs.
```

The tracked public `backend/deployment/software-engineer-reviewed.json` binds
exactly 30 Software Engineer records, ten each Easy/Medium/Hard, with
`gemini-embedding-001`/768 dimensions. It includes metadata/content/float32 hashes,
not vector arrays/candidates. SHA-256:
`f06730c33172381bf957aebe4d3876c3726c74b44cec70ff3aeef9615ecbaf11`.

Use the **Phase 7** reviewed update, not the older Phase 6B revision-2 cache:
the current sources/database legitimately differ from that historical input.
All ten current source-file byte hashes and the Phase 7 receipt's manifest/cache
hashes were checked. The original Phase 6B evidence remains unchanged.

Offline export from frozen local artifacts, from `backend` (already executed;
refuses overwriting evidence):

```sh
python scripts/export_staging_knowledge.py --source-manifest ../storage/phase7/source-manifest.json --vector-cache ../storage/phase7/vectors.json --output ../storage/security-audit/staging-prep/reviewed-knowledge-current.json
```

Bundle SHA-256: `2d7f102495236bc10897b32c57f2284397cf3a3d16a7cb174f29f48fd5c57c76`.
Missing original cache is a blocker, not permission for paid regeneration. The
private cache and generated bundle remain ignored. With the operator's staging
migration environment and read-only CA/bundle mounts, run from `backend`:

```sh
python scripts/initialize_staging_knowledge.py --bundle <REVIEWED_BUNDLE_PATH> --sha256 2d7f102495236bc10897b32c57f2284397cf3a3d16a7cb174f29f48fd5c57c76
# Only after separate cloud-write approval, repeat with --apply.
```

Preview is read-only. Apply revalidates scope/hashes, acquires the existing advisory
lock, inserts in one transaction and checks persisted content/float32 vectors.
No updates, deletes or provider calls. Exact existing 30 yield zero changes;
any other nonempty corpus aborts. It intentionally refuses the 61-row development
corpus. Do not copy the legacy 31, broaden to 156/183 rows, or import candidate data.
Other roles' RAG coverage is not certified by this initial seed. Then run hardening,
create the runtime login and pass read-only preflight. No cloud seed was executed.

## Backup, restore and rollback

Operator owns a daily local Task Scheduler/cron job; retain seven daily and four
weekly encrypted copies in separately approved storage. Restore before tester
access and monthly thereafter. Proposed RPO <=24h/RTO <=4h are rehearsal targets,
not guarantees: a sleeping operator machine misses backups. Free hosting disks are
not backups; no offsite/private-data upload was authorized here.

Use a matching/newer `pg_dump` major, a privileged backup connection, TLS/CA and
ACL-protected `PGSERVICEFILE`/`PGPASSFILE` outside Git. Record PostgreSQL/extension
version and schema, image revision, Alembic head, table/sequence digests and dump
SHA-256. Include quota history so recovery does not reset daily reservations.

```sh
pg_dump --dbname=service=prepmate_staging_backup --format=custom --schema=public --no-owner --no-acl --file=storage/backups/staging.dump
pg_restore --list storage/backups/staging.dump
age -p --output storage/backups/staging.dump.age storage/backups/staging.dump
```

`age` is an optional trusted operator tool, not an application dependency; enter
passphrases interactively. Protect recovery keys separately. Do not binary-redirect
dumps through PowerShell 5; use `--file`. Secure cleartext dump ACLs and review their
retention/removal after validation. Manually copy only encrypted backups offsite.

Restore to a **new disposable local database**, never an existing cloud/development
database. Recreate pgvector in its recorded schema and the NOLOGIN runtime policy
group first. Do not restore provider-managed schemas or copy owner passwords.

```sh
age --decrypt --output storage/backups/restore.dump storage/backups/staging.dump.age
pg_restore --list --file=storage/backups/restore-full.list storage/backups/restore.dump
python scripts/prepare_public_restore_list.py --input storage/backups/restore-full.list --output storage/backups/restore.list
pg_restore --dbname=service=prepmate_disposable_restore --use-list=storage/backups/restore.list --no-owner --no-acl --exit-on-error storage/backups/restore.dump
```

Do not use `--clean`. Verify all table digests, sequences, answer/evaluation/report
associations, float32 vectors and ledger values, then reapply hardening because
ACLs are omitted. Test synthetic app recovery on the restore. Supabase Auth/Storage
are outside this app-schema backup; adopting those services needs a new plan.

The fresh local target already has a `public` schema. The restore-list helper
comments exactly its SCHEMA creation entry, preserving every table, sequence,
policy and data entry; unexpected/duplicate entries cause an abort. It never
drops schemas or suppresses restore errors. Recreate pgvector and runtime policy
roles first as above; review the complete restore list before executing it.

For code rollback, disable new AI/Speech work, stop writes and select the previous
reviewed revision/image. Leave the additive ledger table; no automatic downgrade,
deletion or candidate-data restore. Data recovery requires separate target/recovery
point approval. [Supabase Free backup guidance](https://supabase.com/docs/guides/platform/backups).

## Live free-tier acceptance gates (not locally verified)

- [ ] Actual HTTPS/database TLS, Data API denials, runtime preflight, foreign CORS
  rejection and direct-Render uninvited/anonymous access rejection.
- [ ] Allow normal Render idle sleep (currently 15 minutes), then measure cold/warm
  requests separately. No keepalive scheme to evade free limits. `/health` is
  liveness; `/health/ready` is DB initialization, not provider/corpus certification.
- [ ] Confirm session restoration keeps valid tokens on 503/network failures and
  offers retry; expired JWTs require login. Never automatically repeat answer/start
  POSTs after timeout. Check persisted state before manual retry.
- [ ] One tester, then at most two: Technical/HR Text journeys, restart/refresh,
  answer/evaluation/report persistence, cross-user rejection, quota 429, kill switches.
  Measure actual Render RAM/CPU/timings. Local 512MiB/1-CPU tests do not certify the
  free shared CPU. Render can sleep/restart and has no persistent disk; Supabase
  Free may pause. Communicate supervised staging downtime explicitly.
- [ ] Separately enable approved live providers, then bounded real AI and physical
  microphone/speaker tests. Mocked Speech is not human microphone verification.
- [ ] Complete encrypted backup/disposable restore; verify free quotas/plan selections
  and backup owner. No paid fallback, automatic upgrade or unapproved deployment.

[Render Free](https://render.com/docs/free),
[Pages limits](https://developers.cloudflare.com/pages/platform/limits/),
[Pages SPA fallback](https://developers.cloudflare.com/pages/configuration/serving-pages/).

## Local verification record

| Check | Result |
|---|---|
| Complete backend suite | **523 passed**, no failures/errors/skips; fresh PostgreSQL/pgvector migrations, no paid HTTP |
| Complete frontend suite | **145 passed** across 14 files; existing cold-start/network session recovery regressions included |
| Operator tooling | **20 passed**, including narrow restore-list acceptance/refusal cases |
| TypeScript/Vite | Passed; existing ~770kB main JS chunk warning remains |
| Production image | Built; UID 10001; boots with no provider credentials and network disabled; docs closed, registration closed, uninvited login denied |
| Supabase-like SQL roles | API roles denied all 12 tables; runtime business persistence/ledger and scoped retrieval work; restricted writes denied |
| Reviewed knowledge | Current Phase 7 receipt/source/cache verified; existing 30 rows/content/float32 vectors match; scoped preview zero changes/embeddings |
| Original development data | All 11 original table digests match prior audit; 61 chunks; original Alembic version untouched |
| Backup/restore | Fresh synthetic-only PostgreSQL 16.15 custom dump restored; all 12 table/sequence/schema digests match; restored quota 3; rehardening denial passes |
| Python scans | Pinned Linux pip audit: zero known advisories; Bandit: zero High/Medium, 17 existing Low findings |
| npm production scan | Zero High/Critical; two existing Moderate React Router findings require review/acceptance before tester access; no major-version routing upgrade in this task |
| Secret preflight | Raw scanner reports 22 reviewed synthetic test/mock findings and exits nonzero; seven configured values checked, no configured-secret matches. Not a Git-history/PII certificate |
| Git | Whitespace check passed; no index mutation, commit, push or deployment |
| External AI usage | Zero calls/tokens/cost for this task; cached vectors only |

Private evidence: `storage/security-audit/staging-prep/`. Actual cloud Data API,
TLS/ingress/quotas, Render idle wake-up/performance and live AI/physical-microphone
acceptance are **NOT VERIFIED**. Encrypted offsite backup and operator RPO/RTO are
still action items; a successful local unencrypted synthetic restore is not those
checks. Restricted staging remains **NOT READY for tester access** until the cloud
and operator gates above pass. There is no public-production readiness claim.

## Safe Git plan (no staging/commit/push performed)

Current branch: `feature/phase5-saas-redesign`, target `origin` only after approval.
Preserve all existing dirty work. The private before-inventory is
`storage/security-audit/staging-prep/source-before.json`. Review its hashes to
separate this task from earlier changes, especially shared files.

Proposed logical commits after separate diff/approval review:

1. `fix: restrict private staging access and AI usage` — config/admission/auth,
   ledger/model/migration, lazy resume provider, readiness, Docker proxy command,
   focused tests and runner opt-in. Include earlier required security/header/body
   limit/DB helpers deliberately; a dirty shared file cannot be blindly called a
   staging-only diff.
2. `docs: prepare free-tier staging security and recovery` — Render/env examples,
   Supabase SQL, public reviewed manifest, seed/export/preflight scripts, their
   tests, deployment/audit/checklist docs, backup/restore helper and libpq ignore rules.

Prior UI/theme changes need a separate review. Exclude credentials, `.env*` except
templates, candidate data, dumps, cached vectors/private manifests, logs, scan
tools/evidence and dependencies. Before each approved commit inspect exact staged
diff, whitespace and staged-secret scan. Use ordinary non-force Git operations;
do not merge, deploy or push as a side effect of documenting this plan.
