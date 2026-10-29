# BidFit 2.0 test evidence — 29 October 2026

## Executed on Linux x86-64

- **40 backend tests passed** inside the rebuilt non-root Docker app image with real PostgreSQL and private S3-compatible emulator, in **46.34 s**. Includes all original 21 tests. No skipped/xfail/zero-test result. Upstream deprecation and optional read-only pytest-cache warnings remain; these are not failed tests.
- **5 actual Chromium browser journeys passed against the Docker app**, in **23.9 s**: complete 2.0 classification→summary review→matrix/export; unavailable explicit standard→INSUFFICIENT DATA; rule draft/designated approval plus product/candidate/reference-review and draft price UI; original GO workflow; original missing-data workflow.
- Strict TypeScript and Vite production build passed natively and during Docker build. A refresh/remount bug that cleared the review reason was fixed and both 2.0 flows rerun successfully. Native select controls are tested by their accessible combobox role.
- Fresh Docker build/start/init/DB/storage/API/worker checks passed. The launcher created original and new examples through the actual API/worker. Rebuilding/restarting kept example records and did not duplicate them.
- All **9 pre-upgrade frozen evaluation snapshots** in the development instance retained their original hashes. Legacy RFQs remain readable/evaluable; explicit classification adoption preserves facts/runs and changes project revision.
- ZIP integrity/file-manifest checks, Windows launcher static checks and source-file inclusion are checked during packaging. Windows itself, WSL installation and automatic Chrome launching are **not** available for execution here.

## Required scenarios

| Owner case | Evidence |
|---|---|
| Complete pump RFQ | `test_v2_four_frozen_decisions[go-GO]` and complete browser journey; synthetic only |
| Missing NPSHA | `test_missing_npsha_and_unavailable_standard_never_pass`; no hydraulic-feasibility claim |
| Unsupported type | `test_approved_synthetic_product_prohibition_requires_exact_confirmed_value`; DRAFT abstains, designated approved synthetic prohibition blocks |
| Possible deviation | 2.0 CONDITIONAL GO fixture and DEVIATION assertion |
| Mixed package | separate pump/valve/parts findings; no pump rule applied to other categories |
| Contradictory documents | accepted conflicting values and standard editions retained; no newest-upload precedence |
| New revision | original bytes/versions retained; summary approval invalidated and old HTML/JSON/CSV unchanged after edits |
| Unavailable standard | explicit API 610 edition/source retained, NOT VERIFIED / REQUIRES REVIEW; no clause text invented |
| Historic access | legacy adoption/integration test and nine preserved instance hashes |
| Unauthorized access | project/tenant/role/CSRF/jobs/downloads/exports/studios/quote/rule-approval isolation |

Further checks cover exact Word paragraphs/Excel cells, ZIP traversal/absolute/drive/backslash paths and expansion bounds, candidate data without approved portfolio exclusion, retry/lease/idempotency, finite units and pressure basis, corrected-vs-original facts, stale active rule revisions, source hashes, safe HTML/CSV, separate commercial gates and rejection of free-text hard-stop bypass.

## Untested or deliberately unavailable

Real KSB standard compliance, approved source coverage, hydraulic selection, live OIDC/provider integrations, ICAP/EasySelect, real commercial pricing, confidential data, native Windows/ARM desktops, hosted preview/public deployment and production security/load/backup certification. The old pure-engine benchmark is historical and is not presented as a 2.0 end-to-end performance claim.
