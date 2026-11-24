# PrepMate: Vercel Hobby + Render Free + Azure PostgreSQL

Final architecture, 24 November 2026. This supersedes App Service, Container Apps,
Cloudflare Pages and Supabase hosting proposals. Preparation is **not approval to
commit, push, deploy, change firewall rules or buy services**. No Render/Vercel URL
is allocated yet. Keep AI and Speech disabled during initial hosting verification.

## Prepared configuration

- `render.yaml`: Free Docker, Singapore, manual deployments, one worker, `/health`,
  public registration and persistent quotas. No new database/disk/registry.
- `frontend/vercel.json`: Vite build, `dist`, SPA deep links and security headers,
  including `microphone=(self)`. Vercel ignores Cloudflare's `_headers` syntax.
- API loading-page/network failures produce a readable recovery message. No
  automatic request replay, health polling or artificial keepalive is added.
  Existing session restoration retains credentials on recoverable failures.
- Existing image tested locally at **0.1 CPU / 512 MiB**: **42.988s** startup,
  **4.283s** first DB readiness, **128.7 MiB** idle, **231.65 MiB** observed peak.
  Non-root/one worker; `prepmate_api` with verify-full TLS 1.3; read-only counts
  30 knowledge / 0 users / 0 interviews / 0 quota rows. This is a hosting smoke
  test, not PDF/AI stress testing or a measurement on Render.

## 1. Git review, then separately approved publication

Use `feature/phase5-saas-redesign` and the exact approved commit. GitHub currently
does not include all local public-access/container fixes. Review the complete diff;
keep sources, tests and JSON taxonomy/reviewed knowledge metadata in Git. Exclude
all real `.env` files, storage/evidence, backups, ZIPs, credentials and local data.
No files have been staged/committed/pushed by this task. No merge or force push.

Suggested commits: (1) public demo access, persistent quota protections and Docker
hygiene; (2) Render/Vercel deployment, cold-start error handling, tests and docs.
Render builds from Git: no GHCR/ACR publication or registry account is needed.
Old Azure proposal files remain historical, not executable deployment plans.

## 2. Render dashboard — after approval

**New → Web Service**, connect `Gautamgoyal1/ai-interview-coach`, choose the reviewed
feature-branch commit. Manual creation uses this table; a `render.yaml` Blueprint
is an alternative, not a second service.

| Field | Value |
| --- | --- |
| Name | `prepmate-api` or an available unique variant |
| Branch | `feature/phase5-saas-redesign` |
| Region | **Singapore**; confirm Free is offered before creation |
| Runtime | **Docker** |
| Root Directory | Empty / repository root |
| Dockerfile Path | `./backend/Dockerfile` |
| Docker Build Context Directory | `./backend` |
| Docker Command | Empty, use the existing image CMD |
| Instance Type | **Free**: 0.1 CPU / 512 MB; one instance |
| Health Check Path | `/health` |
| Auto-Deploy | **Off** |
| Initialization / pre-deploy commands | Empty |
| Shutdown delay | 60 seconds, as in render.yaml |

