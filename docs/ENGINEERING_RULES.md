# Rule and decision contracts

The UI/backend allowlisted rule schema supports `range` on canonical numeric units, `enum_in` on text, and `present` for explicit completeness checks. No eval/SQL/LLM executable logic is accepted. Bounds must be finite and ordered; missing thresholds/enums and unsupported fields fail validation. Pressure comparisons require an explicit rule basis matching accepted requirement evidence. Empty values remain missing. No pressure-to-head or compatibility value is guessed.

Only `synthetic-demo-v2` publication is available. The eight inherited training rules are explicitly fictional; they do not originate from KSB standards/capabilities. All additional rules start DRAFT, include source, category, scope, applicability selectors, severity, effective date, version and content hash, and require designated engineering_approval permission. Draft/inactive required checks are NOT VERIFIED and prevent GO. Approved versions cannot be edited through API; new versions preserve old snapshots. Approval records are demonstration governance, not corporate authorization.

Rule results retain compliance status, tag/category, raw/normalized fact references, source spans, exact threshold/condition, capability evidence separately from rule authority, severity, version/hash, uncertainty, clarification and decision impact. A supplied standard clause identifier is not treated as a verified full standard: explicit standard requirements remain NOT VERIFIED until actual authorized coverage exists.

Statuses: COMPLIANT, NON-COMPLIANT, DEVIATION, NOT APPLICABLE, NOT VERIFIED, MISSING INFORMATION, CONFLICTING INFORMATION, REQUIRES ENGINEERING REVIEW. Extraction acceptance alone never proves equipment compliance.

Ordered decision: explicit engineer-reviewed value matching an approved non-waivable project prohibition → NO-GO (keep other unknowns visible); otherwise any critical missing/conflicting/unreviewed/coverage/rule/capability issue → INSUFFICIENT DATA; otherwise explicit waivable deviations → CONDITIONAL GO; otherwise positive minimum synthetic screening coverage → GO. The latter is not a hydraulic selection claim. A candidate check failure cannot prove complete portfolio exclusion, so it cannot independently produce tag NO-GO. No approved exhaustive alternative search is implemented.

Complete-package rollup: NO-GO, then INSUFFICIENT DATA, then CONDITIONAL GO, then GO. Mixed packages are evaluated by each tag's product category; pump policy is not applied to valves/parts. Without product-specific approved coverage, valve/parts results abstain. Selection/price/commercial attractiveness never unlocks a technical prohibition.

Engineering disposition can acknowledge/decline/request clarification/return for correction, or record a justified conservative requested outcome. Favorable free-text overrides are rejected; changed evidence/approved rules must be evaluated in a new run. Computed results are never overwritten.
