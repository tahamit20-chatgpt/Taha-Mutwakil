# CODEX IMPLEMENTATION PROMPT
## BidFit 2.0 — Saudi Aramco 9COM Approval Registry & KSB Product Portfolio Integration

**Project:** KSB Arabia – BidFit 2.0  
**Development Package:** Aramco Approval Intelligence  
**Priority:** P0 – High Priority  
**Implementation Type:** Upgrade the existing working application  
**Primary Objective:** Integrate verified Saudi Aramco 9COM approval records with KSB's product portfolio, engineering standards registry, RFQ evaluation, and Bid/No-Bid decision engine.

---

# 1. MISSION

You are working in the existing BidFit 2.0 GitHub repository.

BidFit is a standalone AI-powered engineering bidding platform supporting:

1. RFQ creation and classification.
2. Market segment and application selection.
3. RFQ document uploading.
4. Intelligent RFQ understanding.
5. Standards identification.
6. Technical compliance evaluation.
7. Explainable Bid/No-Bid decisions.
8. Future product selection, pricing, and quotation workflows.

The existing application has already been developed and tested.

**DO NOT rebuild the application from scratch.**

Your assignment is to integrate an official customer approval reference and an internal KSB product mapping into the existing system.

The implementation must introduce real database records, executable validation logic, user interface components, and automated tests.

This is not simply a documentation or visual design task.

---

# 2. SOURCE DOCUMENTS

Two documents support this implementation.

## Source A — Official Saudi Aramco Approval Letter

**Filename:** `Aramco Approval Notification Letter for KSB Pumps Arabia Ltd..pdf`

Issuer: Saudi Arabian Oil Company  
Department: Supplier Relationship Management  
Reference: SQU-26-24  
Date: 1 April 2024

Approved company:

**KSB Pumps Arabia Ltd.**

Vendor Code: `10066368`

Plant ID: `30008606`

The letter confirms that the company was included in Saudi Aramco's Supplier Information System for seven commodity classifications, subject to continued compliance with applicable requirements.

This document is the authoritative historical evidence for the seven listed 9COM classifications and the associated vendor and plant identifiers.

It does not establish the current live status of the approvals as of 2026.

## Source B — KSB Arabia Product Portfolio Presentation

**Filename:** `KSB PA main persentation 2026.pptx`

Relevant sections:

- Slide 1: Approved 9COM Categories.
- Slide 2: Approved Horizontal Pump Product Portfolio.
- Slide 3: Approved Vertically Suspended and Vertical Inline Product Portfolio.

This presentation maps KSB pump product series to Aramco 9COM codes and applicable design standards.

The internal presentation is supporting evidence for the product-series mapping.

It is not a substitute for an official current customer approval certificate.

**IMPORTANT:** If these files are attached and accessible, inspect them and reconcile their contents with the structured records below. Do not invent additional approvals.

---

# 3. OFFICIAL SAUDI ARAMCO APPROVED 9COM CATEGORIES

Create the initial historical approval records exactly as follows:

| 9COM Code | Official Approved Commodity Description |
|---|---|
| 6000002283 | PUMP; CENTRIFUGAL; GENERAL SERVICE; HORIZONTAL |
| 6000002288 | PUMP; CENTRIFUGAL; VERTICALLY SUSPENDED |
| 6000002346 | PUMP; CENTRIFUGAL; GENERAL SERVICE; VERTICAL |
| 6000002350 | PUMP; CENT, HORIZ, ASMEB73.1 OR ISO5199 |
| 6000002355 | PUMP; CENTRIFUGAL; MAIN FIREWATER; HORIZONTAL |
| 6000002356 | PUMP; CENTRIFUGAL; END SUCTION; SINGLE STAGE |
| 6000011675 | RE-ENGINEERED MACHINED OR WELDED PARTS |

All seven records must be linked to:

- Customer: Saudi Aramco.
- Vendor Code: 10066368.
- Plant ID: 30008606.
- Original Approval Date: 2024-04-01.
- Original Source Reference: SQU-26-24.
- Historical approval evidence: Confirmed by uploaded letter.
- Current approval status: Verification Required, unless separately confirmed through an authorized current source.

Do not infer that every product model, configuration, or material is automatically covered by the commodity approval.

Do not generate or invent additional 9COM codes.

---

# 4. KSB PUMP PRODUCT-TO-9COM MAPPING

Create the following structured initial product-series mapping based on the KSB presentation.

