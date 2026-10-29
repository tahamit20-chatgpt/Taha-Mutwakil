# Approval evaluation logic

The approval module performs deterministic comparisons against database evidence;
it does not ask an LLM to decide eligibility. It runs per equipment tag inside
the existing reviewed-summary → PROCESS RFQ → engineering matrix workflow.

## Inputs and uncertainty

`required_9com`, `vendor_code`, `plant_id`, `manufacturer_approval` and
`component_approval` are allowlisted source fields. In demo extraction, lines use
`field: value` under `Tag: P-101`. The original document/physical page/TXT line or
Office cell/paragraph citation is retained and must pass exact source validation.
All proposals need acceptance/correction/rejection through the existing review.
A required 9COM is a ten-digit string, preserving leading zeros; invalid values
remain unknown. Conflicting or unreviewed facts cannot establish a code.

A selected candidate may suggest an associated 9COM, but it never supplies a
missing customer requirement. Pump-type suggestions are labelled inferred
candidates requiring engineer verification. Proposed vendor/plant values are not
automatically copied from the historical approval profile. Missing or conflicting
values remain gaps. Candidate choices, reasoning and component applicability
reviews are appended to the project audit trail.

## Executable checks

| Check | Logic | Missing/mismatch effect |
|---|---|---|
| ARAMCO-001 | Exact supported Saudi Aramco customer/profile/end-user identity | Other customers: module not applicable |
| ARAMCO-002 | One unambiguous accepted required_9com, no outstanding proposals | Insufficient data; suggestions do not fill missing requirements |
| ARAMCO-003 | Code and item category in owner-reported original historical listing | Not listed/unknown is insufficient data, not proof of current rejection |
| ARAMCO-004 | Selected series/category plus matching commodity association; parts commodity can remain model-independent | Unknown/mismatch is insufficient data, not portfolio exclusion |
| ARAMCO-005 | Explicit proposed/accepted vendor matches historical profile; no contradictory source | Insufficient data |
| ARAMCO-006 | Explicit proposed/accepted plant matches historical profile; no contradictory source | Insufficient data |
| ARAMCO-007 | Current authorized source review with applicable explicit validity, independent of the historical listing | Requires verification → insufficient data |
| ARAMCO-008 | Technical suitability explicitly delegated to independent engineering checks | Never an approval-based technical PASS |
| ARAMCO-009 | Standards, editions and deviations explicitly delegated to independent checks | Portfolio metadata never grants contractual compliance |
| ARAMCO-010 | Component supplier/9CAT applicability reviewed with evidence; a manual VERIFIED assertion is not authority | Pending → insufficient data; supported not-applicable has no decision effect |
| ARAMCO-011 | Omega plus API 610 reference/applicability flags known design deviations | Default insufficient data; designated policy may require conditional review |

A COMPLIANT label on a registry comparison only means that specific reference
comparison matches; it is not a technical compliance certificate. The matrix
includes separate reasons, authority, rule/policy version/hash, references and
required actions. Technical checks 008/009 explicitly say evaluated separately.
No critical/major engineering severity is invented for workflow metadata checks.

## Verification and versioning

New verification reviews must identify a source, reviewer, date, restrictions and
the exact latest record they supersede. Future/backdated supersession and invalid
date ranges are rejected. A historical letter/internal presentation cannot verify
current status. A claimed positive/negative current status requires explicit
source authorization and attached bytes. Demo synthetic records remain
UNVERIFIED_REVIEW_OR_SIMULATED_TEST regardless of their recorded fixture status.
The live source validation/approved scanning path is not configured; no initial
record can become genuinely current-verified through this demo UI.

The internal current-status function honors explicit validity ranges. With no
range, verification proves status as of the recorded date only, not indefinitely.
No expiry date or arbitrary freshness period is fabricated. The evaluation date
is included in the registry hash so date-sensitive evidence becomes stale when
appropriate. This currently uses the server's calendar date, exposed in the frozen
assessment; deployment timezone policy is a future production setting.

The limited versioned evidence policy is stored in the database. It fixes missing
essential evidence, mismatches and unlisted historical records at INSUFFICIENT
DATA. A designated engineer may choose INSUFFICIENT DATA or CONDITIONAL GO for
unresolved Omega design-deviation review, with recorded rationale. This cannot
turn missing current approval into GO or override independent engineering rules.
No live current-authority approval blocking rule is configured, so this module
cannot independently emit NO-GO. Actual definitive exclusion needs approved,
current authority and a separate controlled rule implementation.

## Existing decision aggregation and reporting

The existing per-tag engine combines independent synthetic engineering results
with these approval findings: approved definitive hard stop → NO-GO; essential
unknown/conflict → INSUFFICIENT DATA; defined condition → CONDITIONAL GO; all
positively supported preliminary checks → GO. Overall mixed-package aggregation
is unchanged. Commercial assessment remains independent. A historical match alone
never yields GO; missing verification alone never yields NO-GO.

Every new Aramco evaluation embeds profile, item assignments, exact commodity and
mapping metadata, source references, verification history used, policy version,
registry hash and final check results. HTML/JSON/CSV exports use that frozen
snapshot. Later registry/policy/source/date changes mark the run stale for current
adjudication or quotation; its old exports remain identical and downloadable.
Other-customer and legacy evaluations retain their existing workflow and reports.
