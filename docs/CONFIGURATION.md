# Configuration

No external credentials are required for local demo. Never put secret values in source control or chat. Configure them securely in your environment.

| Variable | Meaning |
|---|---|
| `BIDFIT_MODE` | Default `demo`; anything else disables local demo login and ingestion pending security integrations |
| `DATABASE_URL` | SQLAlchemy `postgresql+psycopg://…` URL; local Compose default in config.py |
| `S3_ENDPOINT`, `S3_BUCKET` | Default loopback S3rver, private `bidfit-private` bucket |
| `S3_ACCESS_KEY`, `S3_SECRET_KEY` | Private S3 service credentials; demo-only fallback `S3RVER` |
| `SESSION_SECRET` | Stable random session-state signing secret; local default generated in ignored `.runtime/session-secret` |
| `OIDC_ISSUER`, `OIDC_CLIENT_ID`, `OIDC_CLIENT_SECRET`, `OIDC_REDIRECT_URI` | Approved HTTPS OIDC provider; callback `/api/v1/auth/callback` |
| `OIDC_INVITES_JSON` | Subject-bound invite map: `{"provider-subject":{"user":"internal-user-id","tenant":"tenant-id","role":"Engineer"}}`; no auto-enrolment from email domain |
| `EXTRACTION_PROVIDER` | `demo` (default) or `openai` |
| `LLM_MODEL`, `LLM_API_KEY` | Explicit approved model ID and secure API binding |
| `PROVIDER_EGRESS_APPROVED` | Must equal `yes` before any real model call; keep unset for demos/CI |
| `BIDFIT_DEMO_NETWORKS` | Optional local Docker-only peer CIDRs for demo login; private bridge peers only, with API host port bound to loopback. Default unset for direct development; never production auth |
| `CHROMIUM_PATH` | Browser executable for Playwright, if not `/usr/bin/chromium` |
| `TEST_DATABASE_URL` | Isolated test database URL ending `_test`; PostgreSQL credentials must permit its creation |

Real extraction destination is fixed `api.openai.com` over verified HTTPS; documents cannot select URLs. Any cloud network allowlist must explicitly permit it only after the owner approves data processing. No real provider call was made in this implementation. No approved managed OIDC or production object service was available; their live integration remains unverified. No secret requirement was added to the onboarding draft since the requested synthetic milestone does not need one.

Development outbound installation destinations: npm registry, Python package index, Docker Hub. Browser tests use preinstalled Chromium; the initial Playwright browser download was network-denied, resolved by using the installed browser. An initial MinIO Docker pull failed; current local storage is disk-backed S3rver, not MinIO.