| KSB Product Series | Pump Classification | 9COM Code | Industry / Design Standard |
|---|---|---|---|
| MegaCPK | OH1 – Horizontal Foot-Mounted, Radially Split | 6000002350 | ISO 2858 / ISO 5199 |
| Etanorm | Horizontal General Service | 6000002283 | HI / EN 733 |
| RPH | OH2 – Horizontal Centerline-Mounted, Radially Split | 6000002356 | API 610 / ISO 13709 |
| Omega | BB1 – Axially Split | 6000002355 | HI; BB1 with deviations from API 610 |
| WKB | VS1 – Vertically Suspended | 6000002288 | API 610 / ISO 13709 |
| RPH-V | VS4 – Vertically Suspended Sump Pump | 6000002288 | API 610 / ISO 13709 |
| WKTR | VS6 – Double-Casing Vertically Suspended | 6000002288 | API 610 / ISO 13709 |
| Movitec | Vertical Inline Multistage | 6000002346 | Manufacturer Standard |

Also create the separate commodity record:

- Commodity: Re-engineered Machined or Welded Parts.
- 9COM: 6000011675.
- Product classification: Re-engineering / Parts.
- No automatic specific pump model association.

## Important Engineering Clarifications

### 4.1 One 9COM Can Cover Multiple Product Series

The following product series share 9COM `6000002288`:

- WKB — VS1.
- RPH-V — VS4.
- WKTR — VS6.

The database must support this relationship.

Do not enforce a one-to-one relationship between a 9COM code and a pump series.

Prefer normalized relational records or a configurable mapping table, allowing future extensions and appropriate multi-entity associations.

### 4.2 Approval Does Not Equal Technical Compliance

A product's presence under an approved commodity code does not automatically mean:

- The requested duty point is achievable.
- The pump conforms to every required engineering standard.
- The requested materials are available.
- The specific configuration is approved.
- The product is currently available for manufacture.
- The pump is commercially competitive.
- The manufacturer is approved for every requested condition.

These must remain separate checks.

### 4.3 Special Attention — Omega

The presentation describes Omega as a BB1 design with deviations from API 610.

Therefore:

**Never automatically classify Omega as fully API 610 compliant merely because of its BB1 classification or approved firewater 9COM mapping.**

The specific application and applicable standard requirements must be evaluated independently.

### 4.4 Product Mapping and Approval Evidence Are Separate

Maintain traceability to both:

- Official historical approval evidence.
- Internal product-to-commodity mapping evidence.

Where current approval verification or configuration-specific evidence is missing, the system must clearly communicate this limitation.

---

# 5. DATABASE DESIGN

Inspect the existing database schema first.

Reuse appropriate entities where available.

Avoid duplicate or conflicting master records.

Create or extend the following logical entities.

## 5.1 Customer Approval Profile

Suggested fields:

- id
- customer_id
- customer_name
- vendor_code
- plant_id
- manufacturer_name
- manufacturing_location
- approval_authority
- original_approval_date
- original_reference
- current_verification_status
- last_verified_at
- verified_by
- notes

## 5.2 Approval Commodity

Suggested fields:

- id
- approval_profile_id
- commodity_code
- commodity_description
- product_category
- approval_source
- source_revision
- original_approval_date
- current_status
- verification_required
- valid_from
- valid_until
- supporting_document_id
- last_verified_at
- updated_at

Do not invent validity or expiry dates.

If the approval document does not specify an expiration date, store NULL or equivalent.

## 5.3 Product Series

Suggested fields:

- id
- product_series_name
- product_category
- pump_design_type
- api_pump_classification
- configuration
- description
- primary_design_standard
- manufacturing_reference
- engineering_verification_status

## 5.4 Product-to-Approval Mapping

Suggested fields:

- id
- product_series_id
- approval_commodity_id
- customer_approval_profile_id
- applicable_plant_id
- supporting_reference
- mapping_source_document
- mapping_source_slide
- mapping_verification_status
- engineering_notes
- created_at
- updated_at

## 5.5 Approval Verification Record

Suggested fields:

- id
- approval_commodity_id
- verified_status
- verification_date
- verification_source
- source_document_id
- reviewed_by
- reviewer_notes
- supersedes_verification_id

Preserve historical verification records rather than overwriting them.

## 5.6 Engineering Evaluation Result

Extend the existing RFQ evaluation structure to store:

- rfq_id
- equipment_tag_id
- customer_id
- product_series_id
- required_9com
- matched_9com
- relevant_plant_id
- historical_approval_evidence
- current_approval_verification
- technical_compliance_status
- supporting_references
- decision_impact
- required_action

