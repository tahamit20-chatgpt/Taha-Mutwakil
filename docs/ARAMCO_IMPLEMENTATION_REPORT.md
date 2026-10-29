# Aramco Approval Intelligence — implementation report

This upgrade extends the existing BidFit 2.0 application; frontend, backend,
processing worker, PostgreSQL, private S3-compatible storage, authentication,
existing deterministic rules and Windows launchers are retained.

## Implemented

- Six tenant-scoped relational tables with a non-destructive `0002` migration,
  idempotent transactional seed, extensible metadata, many-to-many mapping keys,
  revision/audit events and append-only verification reviews.
- Exactly seven initial historical commodity codes, vendor `10066368`, plant
  `30008606`, date `2024-04-01`, reference `SQU-26-24`; eight product-series
  mappings. Parts remain a separate commodity without an automatic pump model.
- Existing source extraction/review allowlist extended for 9COM, vendor, plant,
  manufacturer and component approval requirements; exact source citations and
  textual identifiers preserved. Demo extraction remains labelled pattern-based.
- Customer-specific item assessments ARAMCO-001 through 010, plus Omega/API 610
  deviation check 011. Accepted explicit requirements, suggested classifications,
  candidate selection, historical listing, current verification, independent
  technical compliance and commercial assessment remain separate.
- Knowledge Library approval registry with five filters; Product Library series
  profiles; RFQ summary approval review; frozen compliance evidence and reports.
- Functional administrator operations for source metadata, supplied commodity,
  series and mapping revisions, synthetic private test attachments, review history,
  conditions and a limited versioned evidence policy. Shared-record writes and
  verification reviews require distinct permissions.
- Frozen registry/policy/source metadata in every new Aramco evaluation. New
  registry evidence, revisions and date-sensitive changes invalidate current
  reliance while historic HTML/JSON/CSV exports remain unchanged.
- RPH and Omega synthetic examples and a Windows guide, without a new host
  prerequisite or paid service. Existing data volumes and old downloadable
  packages remain intact.

## Principal files

| Area | Added/changed files |
|---|---|
| Data | `backend/app/approvals/store.py`, `migrations/versions/0002_approval_registry.py`, `migrations/env.py`, `backend/app/configuration/aramco_seed.json` |
| Logic/API | `backend/app/approvals/models.py`, `service.py`, `routes.py`; existing `workflow/service.py`, `workflow/routes.py`, `api/access.py`, `main.py`, `extraction/service.py`, `auth/service.py`, `reports/service.py` |
| Interface | New `frontend/src/Approvals.tsx`; existing `Libraries.tsx`, `Workspace.tsx`, `api.ts`, `style.css` |
| Tests | `backend/tests/test_approvals.py`, `frontend/e2e/approvals.spec.ts` |
| Delivery | `infra/seed_demo.py`, `infra/package_zip.py`, `infra/Dockerfile.local`, `fixtures/synthetic/aramco-rph.txt`, `aramco-omega.txt`, `approval-test-source.txt`, `BIDFIT_ARAMCO_WINDOWS.txt`, README and existing Windows guide |
| Documentation | `ARAMCO_9COM_APPROVAL_REGISTRY.md`, `KSB_PRODUCT_9COM_MAPPING.md`, `APPROVAL_VERIFICATION_LOGIC.md`, `APPROVAL_DATA_PROVENANCE.md`, this report, original request, updated test evidence/OpenAPI/architecture/data model/backlog |

## Evidence and remaining dependencies

The actual approval letter and product presentation were NOT attached, imported
or inspected. Historical listings and product mappings are owner-supplied
structured references; their source attachments remain PENDING. None of the
seven current approvals is independently verified. No expiry dates or actual
source page numbers were invented. User-reported slide references remain labelled
as such. No original protected document is committed or bundled.

Genuine current verification and live document attachment need the approved
scanner/source-authorization integration. Current customer data access,
configuration-specific approvals, component/9CAT sources, customer standards and
approved engineering rules remain unavailable. Real pump performance, hydraulic
selection, material compatibility, manufacturing availability and commercial
competitiveness are not validated by this upgrade. Production identity/authority
integration and native Windows execution remain unverified.

Next recommended development task: implement and validate controlled onboarding
of the authorized original letter/presentation and an authorized current approval
source, with private storage, scanning, designated review and discrepancy
reconciliation. Then connect configuration-specific and component evidence before
expanding current eligibility policy. See TEST_EVIDENCE.md for executed tests.

## Executed validation

54 backend tests passed in the final Docker image (63.92 s), including all 40
previous tests and the actual upgrade test. Seven Chromium browser journeys
passed against that image (32.8 s). TypeScript/Vite and Docker builds passed.
Restart/reseed retained 11 test projects and 10 frozen runs without duplication;
the nine original pre-2.0 development snapshots and both earlier Windows ZIPs
remain unchanged. Windows/WSL/Chrome startup itself was not executed here.
