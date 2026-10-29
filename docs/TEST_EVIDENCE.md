# Aramco Approval Intelligence test evidence — 29 October 2026

## Final upgrade checks (Linux x86-64)

- **54 backend tests passed inside the final non-root Docker image**, with real
  PostgreSQL and private S3-compatible storage: **63.92 s**. This includes all
  previous 40 tests and 14 new approval/migration tests. Nothing skipped or xfailed.
  156 warnings concern upstream deprecated calls and an optional read-only pytest
  cache; no application test failed.
- **7 Chromium browser journeys passed against the final Docker app**, **32.8 s**:
  the five existing journeys plus approval-registry filtering/administration and
  the complete Aramco upload → fact review → candidate review → summary
  acknowledgement → matrix → frozen JSON export workflow.
- Strict TypeScript/Vite production builds passed natively and in Docker.
- Fresh Docker startup initialized DB/storage, applied migrations, started API and
  worker, and seeded all five examples through the actual document/job APIs.
  Both Aramco examples produced INSUFFICIENT DATA with pending source/current
  verification; Omega's API 610 deviation was explicit.
- The migration test upgrades an actual 0001-shaped PostgreSQL database containing
  a legacy RFQ/evaluation and checks its complete frozen payload remains identical.
  All nine pre-2.0 evaluation hashes in the existing development DB are unchanged.
- Restarting the Docker API/worker and rerunning the seed preserved all 11
  test-instance project identities, 8 mappings and 10 frozen run hashes; no
  duplicate examples appeared.
- Original Phase 1 and 2.0 Windows ZIP hashes remain unchanged. The new ZIP has an
  internal SHA-256 file manifest and is separately delivered. Native Windows/WSL
  installation and Chrome auto-launch cannot be executed in this Linux workspace.

## Requested approval scenarios

| Required scenario | Executed test |
|---|---|
| Historical RPH / 6000002356 match, correct vendor/plant, no current verification or automatic GO | test_historical_rph_match_is_not_current_verification_or_go |
| WKB, RPH-V, WKTR under 6000002288; exact idempotent seven/eight seed | test_idempotent_exact_seed_and_many_series_lookup |
| MegaCPK ISO identifiers, no automatic certification | test_megacpk_design_references_do_not_certify_iso |
| Omega deviations / no assumed API 610 compliance; versioned evidence policy | test_omega_api610_deviation_and_configuration_policy |
| Unlisted code and missing explicit code, neither automatic NO-GO nor inferred requirement | test_unlisted_code_and_missing_explicit_code_are_not_negative_approval_claims |
| Saudi Water Authority receives no automatic Aramco requirements | test_other_customer_preserves_existing_decision_and_no_aramco_requirements |
| Pump/valve/parts isolation and no parts pump-model association | test_mixed_package_isolation_and_parts_commodity_has_no_pump_model |
| Existing RFQ regression / additive migration | All existing 40 tests plus test_additive_migration_retains_existing_rfq_and_evaluation |
| Modification authorization / protected source / cross-user and tenant access | test_admin_permissions_private_evidence_and_cross_project_isolation |
| New review/source revision retains history and all three frozen exports, stale-current gates | test_verification_append_only_preserves_frozen_reports_and_stales_current_run; test_admin_mapping_and_commodity_revisions_keep_original_audit_sources |

Additional tests exercise conflicting 9COM/vendor/plant requirements, textual
leading zeros, exact source lines, malformed identifiers, future verification,
historical-source misuse, demo verification claims, explicit validity and as-of
date handling. The upgrade does not validate genuine customer authority, original
PDF/PPTX contents, real technical compliance, manufacturer capability, component
sources, live identity/LLM/ICAP integrations, native Windows, or production security.

---

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
