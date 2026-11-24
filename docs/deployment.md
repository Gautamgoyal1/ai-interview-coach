# PrepMate deployment

The finalized academic-demo architecture is **Vercel Hobby Free frontend, Render
Free Docker backend in Singapore, and the existing Azure PostgreSQL in East Asia**.

Follow [the current deployment runbook](hybrid-deployment.md) for the exact dashboard
settings, environment variables, restricted firewall/TLS setup, CORS, verification,
limits and approval boundaries.

Azure App Service, Container Apps/private networking, Cloudflare Pages and Supabase
hosting proposals are superseded. Preserve the existing Azure database and provider
resources. Do not rerun migrations or embeddings for this hosting deployment.

Configuration preparation does not authorize commits, pushes, deployment, database
firewall changes or paid services. Keep AI and Speech off during initial checks.