All identifiers, particularly 9COM, Vendor Code, and Plant ID, must be stored as strings to preserve their exact representation.

---

# 6. INTEGRATION WITH THE EXISTING RFQ WORKFLOW

The new functionality must be integrated into BidFit's approved functional architecture.

## STEP 1 — RFQ Classification

When the user creates a new RFQ, the existing classification flow must remain unchanged:

1. Product Category.
2. Market Segment.
3. Application.
4. Customer / End User.

If the selected customer is Saudi Aramco, activate the Aramco Approval Evaluation capability.

If the RFQ concerns another customer, do not incorrectly apply Aramco approvals as universal technical requirements.

## STEP 2 — RFQ Upload

Preserve the current document uploading and classification functionality.

The system should attempt to identify:

- Requested pump type.
- Required standard.
- Equipment tag.
- Customer-required 9COM code, if explicitly stated.
- Manufacturer approval requirements.
- Product configuration.

Do not invent a requested 9COM if it is absent.

The system may suggest a potential classification based on available mapping records, but this must be labelled as an inferred candidate requiring verification.

## STEP 3 — Intelligent RFQ Summary

Expand the summary to show an approval-related section where relevant.

Suggested interface:

**Saudi Aramco Approval Requirements**

- Customer: Saudi Aramco.
- Required Equipment Type.
- Required 9COM: Extracted or Not Specified.
- Candidate KSB Product Series.
- Associated 9COM.
- Vendor Code.
- Plant ID.
- Historical Approval Evidence.
- Current Approval Verification Status.
- Engineering Action Required.

Allow the engineer to review classification suggestions.

## STEP 4 — Standards Identification

Connect approved product mapping with the existing Standards Registry.

Examples:

MegaCPK:
- ISO 5199.
- ISO 2858.

RPH:
- API 610.
- ISO 13709.

WKB, RPH-V, and WKTR:
- API 610.
- ISO 13709.

Etanorm:
- HI / EN 733 reference category.

Movitec:
- Manufacturer Standard.

Omega:
- HI reference and an explicit requirement to review deviations when API 610 applies.

These are product-design references from the KSB presentation.

Do not automatically declare them to be the applicable contractual standard for every RFQ.

The actual customer specifications and application must determine contractual applicability.

## STEP 5 — Technical Compliance

Add an approval verification section to the existing Compliance Matrix.

Suggested checks:

| Check ID | Check | Expected Outcome |
|---|---|---|
| ARAMCO-001 | Is the customer Saudi Aramco? | Applicable / Not Applicable |
| ARAMCO-002 | Does the RFQ explicitly require a 9COM classification? | Identified / Missing |
| ARAMCO-003 | Is the requested 9COM listed in the historical official approval letter? | Listed / Not Listed |
| ARAMCO-004 | Is the candidate product series associated with that 9COM in the internal portfolio mapping? | Matched / Not Matched / Unknown |
| ARAMCO-005 | Is the vendor code consistent with the approval profile? | Match / Mismatch |
| ARAMCO-006 | Is the proposed plant consistent with the approved plant reference? | Match / Mismatch / Unknown |
| ARAMCO-007 | Has current approval status been verified using an authorized source? | Verified / Requires Verification |
| ARAMCO-008 | Is the proposed product technically suitable for the RFQ? | Evaluated Separately |
| ARAMCO-009 | Are customer standards and deviations addressed? | Evaluated Separately |
| ARAMCO-010 | Are applicable component supplier/9CAT approvals confirmed? | Verified / Pending / Not Applicable |

These checks must be implemented with explicit logic.

Avoid generating unsupported eligibility claims using only LLM text generation.

## STEP 6 — Bid/No-Bid Decision

Approval verification results must contribute to the technical decision.

However:

**A historical 9COM match must never automatically produce GO.**

**A missing current verification must not automatically produce NO-GO.**

**A product not listed under the historical approval evidence does not automatically prove that the product is unapproved today.**

Use:

- GO, when the overall approved rules and verified evidence support preliminary eligibility.
- CONDITIONAL GO, when defined conditions require confirmation or an accepted deviation.
- NO-GO, only when a definitive blocking condition is supported by current, authoritative evidence and an approved rule.
- INSUFFICIENT DATA, where essential eligibility evidence is missing.

The approval module must provide its own detailed status and evidence.

The existing decision aggregation engine should determine how that status affects the RFQ decision, based on approved rules.

