# BidFit 2.0 — architecture inventory and upgrade

This is an in-place extension of commit `7248ede` (the working Windows prototype), on branch `bidfit/2.0`. The original `bidfit/windows-demo` branch/download stays intact. No Git worktree, replacement application, public deployment, technology migration or confidential-data transfer was introduced.

React/TypeScript/Vite still serves from FastAPI under one origin. PostgreSQL/SQLAlchemy, Alembic, the existing tenant-scoped JSON record table, private S3-compatible storage and a separate leased Python worker are retained. New modules live in `backend/app/workflow`, classification JSON in `backend/app/configuration`, reusable access checks in `backend/app/api/access.py`, and extracted frontend components beside the existing API client. There is no database reset or destructive schema migration. Existing RFQs default to the legacy workflow; a deliberate classification save can adopt 2.0 with all tags/facts/runs preserved.

## Inventory / gap assessment

- Existing and verified: cookie sessions, CSRF/revocation, role/project isolation, PDF/TXT parsing, source-backed facts and corrections, deterministic demo screening, frozen HTML/JSON/CSV exports, private objects, leased jobs/idempotency/retries and Windows Docker bundle.
- Improved: RFQ navigation/history, metadata/classification, separate understanding/summary/PROCESS RFQ gates, document formats/revisions, criterion-level findings, rule governance and stale approvals.
- New: six-area configurable classification, per-tag categories, standards metadata and suggestions/explicit requirements/approved-rules layers, versioned synthetic-only registry, library/analytics/settings, exact-PNG branding support, Selection Studio references/reviews, draft pricing references and immutable draft quotation exports.
- Requires engineering data: actual rules/clauses/editions, portfolio coverage, approvals, curves, material compatibility, manufacturing capability and prices. No real values were invented or real data uploaded.
- Future: live rule publication, full normalized/RLS entity model, corporate user/admin provisioning, verified OIDC/provider integrations, OCR, certified hydraulic selection, actual EasySelect/ICAP integration and production approval/submission.

## Authentication

Existing opaque HttpOnly/SameSite cookie sessions and CSRF checks remain. Demo Alice is explicitly synthetic and has configuration/designated synthetic-engineering approval permissions; Bob cannot approve rules or configure master data. Real username/password entry belongs to the configured managed OIDC provider, not an unverified new password store. Company sign-in remains unverified/unconfigured here. Synthetic ingestion still fails closed outside demo mode pending malware scanning/production controls.

## Branding

All visual tokens are centralized in `frontend/src/style.css`. Blue/grey values are **provisional**, not claimed official brand codes. The three inline images are visible to the assistant but their original byte files were not exposed in the workspace. They were not regenerated, traced, substituted from the internet or distorted. Settings accepts an original PNG unchanged (hash recorded); login and navigation use it with preserved aspect ratio. A supplied `frontend/public/branding/ksb-logo.png` can also be bundled later. Until that file is supplied/configured, the interface explicitly says the original logo is pending. Champion 28 and the second mark were not invented or copied into new artwork.

## Parsing limits

General ZIP: at most 100 archive entries and 20 total project files including the container; 25 MiB per original/child, 50 MiB expanded total, maximum 200:1 per-entry expansion. No nested archives, unsafe/duplicate paths, links or encryption. Office packages: at most 1,000 parts, 50 worksheets and 50,000 cells, within the same byte limits. XML entities are disabled. Relevant unsupported drawings, formulas, scans and attachments remain explicit gaps rather than being silently ignored.


## Aramco approval evidence extension

Six relational tables supplement the original record store without replacing it.
The new approval service supplies deterministic evidence findings to the same
reviewed-summary/compliance/decision/report workflow. Customer scope, permissions,
private source storage and frozen evidence are enforced server-side. See
ARAMCO_9COM_APPROVAL_REGISTRY.md and APPROVAL_VERIFICATION_LOGIC.md.
