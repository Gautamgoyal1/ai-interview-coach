# PrepMate deployment runbook

Reviewed 23 November 2026. Prepared configuration is not deployment approval.
Do not launch until the audit's external verification gates are complete.

For the restricted free-tier pilot, follow the stricter
[private staging checklist](private-staging-checklist.md). It adds exact tester
access, closed registration, AI/Speech kill switches, durable daily quotas,
database `verify-full`, Supabase SQL controls and reviewed knowledge-only tooling.
Its requirements supersede the general examples below for restricted staging.

## Hosting and free-tier feasibility

Use Cloudflare Pages for `frontend/dist`, a single Render Docker web service for
FastAPI, and a separately provisioned Supabase PostgreSQL/pgvector database.
PrepMate uses its own JWT authentication, not Supabase Auth or its browser SDK.

- Pages: root `frontend`, build `npm ci && npm run build`, output `dist`,
  `NODE_VERSION=24`. Set **both** `VITE_API_BASE_URL` and `VITE_API_URL` to the same
  HTTPS API origin before building. All Vite values are public; never add keys.
- Render: the prepared `render.yaml` declares a Free Docker API with auto-deploy
  disabled and **no database or paid disk**. `backend/Dockerfile` runs as UID
  10001, honors `PORT`, and starts one worker without reload. Do not use Vite's
  development or preview server as the production frontend.