---

# 7. USER INTERFACE REQUIREMENTS

Use the existing BidFit 2.0 interface and KSB blue/grey design system.

Do not redesign the entire application.

Add the following features.

## 7.1 Aramco Approval Registry

Accessible through:

**Knowledge Library → Customer Approvals → Saudi Aramco**

Display:

- Vendor Code.
- Plant ID.
- Approval Letter Reference.
- Original Approval Date.
- List of approved commodity codes.
- Product series associated with each code.
- Current verification status.
- Supporting documents.

Support filtering by:

- Product Category.
- Pump Classification.
- 9COM Code.
- Product Series.
- Approval Status.

## 7.2 Product Portfolio Mapping

Add a management view:

**Product Library → KSB Product Series**

Each product-series profile should display:

- Product Name.
- Design Classification.
- Associated 9COM.
- Relevant Standards.
- Manufacturing Reference.
- Approval Evidence.
- Engineering Verification Status.

Support multiple series under one commodity code.

## 7.3 RFQ Approval Status

Inside each Saudi Aramco RFQ, display a compact approval evaluation section.

Example:

**Aramco Supplier Approval**

- Product: RPH.
- Design Type: OH2.
- Suggested 9COM: 6000002356.
- Vendor Code: 10066368.
- Plant ID: 30008606.
- Historical Listing: Confirmed by SQU-26-24.
- Current Verification: Required.
- Final Technical Compliance: Separate evaluation.

This is an example of displaying database references, not a claim of current approval for a new RFQ.

## 7.4 Approval Evidence Details

Users must be able to inspect the evidence used for each approval-related finding.

Where available, show:

- Source document title.
- Reference number.
- Date.
- Page or slide.
- Relevant product.
- Commodity code.
- Verification status.

Do not copy full protected documents into a publicly exposed page.

---

# 8. ADMINISTRATION & FUTURE UPDATES

Approvals can change.

The system must not depend on hardcoded approval lists that require source-code changes for routine updates.

Authorized administrators should eventually be able to:

1. Add a new approval document.
2. Add or update a commodity classification.
3. Associate product series.
4. Record updated verification evidence.
5. Mark a record as superseded.
6. Record restrictions or conditions.
7. Manage approval evidence and validity information.
8. Review approval history.

For the current implementation, provide an appropriate minimal working administration function or seedable management interface consistent with the existing architecture.

Do not automatically overwrite older approval records.

Maintain an audit trail of changes.

---

# 9. REQUIRED AUTOMATED TESTS

Implement tests covering the following scenarios.

### Test 1 — Approved Historical Commodity Match

Customer: Saudi Aramco.  
Candidate Product: RPH.  
Required 9COM: 6000002356.

Expected:

- Historical commodity listing found.
- RPH product mapping found.
- Correct vendor code and plant ID displayed.
- Current status not falsely marked verified.
- Overall RFQ decision not automatically set to GO.

### Test 2 — Multiple Series Under One 9COM

Search for `6000002288`.

Expected product series:

- WKB.
- RPH-V.
- WKTR.

### Test 3 — ISO Pump Mapping

Candidate Product: MegaCPK.

Expected:

- 9COM 6000002350.
- ISO 5199 and ISO 2858 as design references.
- No automatic ISO compliance certification without actual evaluation.

### Test 4 — Firewater Pump with Deviations

Candidate Product: Omega.

Expected:

- 9COM 6000002355.
- Historical classification evidence found.
- API 610 full compliance not assumed.
- Engineering deviations flagged when relevant.

### Test 5 — Unlisted Historical Commodity

Customer RFQ requires a commodity code that does not appear in the 2024 letter.

Expected:

- Not Listed in Available Historical Evidence.
- Current approval verification requested.
- No unsupported automatic NO-GO.

### Test 6 — Another Customer

Customer: Saudi Water Authority.

Expected:

- Saudi Aramco approval rules are not applied automatically.
- Other relevant customer standards and approval profiles remain available.

### Test 7 — Mixed Product RFQ

RFQ contains pumps, valves, and spare parts.

Expected:

- Separate item-level evaluations.
- Pump approval mappings not incorrectly applied to valves.
- Re-engineered parts category evaluated separately.

### Test 8 — Existing RFQ Regression

All previously functional RFQ creation, uploading, history, and analysis operations must continue to work.

### Test 9 — Authorization

An unauthorized user cannot modify customer approval records.

### Test 10 — Historical Revision

When a newer approval document is added:

