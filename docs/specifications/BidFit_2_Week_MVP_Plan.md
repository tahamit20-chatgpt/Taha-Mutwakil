# BidFit two-week MVP execution plan
Version 1.0 • Ten development working days from commencement

## Delivery assumptions
Prototype only, synthetic English text PDFs/TXT, no corporate integrations or certified pump selection. Planning basis: two experienced developers each with 60 focused hours over ten days (120 hours total), plus owner and application engineer availability. Backlog P0 effort is 116 focused hours across 20 tasks, leaving four hours within the 120-hour capacity assumption. This is a thin contingency, so any material issue triggers scope/date review. Engineering review allowance is eight additional hours. One developer should plan approximately twice the elapsed duration or reduce scope explicitly. AI coding assistance does not remove engineering review, test or deployment work.

The original brief places most implementation in week 2. To meet the target, start a thin end-to-end path during week 1 while architecture/rules are refined. No need to wait for EasySelect data or advanced benchmarking. Days are relative; the owner chooses the start date.

| Day | Developer A (backend/data) | Developer B (UI/integration) | Review/evidence |
|---|---|---|---|
| 1 | Bootstrap repository, Compose, schemas/migrations and CI | Wireframes, typed UI shell, synthetic RFQ fixtures | Owner accepts scope; engineer reviews missing-data policy |
| 2 | OIDC session integration, project authorization | Login, dashboard, project/tag screens | Cross-project access denial demonstrated |
| 3 | Quarantine upload, private storage and durable jobs | Manifest, upload and progress/failure states | Unsupported file remains an explicit coverage gap |
| 4 | Page-preserving parser and extraction adapter | Source viewer and proposed fact review | Physical page citations verified against fixture |
| 5 | Unit normalization, conflict records and correction versioning | Accepted fact revisions and validation feedback | End-to-end upload-to-reviewed-facts checkpoint |
| 6 | Approved rule-pack interpreter and deterministic evaluation | Criterion table, coverage and four outcomes | Engineer accepts synthetic result truth table |
| 7 | Per-tag/lot rollup, approval scope and unknown handling | Clarification register and separate commercial form | Missing portfolio evidence cannot produce NO-GO |
| 8 | Adjudication, audit and stale-run checks | Review action, revision history and management disposition | Commercial score cannot bypass prohibition |
| 9 | HTML/JSON/CSV exports, retry/restart checks | Exports and integrated workflow tests | Report matches frozen run; formula/HTML injection tests |
| 10 | Security fixes, smoke/load timings, restore rehearsal | Demo polish, runbook and recorded fixture walkthrough | Owner/engineer demo review and next-phase decision |

## Daily checkpoints
Do not proceed with insecure shared access to preserve a demo date. If authentication/storage is blocked, run the prototype locally with synthetic data and disclose the gap. At day 5, if citations or accepted fact snapshots are unreliable, drop polish, OCR and candidate views to finish evidence/rules. At day 8, if four outcomes cannot be reproduced deterministically, defer external deployment and demonstrate a local controlled workflow.

## Exit criteria
- Invite-only users can create scoped projects and upload allowed fixtures.
- Processing states and failed/unreadable pages remain visible; partial coverage cannot appear complete.
- At least one multi-tag RFQ is parsed and reviewed with exact source locations.
- Synthetic rule namespace demonstrates GO, CONDITIONAL GO, NO-GO and INSUFFICIENT DATA without real KSB assertions.
- Decision-critical unknowns and contradictions abstain; non-waivable failures cannot be waived in management UI.
- Candidate rejection never becomes project NO-GO without documented completeness.
- Every evaluated run pins document, fact, capability and rule versions.
- Engineer disposition, reason and evidence persist; edits invalidate prior approval for the current project state.
- HTML/JSON/CSV reports agree and include sources, assumptions, unresolved issues and preliminary status.
- Cross-project authorization, retry idempotency and worker restart tests pass.
- Measured performance, unresolved defects and release limits are documented. The proposed ≤2-second evaluation target is measured separately from parsing/OCR.

## Dependencies and approval queue
Day 1: owner confirms synthetic-only scope and team capacity. Day 2: company-approved deployment/auth/provider decisions if cloud demonstration is desired. Day 5: engineer reviews schema and minimum screening coverage. Day 6: engineer approves production rules only if authoritative limits exist; otherwise retain synthetic demo rules and UNKNOWN real evaluations. GOAL weights remain unset pending the actual checklist.

## Phase 2 hydraulic roadmap (separate workstream, indicative)
| Gate | Indicative effort after data availability | Exit evidence |
|---|---|---|
| Authorized data pilot | 2–4 weeks | One family with approved curves, conditions, limits and reuse rights |
| Deterministic engine | 3–5 weeks | Independent tests for interpolation, power, NPSH, duty envelope and abstention |
| Engineer validation | 2–4 weeks | Held-out cases compared with authoritative approved selections; discrepancy log |
| Controlled pilot | 2–4 weeks | Recall, false-GO, review effort and data coverage accepted by engineering |

Windows may overlap but cannot be committed before data review. Add materials/viscosity/series-parallel services only with approved methods. Phase 3 then covers compliance matrices, scope of supply and quotation drafting; costing/pricing interfaces are separate authorized integrations.

## Delivery boundary

- Established: ten-day prototype sequence and explicit exit tests
- Uncertain: team availability, extraction effort and deployment prerequisites
- Engineering approval: decision coverage and any real active rules
- Implement immediately: P0 backlog in parallel backend/UI workstreams
- Postpone: OCR-heavy packages, advanced selection and production release