- Supabase: use a TLS SQL connection. Choose its session pooler if the direct
  endpoint's IPv6 requirements conflict with the host. Do not assume transaction
  pooling supports psycopg prepared statements without extra configuration/testing.
  [Connection modes](https://supabase.com/docs/guides/database/connecting-to-postgres).

This can support a small private beta after validation; it is not an availability
guarantee. Render Free sleeps after 15 idle minutes and lacks persistent disks;
its free PostgreSQL expires after 30 days. Supabase Free has a 500 MB database
allowance, may pause after inactivity, and lacks included automatic backups.
Pages Free has build/asset limits (currently 500 builds/month and 25 MiB per asset).
AI generation, embeddings and Speech remain metered. Do not promise zero-rupee
operation. Recheck these terms before launch.
[Render limitations](https://render.com/docs/free),
[Supabase pricing](https://supabase.com/pricing),
[Supabase pausing](https://supabase.com/docs/guides/platform/free-project-pausing),
[Pages limits](https://developers.cloudflare.com/pages/platform/limits/).

## Mandatory Supabase access boundary

**Secure or disable the Data API before loading private data.** Backend owner
filters do not protect a second REST/GraphQL access path. Alembic creates ordinary
`public` tables; existing Supabase default grants can expose SQL-created tables
without RLS. PrepMate JWTs do not automatically become Supabase Auth identities.

For this backend-only use, disable the Data API using the provider's supported
setting, or remove the application's schema from exposed schemas and configure
restrictive grants/RLS. Audit table, sequence, view and default privileges for the
actual migration owner. Verify unauthenticated Data API requests cannot read or
write users, analyses, interviews, turns, reports, practice or usage records.
Use separate least-privilege runtime and migration database roles. No cloud
privileges or policies were modified by this audit.
[Supabase API security](https://supabase.com/docs/guides/api/securing-your-api),
[RLS and SQL-created tables](https://supabase.com/docs/guides/database/postgres/row-level-security).

## Environment and runtime

| Setting | Requirement |
|---|---|
| `APP_ENV` | `production`; enables validation/headers and disables public API docs |
| `CORS_ORIGINS` | JSON list of exact public HTTPS origins, e.g. `["https://prepmate.pages.dev"]`; no slash/path/wildcards |
| `DATABASE_URL` | `postgresql+psycopg://.../postgres?sslmode=require`; prefer `verify-full` with the provider CA |
| `JWT_SECRET_KEY` | New random secret of at least 32 bytes, stable across restarts |
| `LLM_PROVIDER` | `azure_openai` or `gemini` with an actually available account/model |
| `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_MODEL` | Backend-only Azure generation configuration when selected |
| `GEMINI_API_KEY` | Backend-only; needed for Gemini embeddings even with Azure generation |
| `EMBEDDING_MODEL`, `EMBEDDING_DIMENSIONS` | Match reviewed vectors: `gemini-embedding-001`, `768` |
| `AZURE_SPEECH_KEY`, `AZURE_SPEECH_REGION` | Optional Voice configuration; never send the subscription key to the frontend |
| `DB_POOL_SIZE`, `DB_MAX_OVERFLOW` | Defaults 5 + 5, at most 10 application connections with one worker |
| `DB_POOL_TIMEOUT`, `DB_CONNECT_TIMEOUT` | Default 10 seconds, with connection pre-ping/recycle |
| `LLM_TIMEOUT_SECONDS` | Default 60; some generation paths use a shorter shared deadline |

Store secrets in provider settings, never build args or Git. Confirm database
extension privileges and vector search-path compatibility on the chosen host.
Do not casually trust `X-Forwarded-For`: configure `FORWARDED_ALLOW_IPS` only for
the actual ingress, then verify spoofed headers cannot change client identity.
Otherwise legitimate users may share proxy-IP quotas. No reverse proxy was
configured/tested by this local audit.

`/health` is process liveness. `/health/ready` adds a bounded connection attempt
and checks core PostgreSQL initialization tables and vector availability, with
controlled 503 errors. It does not prove providers, corpus coverage or that every
migration is current. The Render sample uses liveness to avoid a restart loop
during a transient database outage; readiness is a separate launch gate.

## Explicit rollout order

1. Review and separately approve the intended Git revision; the working tree may
   contain uncommitted fixes. No audit action deploys the repository.
2. Provision the intended new database, secure alternate Data API access, configure
   TLS, and verify the target independently before running any migration.
3. Build `docker compose build backend`. Run these commands only with an ignored,
   operator-controlled `.env.production` pointing at the intended cloud database:

   ```sh
   docker run --rm --env-file .env.production ai-interview-coach-backend:latest alembic upgrade head
   docker run --rm --env-file .env.production ai-interview-coach-backend:latest alembic current
   docker run --rm --env-file .env.production ai-interview-coach-backend:latest alembic heads
   ```

   Compare current/head IDs. Enable pgvector using the provider's supported
   process if the migration account cannot create it. Never automatically reset
   the development database or run destructive migrations during startup.
4. Prepare a reviewed knowledge-only import/ingestion scope. Sources are not a
   shipped database. `python -m app.modules.knowledge.ingest_cli --root <directory>`
   is a read-only preview; the generic CLI has **no `--role` option**. A folder
   plan is not Software-Engineer-only rollout approval. Do not import private
   development users or silently apply the full corpus. New embeddings can cost
   money and require a separately reviewed plan/cache.
5. Start one backend instance. Verify HTTPS, readiness, CORS preflight, unauthorized
   rejections, private/no-store responses and absence of secrets in logs.
6. Build Pages with the correct public API origin. Verify copied `_headers`, direct
   refreshes of `/interview/<id>` and `/reports/<id>`, and API connectivity. Without
   a top-level `404.html`, Pages provides SPA fallback.
   [Pages routing](https://developers.cloudflare.com/pages/configuration/serving-pages/).
7. Verify real Technical/HR journeys with synthetic users, then restart/recover and
   inspect stored answers, turn evaluations and reports. Check cross-user access.
8. Configure actual service quotas and billing controls. Perform a bounded real-AI
   smoke test and the final human microphone acceptance check. Mocks cannot pass
   these gates. Alerts are not a hard spending ceiling.
9. Create an encrypted offsite backup and verify a disposable restore. Record
   retention, recovery ownership, RPO/RTO and an image rollback procedure.

For reproducible local regressions, explicitly select the newly built image:

```sh
python scripts/test_backend_isolated.py --image ai-interview-coach-backend:latest
cd frontend
npm ci
npm test
npm run build
```

The Linux lock is the tested Python 3.12 image snapshot, not a Windows lock.
Update source constraints, regenerate the Linux lock, test and audit deliberately.

## Remaining operating boundaries

- Keep one worker/replica. Rate limits, locks and active checkpoints are local to
  the process; a distributed deployment needs additional coordination.
- Request/concurrency quotas are not currency caps. Public registration and
  resource-scoped browser Speech authorization need provider-side abuse/spending
  controls and an access-controlled private-beta boundary before broad exposure.
  Protect both frontend and API ingress; protecting Pages alone does not prevent
  direct registration or paid requests to a public `onrender.com` API address.
- Completed/deleted checkpoint stores are released. Abandoned active sessions
  can occupy memory until restart/deletion; monitor active count and RAM.
- Tokens use browser storage; no refresh-token or immediate revocation system is
  implemented. Password changes do not revoke issued JWTs. Keep the short TTL
  and test reauthentication during long interviews.
- Stable portraits are intentional. No rig or phoneme lip-sync is claimed. Test
  physical microphones, speakers and supported browsers separately.
- A sequential mock journey or a 512 MiB local container does not establish cloud
  concurrency, throttled-CPU capacity or an availability SLA. Measure the actual
  deployment before widening access. Back up data independently of free-tier sleep.