- Historical records are preserved.
- Current verification status may be updated through an authorized workflow.
- Previous RFQ evaluations remain traceable to their original evidence and rule versions.

---

# 10. IMPLEMENTATION PLAN

## Stage A — Inspect Existing Repository

Before modifying code:

- Inspect the frontend and backend.
- Identify existing customer records.
- Identify product library structures.
- Identify compliance rule definitions.
- Identify standards registry structures.
- Identify the RFQ decision engine.
- Identify existing migrations and tests.

Do not duplicate functioning modules unnecessarily.

## Stage B — Add Database Models and Migrations

Implement or extend:

- Customer Approval Profile.
- Commodity Approval Records.
- Product-to-9COM Mapping.
- Approval Verification History.
- RFQ Approval Evaluation Results.

Ensure migrations preserve existing data.

## Stage C — Seed Initial Records

Seed the seven official 9COM classifications and eight KSB pump-series mappings.

Use an idempotent import or seed process.

Do not duplicate entries when the seed command is run more than once.

Use source metadata and clear historical verification status.

## Stage D — Build APIs and Business Logic

Implement:

- Approval lookup.
- Product-series lookup.
- 9COM mapping.
- Customer eligibility evaluation.
- Evidence retrieval.
- Verification status management.

Integrate with existing server-side authorization.

## Stage E — Build UI Components

Implement:

- Aramco Approval Registry.
- Product approval details.
- RFQ approval assessment section.
- Compliance Matrix integration.
- Approval-related explanations.

Use the current KSB-themed components.

## Stage F — Integrate with Bid/No-Bid

Connect approval findings to existing decision aggregation using configurable, explainable rules.

Do not bypass the existing technical compliance process.

## Stage G — Test and Validate

Run relevant tests.

Fix integration problems.

Verify backward compatibility.

Document any remaining uncertainty.

---

# 11. DOCUMENTATION

Update or create the following documentation according to repository conventions:

- `docs/ARAMCO_9COM_APPROVAL_REGISTRY.md`
- `docs/KSB_PRODUCT_9COM_MAPPING.md`
- `docs/APPROVAL_VERIFICATION_LOGIC.md`
- `docs/APPROVAL_DATA_PROVENANCE.md`
- `docs/TEST_EVIDENCE.md`

Document:

- Source references.
- Initial 9COM mapping.
- Database relationships.
- Approval verification limitations.
- Decision logic.
- How administrators can add updated approvals.
- How RFQs consume the approval registry.

---

# 12. SECURITY & DATA GOVERNANCE

Use the existing authentication and authorization architecture.

At minimum:

- Restrict modification of approval records.
- Preserve audit logs.
- Protect uploaded supporting documents.
- Avoid exposing protected files publicly.
- Do not expose credentials or AI API secrets.
- Maintain document source traceability.
- Prevent cross-user unauthorized access.

Keep the approval evidence accessible only through authorized application functions.

If source files are not already present in the repository, do not fabricate file paths or claim they were imported.

Use the structured data in this prompt to create initial records and mark supporting document attachments as pending until actually provided.

Do not commit sensitive source documents or credentials to a public repository.

---

# 13. REQUIRED IMPLEMENTATION REPORT

After implementation, provide:

1. Summary of code changes.
2. Files created or modified.
3. Database migrations.
4. Initial 9COM records loaded.
5. Product-series mappings loaded.
6. User interface additions.
7. RFQ evaluation integration status.
8. Automated test results.
9. Unresolved engineering dependencies.
10. Next recommended development task.

Distinguish clearly between implemented functionality and planned work.

Do not claim that engineering approval is verified merely because the initial records have been loaded.

---

# 14. FINAL INSTRUCTION

**START IMPLEMENTATION NOW IN THE EXISTING BIDFIT 2.0 REPOSITORY.**

Your immediate objective is to transform the Saudi Aramco approval letter and KSB product portfolio mapping into a functional, evidence-based customer approval capability.

The expected result is:

**RFQ → Customer Identification → Product Classification → 9COM Matching → Vendor/Plant Verification → Standards & Technical Compliance → Explainable Bid/No-Bid Recommendation**

All results must be traceable, auditable, and clearly distinguish historical approval evidence from current verification.

Preserve the existing RFQ workflow, database compatibility, authentication, and KSB visual identity.

Implement, test, and report what actually works.

Do not rebuild the platform.

Do not generate fake approvals.

Do not assume that a listed commodity automatically guarantees technical compliance.

**Proceed.**