No Render database, disk, dedicated outbound IP, paid build machine or add-on.
If Singapore Free is unavailable, stop rather than relocate/upgrade silently.
Creation can start the first build; flags must be off from the outset. Readiness
can fail until approved DB firewall rules exist. `/health` avoids dependency-driven
restart loops; verify `/health/ready` separately. The existing Dockerfile honors
Render's `PORT`, uses the audited Python 3.12 lock and runs as non-root/one worker.
[Docker](https://render.com/docs/docker),
[Blueprint configuration](https://render.com/docs/blueprint-spec).

Enter these in **Environment**, as runtime variables, not build args:

| Variable | Initial value |
| --- | --- |
| `APP_ENV` | `production` |
| `DATABASE_URL` | Private restricted runtime URL below |
| `JWT_SECRET_KEY` | Existing stable secret from the protected local deployment secrets file |
| `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES` | `HS256`, `15` |
| `STAGING_ENABLED` | `true`, retains persistent quotas |
| `STAGING_ACCESS_MODE` | `public` |
| `STAGING_REGISTRATION_ENABLED` | `true` |
| `STAGING_ALLOWED_EMAILS` | Omit; no invitation restriction |
| `AI_ENABLED`, `SPEECH_ENABLED` | Both `false` |
| `AI_GLOBAL_CONCURRENCY` | `1` |
| `STAGING_AI_USER_DAILY_LIMIT`, `STAGING_AI_GLOBAL_DAILY_LIMIT` | `30`, `100` |
| `DB_POOL_SIZE`, `DB_MAX_OVERFLOW` | `2`, `2` |
| `DB_POOL_TIMEOUT`, `DB_CONNECT_TIMEOUT` | `10`, `10` seconds |
| `FORWARDED_ALLOW_IPS` | Empty until ingress trust is verified; never `*` |
| `LLM_PROVIDER` | `azure_openai` |
| `EMBEDDING_MODEL`, `EMBEDDING_DIMENSIONS` | `gemini-embedding-001`, `768` |
| `CORS_ORIGINS` | Exact JSON array in step 4 |

Without explicit proxy trust, IP buckets may conservatively group users behind
Render ingress. Per-account/global limits remain active. Verify actual trusted
ingress addresses and spoofed headers before configuring explicit IPs/CIDRs; Render
**outbound** ranges do not establish inbound proxy identity. Never disable limits.

Provider keys remain absent initially. After hosting/provider/spending verification,
add `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_MODEL`,
`GEMINI_API_KEY`, `AZURE_SPEECH_KEY`, `AZURE_SPEECH_REGION` and optional
`AZURE_SPEECH_ENDPOINT` to **Render only**. Preserve embedding model/dimension.
Request quotas are not dollar/Speech-minute caps; configure provider controls first.

### Existing database and certificate verification

Read the protected `.env.azure-container-apps.secrets` locally as the existing
credential source despite its historical filename. Do not print it, edit it or
change the development `.env`. The Docker image's verified certifi path applies.
Only this URL shape is public; replace the password privately, URL-encoded:

```text
postgresql+psycopg://prepmate_api:<URL_ENCODED_PASSWORD>@prepmate-staging-db.postgres.database.azure.com:5432/prepmate_db?sslmode=verify-full&sslrootcert=/usr/local/lib/python3.12/site-packages/certifi/cacert.pem
```

Never use the admin role, weaken TLS, replace the hostname with an IP or put DB
credentials in Vercel. The existing database already has 12 tables, revision
`b8c9d0e1f2a3`, pgvector 0.8.7 and 30 reviewed Software Engineer records, 10 per
difficulty, with 768-dimensional vectors. **Do not migrate, recreate, seed, copy
local candidate data or generate embeddings during this hosting deployment.**

### Render egress → Azure firewall — separate approval required

In the actual Singapore service, open **Connect → Outbound**. Copy **all IPv4
CIDRs**, preserving the service ID/date. Exact current ranges are not verified
before creation; never reuse an old online list. Any IP in those shared ranges
may be used. Azure's inclusive start/end rules can represent each complete CIDR.

Convert each copied CIDR locally; this performs no cloud change:

```powershell
python -c "import ipaddress; n=ipaddress.ip_network(input('Render IPv4 CIDR: ').strip(), strict=True); assert n.version == 4 and n.is_global; print('Start:', n.network_address, 'End:', n.broadcast_address)"
```

After approval: Azure Portal → existing PostgreSQL server → **Networking → public
access/firewall**. Add one clearly named rule per displayed CIDR with those exact
start/end addresses. Preserve the laptop rule; leave **Allow Azure services** off.
No 0.0.0.0 exception, all Internet, whole Azure region, single observed egress IP,
or network/broadcast-only host rules. Review unexpected broad/IPv6-only ranges
instead of widening access. These are shared regional IPs, not app-exclusive
identity: password, verify-full and restricted grants remain essential. Recheck
ranges after provider changes/recreation and save a receipt of rules added.
[Render outbound contract](https://render.com/docs/outbound-ip-addresses),
[Azure firewall](https://learn.microsoft.com/en-us/azure/postgresql/security/security-firewall-rules).

## 3. Vercel dashboard — after approval

**Add New → Project → Import Git Repository**, personal **Hobby**, not Pro trial.
Use the same repository and approved feature-branch commit.

| Field | Value |
| --- | --- |
| Project | `prepmate` or an available variant |
| Framework Preset | **Vite** |
| Root Directory | **frontend**, so its vercel.json is used |
| Install Command | `npm ci` |
| Build Command | `npm run build` |
| Output Directory | `dist` |
| Node.js Version | **24.x** |
| `VITE_API_BASE_URL` | Actual `https://<assigned-service>.onrender.com` origin |
| `VITE_API_URL` | Same exact API origin; no trailing slash |

Set both public variables for **Production** before building. Set Preview only
when deliberately testing previews. These are build-time values; rebuild after
changing them. No DB/JWT/provider secrets. Requests go directly to Render; no
Vercel function or backend proxy is needed.

Verify **Settings → Environments → Production → Branch Tracking** is the approved
feature branch.
If import initially builds main, do not share/promote it: select the correct branch
and create a deployment of the reviewed commit before using the production alias.
No main merge is necessary. In **Settings → Deployment Protection**, make the
intended production site public; previews can remain protected. Verify refresh of
`/dashboard`, `/interview/<id>`, `/reports/<id>` and normal static assets. The
prepared SPA rewrite is Vercel's documented Vite recipe, not a change to app routes.
[Vite](https://vercel.com/docs/frameworks/frontend/vite),
[Git deployments](https://vercel.com/docs/git).

## 4. Exact production CORS

Before the frontend exists, an initial Render-only check may use the actual API
HTTPS origin as the sole CORS origin. Then replace it with the **actual production
Vercel alias**, for example only if this alias is assigned:

```json
["https://prepmate.vercel.app"]
```

Use the actual variant/custom domain otherwise. No trailing slash, path, wildcard,
`*.vercel.app`, blanket previews or localhost. Add an exact stable preview origin
only deliberately. Updating Render's environment redeploys the backend. Verify the
real frontend preflight succeeds and a foreign origin is rejected. Do not reverse
the frontend/API values: CORS names the UI; Vite variables name the API. Neither
URL is allocated by this document.

## 5. Launch verification and persistence

With AI/Speech still off: check approved commit/build and secret-free logs; HTTPS;
`/health` and `/health/ready` 200; `/docs` 404; anonymous private routes 401; response
headers; CORS; synthetic signup/login and two-user isolation; unchanged knowledge
digests. Use dashboard CPU/memory metrics and one manual request after natural idle
sleep for cold-start measurement. No cron, uptime monitor, browser polling or
artificial keepalive. Free Render has no interactive shell: use HTTPS, logs and
metrics. Local DB identity verification alone is not proof of the cloud socket's
role; record the verified runtime config and live readiness evidence honestly.

Resume PDFs use existing upload/parser limits and in-memory processing. Filenames
and completed analysis JSON persist in Azure; original PDFs are not a durable
download archive. Sessions, saved answers/evaluations, reports, practice results
and daily usage counters are in PostgreSQL. In-memory checkpoints recover from
saved session state. Unsent drafts/transcripts, recordings and in-flight work before
commit do not gain persistence from deployment. Keep the existing backup/verified
restore procedure; no live restore or schema alteration is part of this plan.

After hosting and provider controls pass, verify bounded real Resume/Technical/HR
journeys and restart/report persistence before enabling broader use. HTTPS plus
`microphone=(self)` permits user-granted microphone access on the top-level Vercel
page. Explicit record/play actions remain required. CSP permits Speech HTTPS/WSS
and blob audio; browser STT connects to Azure, token/TTS to Render. Physical
microphone/autoplay checks remain manual and cannot pass while Speech is off.

## Limits and costs

Render Free: 0.1 CPU/512 MB; 750 shared workspace hours/month; sleep after 15 idle
minutes and roughly a minute to wake. No persistent disk; arbitrary restarts and
high external DB/API traffic can cause disruption/suspension. Hobby includes 500
standard build minutes and 5 GB outbound/month, then $0.15/GB public egress. No
payment method can mean suspension at allowances; a linked method can allow billed
overages. Review billing/build spend controls, keep paid add-ons off and avoid
rebuild loops. Provider health checks are not an uptime guarantee.
[Compute](https://render.com/docs/compute-plans),
[Free limits](https://render.com/docs/free),
[Build allowance](https://render.com/docs/build-pipeline),
[Bandwidth](https://render.com/docs/outbound-bandwidth).

Vercel Hobby is noncommercial personal hosting, suitable for this academic demo.
Current allowances include 100 GB fast data, 10 GB origin transfer and 1M CDN
requests; usage can pause at limits. No paid functions, AI Gateway, storage or
analytics add-ons are needed. Confirm account allowances before launch.
[Hobby](https://vercel.com/docs/plans/hobby),
[Fair use](https://vercel.com/docs/limits/fair-use-guidelines).

Added fixed hosting target: **$0/month within allowances**, not guaranteed zero total
cost. Existing Azure DB compute/storage/backups and AI/Speech remain separate.
DB responses to Render are Azure public Internet egress, not Azure inter-region
traffic: Azure publishes a shared first 100 GB/month free Internet allowance, then
an Asia Premium-network reference of $0.12/GB in the next tier. Confirm invoice and
shared usage. Queries/provider calls from Render and TTS to browsers consume its
egress allowance. Singapore–East Asia adds latency, unmeasured until live hosting.
Students spending limit remains On.
[Azure bandwidth](https://azure.microsoft.com/en-us/pricing/details/bandwidth/).

Keep the approved Git revision, stable JWT, environment and firewall receipt for
rollback. Roll back application deployments only; leave user data/schema/knowledge
intact. Disable AI/Speech before active-test redeployments: old/new processes may
briefly overlap, and in-memory limits are not distributed locks. No automatic
migration/embedding hook is configured.

Ready for review of Git publication and controlled Free deployment, with actual
Singapore capacity, outbound rules, URLs/CORS and live checks still pending.

## Local verification and proposed Git scope

- **44 focused backend tests passed**, network-disabled container/SQLite; the
  previously completed 533-test suite was not repeated.
- **155 frontend tests passed**; TypeScript/Vite production build passed. Existing
  approximately 770 KB main-chunk warning remains, with no UI redesign or split.
- The resource-limited hosting/TLS smoke and small synthetic PDF parse/invalid-PDF
  rejection passed; no AI/Speech calls, database writes or migrations.
- Render configuration passes its provider JSON Schema; Vercel's configuration
  passes instance validation. The downloaded Vercel schema has an unrelated
  draft-04 meta-schema issue in its unused `experimentalServicesV2` definition;
  it was preserved, not patched or presented as a deployment acceptance result.
- All 24 pending nonignored source/configuration files were scanned against real
  configured credential values with no matches. Only the exact existing
  `coach/change-me` template URL was excluded as a known placeholder. This was a
  worktree scan, not a staged scan; the Git index remains empty.

The 15 files required for the proposed two commits are:

```text
Commit 1 — Preserve public demo access and durable AI quotas
  .env.example
  backend/.dockerignore
  backend/app/core/config.py
  backend/app/core/staging_access.py
  backend/tests/integration/test_staging_access.py
  backend/tests/unit/test_staging_controls.py

Commit 2 — Prepare Render and Vercel free deployment
  .gitignore
  README.md
  docs/deployment.md
  docs/hybrid-deployment.md
  render.yaml
  frontend/.env.example
  frontend/vercel.json
  frontend/src/services/api.ts
  frontend/tests/apiAvailability.test.ts
```

Historical untracked Azure proposal files remain on disk separately; do not stage
them implicitly with `git add .`. Protected environment files, local images/ZIPs,
provider manifests, logs and private evidence stay excluded. Before any approved
commit/push, recheck the exact staged diff and credential scan. Local verification
evidence is in ignored `storage/security-audit/hybrid-prep-20261124/`.
