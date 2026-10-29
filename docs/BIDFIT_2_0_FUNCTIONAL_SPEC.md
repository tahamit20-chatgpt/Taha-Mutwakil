# MASTER IMPLEMENTATION PROMPT
## KSB Arabia — BidFit 2.0
### End-to-End Intelligent RFQ Evaluation, Engineering Selection & Quotation Platform

**MISSION: UPGRADE THE EXISTING APPLICATION — DO NOT REBUILD FROM SCRATCH**

You are working inside an existing GitHub-connected software project that has already been developed and launched as a functional prototype.

The existing application is called **BidFit**, previously referred to as the AI RFQ Accelerator / RFQ Analyzer.

The application currently supports at least some of the following capabilities:

- Web-based access.
- User authentication.
- Dashboard and navigation.
- New RFQ creation.
- RFQ document uploading.
- AI-assisted document analysis.
- Preliminary Bid/No-Bid results.

These features have been tested by the project owner and some are already functional.

**Your task is to upgrade the existing project to BidFit 2.0 while preserving what already works.**

Do not assume any existing feature is functional merely because it is listed here. Inspect and verify the repository first.

Do not create an unrelated new project or replace the existing application unnecessarily.

Work directly within the existing repository and its established development environment.

---

# 1. YOUR ROLE

Act as a combined:

1. Principal Software Architect.
2. Senior Full-Stack Engineer.
3. AI Engineering Systems Architect.
4. Industrial Pump Application Engineering Domain Specialist.
5. Product Manager for Engineering Workflow Applications.
6. Quality Assurance and Test Automation Engineer.
7. User Experience and Interface Designer.

Your objective is to convert the existing functional prototype into a structured, extensible, engineering-focused bidding platform.

This is a real application development assignment, not merely a design exercise.

**You are expected to inspect, implement, test, and demonstrate working code.**

Do not stop after producing a conceptual document or wireframe.

---

# 2. CRITICAL PROJECT RULES

Follow these principles throughout implementation.

### Rule 1 — Preserve the existing application

- Inspect the current codebase before making changes.
- Identify the existing frontend, backend, database, authentication, AI services, and upload mechanisms.
- Preserve existing working features.
- Reuse established architectural patterns.
- Avoid unnecessary migrations or technology replacements.
- Maintain compatibility with existing RFQ records wherever possible.

### Rule 2 — Implement incrementally

Develop in small, testable steps.

Each major function should work before moving to the next.

Use meaningful commits or clearly separated implementation stages.

### Rule 3 — Use real functionality

Do not create decorative buttons, fake analyses, simulated successes, or nonfunctional screens presented as complete.

When a future feature is not implemented, show a clear status such as:

- Not Available Yet
- Pending Engineering Data
- Requires Configuration
- Under Development

Clearly identify demonstrations that use synthetic data.

### Rule 4 — Separate engineering logic from AI interpretation

Use generative AI for:

- Document understanding.
- Requirement extraction.
- Classification.
- Summarization.
- Identification of possible conflicts.
- Drafting explanations and clarifications.

Use deterministic, independently testable logic for:

- Unit conversion.
- Numerical calculations.
- Standards checks based on approved rules.
- Engineering thresholds.
- Technical pass/fail decisions.
- Final decision aggregation.

Never allow the language model to invent technical values or claim engineering compliance without supporting evidence.

### Rule 5 — Prioritize Bid/No-Bid

The immediate priority is:

**A functional, explainable, evidence-based RFQ qualification and Bid/No-Bid workflow.**

Advanced pump selection, pricing, and quotation automation must not delay this objective.

### Rule 6 — Maintain modularity

Future modules must integrate into the same application without requiring a complete rewrite.

### Rule 7 — Engineering authorization

All engineering recommendations are preliminary until reviewed by an authorized engineer.

### Rule 8 — Protect sensitive information

The project owner reports receiving verbal permission to investigate relevant tools and documents, with written confirmations being obtained.

Treat specific access, copying, extraction, redistribution, and AI-processing permissions as requiring confirmation of their actual scope.

Proceed immediately with application architecture, interfaces, generic logic, and synthetic test data.

Do not upload or transfer confidential customer materials or licensed standards to new external services until the relevant rights and permissions are verified.

Do not circumvent access controls or extract restricted source code.

---

# 3. PROJECT VISION

BidFit 2.0 will become an:

**End-to-End Intelligent Sales Engineering & Bidding Platform.**

The application must support a complete commercial and engineering workflow:

1. New RFQ Creation.
2. Product and Application Classification.
3. RFQ Document Upload.
4. Intelligent RFQ Understanding and Summary.
5. Standards Identification.
6. Engineering Compliance Analysis.
7. Technical Bid/No-Bid Evaluation.
8. Commercial and Strategic Bid Qualification.
9. Intelligent Product Selection.
10. Costing and Pricing.
11. Technical and Commercial Quotation Generation.
12. Approval, Submission, Revisions, and Bid Follow-Up.
13. Historical Knowledge and Continuous Improvement.

These functions must exist within one coherent RFQ workspace.

**Core principle: One RFQ. One Workspace. One Continuous Workflow.**

Information extracted during an early stage must remain available to subsequent stages without unnecessary re-entry.

---

# 4. REQUIRED APPLICATION STRUCTURE

The application must retain or develop a secure authentication screen followed by a main dashboard.

## 4.1 Login Screen

Support:

- Username or email.
- Password.
- Secure session management.
- Logout.
- Role-aware access.

Use the existing authentication implementation if secure and functional.

Do not introduce unnecessary authentication dependencies.

## 4.2 Main Dashboard

The dashboard should provide:

- New RFQ.
- RFQ History / My RFQs.
- All RFQs, according to permissions.
- Knowledge Library.
- Standards Library.
- Product Library.
- Reports and Analytics.
- Administration / Settings, according to role.

Display relevant RFQ information:

- RFQ reference.
- Project name.
- Customer.
- Product category.
- Market segment.
- Current workflow stage.
- Bid status.
- Assigned engineer.
- Last updated.
- Submission deadline, when available.

## 4.3 RFQ Workspace

Each RFQ should have a persistent workspace.

Suggested layout:

**Left Sidebar**

- Dashboard.
- New RFQ.
- RFQ History.
- Knowledge Library.
- Standards Registry.
- Product Library.
- Analytics.

**Main Content Area**

The current RFQ and its workflow.

**Top Area**

Project name, customer, RFQ reference, current status, last saved date, and assigned owner.

**Workflow Navigation**

A horizontal or vertical stepper showing the stages of the RFQ lifecycle.

The user must be able to navigate backward and forward among permitted stages without losing data.

Downstream stages must be marked as incomplete or requiring review where necessary.

---

# 5. STEP 1 — PRODUCT & APPLICATION CLASSIFICATION

**THIS CLASSIFICATION FRAMEWORK HAS ALREADY BEEN APPROVED BY THE PROJECT OWNER. PRESERVE IT.**

Before document uploading, the system should guide the user through initial classification.

## 5.1 Product Category

Ask:

**What are you quoting?**

Options:

1. Pump / Pump Set.
2. Valve.
3. Spare Parts.
4. Mixed Package.

Do not treat mixed packages as a single pump.

A mixed RFQ may include multiple equipment categories, each requiring different evaluation logic.

## 5.2 Market Segment

The system must support the following six KSB market areas:

1. Water.
2. Energy.
3. Mining.
4. General Industry.
5. Building Services.
6. Petrochemicals / Chemicals.

Use these as configurable master data.

## 5.3 Application Subcategories

Once a market segment is selected, display corresponding application choices.

Use the following initial structure.

### Water

- Desalination.
- Water Supply.
- Wastewater.
- Water Treatment.
- Water Distribution.
- Other / To Be Determined.

### Energy

- Power Generation.
- Cooling Water Systems.
- Auxiliary Systems.
- Other / To Be Determined.

### Mining

- Slurry Handling.
- Non-Slurry Applications.
- Dewatering.
- Process Water.
- Other / To Be Determined.

### General Industry

- Industrial Process.
- Plant Utilities.
- Cooling and Circulation.
- Other / To Be Determined.

### Building Services

- HVAC.
- Fire Protection.
- Building Water Supply.
- Pressure Boosting.
- Drainage.
- Other / To Be Determined.

### Petrochemicals / Chemicals

- Oil & Gas.
- Chemical Processing.
- Refining.
- Petrochemical Processing.
- Other / To Be Determined.

These application choices are an initial configurable classification, not a final claim about the official KSB application taxonomy.

The classification must be editable through configuration rather than hardcoded throughout the application.

## 5.4 Customer / End User

Provide fields for:

- Customer Name.
- End User.
- EPC / Contractor.
- Project Name.
- Project Location.
- Country.
- RFQ Reference.
- Submission Deadline.

Provide optional customer profiles, including:

- Saudi Aramco.
- Saudi Water Authority.
- Saudi Electricity Company.
- Ma'aden.
- Other / General Customer.

The customer list must be extensible.

## 5.5 Classification Logic

The initial product, segment, application, and customer classification should guide the standards and rules that the system proposes.

However:

**Never determine mandatory engineering standards using the market segment alone.**

Standards applicability must consider:

- Product type.
- Application.
- Customer requirements.
- RFQ specifications.
- Required standard edition.
- Applicable contract documentation.
- Engineering approval.

The system must allow users to verify or correct classification after document extraction.

### Acceptance Criteria

- User can create an RFQ using the classification workflow.
- Product-specific options update correctly.
- Market subcategories are displayed dynamically.
- Customer profile can be selected or entered.
- All selections are saved.
- The RFQ workspace opens successfully.
- Existing RFQs remain accessible.

---

# 6. STEP 2 — RFQ DOCUMENT UPLOAD

Develop or enhance the existing upload functionality.

Support, where practical:

- PDF.
- Excel XLSX.
- Word DOCX.
- Text files.
- Multiple-file upload.
- Drag and drop.
- Additional files after RFQ creation.
- Folder upload where technically supported.
- ZIP upload with safe extraction and clear limits.

Other legacy formats can be added through explicit converters when needed.

## Document Classification

The system should recognize possible document types:

- RFQ / Inquiry.
- Material Requisition.
- Equipment Datasheet.
- Technical Specification.
- Scope of Supply.
- Bill of Quantities.
- P&ID.
- General Arrangement Drawing.
- Hydraulic Calculation.
- Applicable Standards.
- Vendor Requirement List.
- Compliance Sheet.
- Clarification List.
- Commercial Terms.
- Other Attachments.

If document type identification is uncertain, mark it for user confirmation.

## Document Metadata

Capture:

- Original filename.
- File format.
- Upload date.
- Document number.
- Document revision.
- Document category.
- Equipment tags referenced.
- Parsing status.
- Extraction method.
- Source location.

Preserve original files.

Do not overwrite older revisions when a newer document is uploaded.

### Critical Requirement

The user must be able to upload an additional document to an existing RFQ without creating an unrelated new analysis collection.

---

# 7. STEP 3 — INTELLIGENT RFQ UNDERSTANDING

**THIS MUST BE A SEPARATE STAGE FROM THE ENGINEERING DECISION.**

After uploading documents, the system performs initial extraction and generates an editable RFQ summary.

The user must review this information before selecting:

**PROCESS RFQ**

## 7.1 Summary Overview

Display:

- Project name.
- Customer.
- End user.
- Product category.
- Market segment.
- Application.
- Quantity of equipment.
- Applicable equipment tags.
- Identified standards.
- Relevant operating conditions.
- Major documentation requirements.
- Missing information.
- Conflicting information.

## 7.2 Pump-Specific Parameters

Extract where available:

- Tag number.
- Equipment description.
- Quantity.
- Pump type.
- Required flow.
- Required head.
- Differential pressure.
- Suction pressure.
- Discharge pressure.
- NPSHA.
- Pumped liquid.
- Liquid density.
- Viscosity.
- Vapor pressure.
- Operating temperature.
- Design temperature.
- Operating speed.
- Supply frequency.
- Materials of construction.
- Mechanical seal requirements.
- Installation requirements.
- Inspection requirements.
- Applicable design standards.
- Customer approval requirements.

## 7.3 Valve-Specific Parameters

Extract where applicable:

- Valve type.
- Nominal size.
- Pressure class.
- End connections.
- Material specification.
- Operating temperature.
- Process fluid.
- Actuation requirements.
- Applicable testing requirements.
- Applicable product standards.
- Quantity.

## 7.4 Spare Parts Parameters

Extract where applicable:

- Equipment manufacturer.
- Product family.
- Equipment model.
- Equipment serial number, when provided.
- Part number.
- Part description.
- Quantity.
- Required material.
- Revision / compatibility references.
- Availability requirements.

## 7.5 Equipment Tag Register

Create a structured register covering all equipment items within an RFQ.

One RFQ may contain multiple tags and multiple product categories.

Each tag should have its own extracted technical requirements and evaluation results.

## 7.6 Source Traceability

Every extracted parameter must retain:

- Source document.
- Page number or worksheet.
- Original text or source location.
- Original value.
- Normalized value.
- Units.
- Extraction confidence or uncertainty.
- User verification status.

Never invent missing engineering values.

## 7.7 Editable Extraction Review

Users must be able to correct extracted values.

Store both:

- Original extracted value.
- User-corrected value.

Record who made the correction and when.

## 7.8 Output

Display a concise but technically meaningful RFQ Summary.

Avoid verbose or generic AI-generated narratives.

Prominently show:

- Critical technical parameters.
- Missing information.
- Contradictory requirements.
- Equipment quantities.
- Identified document revisions.

The user then clicks:

**PROCESS RFQ**

This action triggers the standards and compliance evaluation stages.

---

# 8. STEP 4 — STANDARDS IDENTIFICATION ENGINE

This is a major functional upgrade.

The existing application must evolve from basic AI summarization into structured standards-based technical evaluation.

## 8.1 Standards Registry

Create a configurable database of standards and engineering rule references.

Initial standards categories may include:

### Pump Standards

- API 610.
- ISO 13709.
- ISO 5199.
- ISO 2858.
- ASME B73.1.

### Mechanical Seal Standards

- API 682.

### Customer and Project Specifications

- Saudi Aramco SAES requirements.
- Saudi Aramco SAMSS requirements.
- Saudi Aramco inspection requirements.
- Saudi Water Authority project-specific requirements.
- Other customer technical specifications.

### Hydraulic Engineering References

- Applicable Hydraulic Institute guidance.
- Approved hydraulic calculation methods.
- Approved engineering operating limits.

### Product-Specific Requirements

- KSB product boundaries.
- Customer approved vendor lists.
- 9COM eligibility.
- Approved manufacturing facilities.
- Material availability.

Do not assume that these standards are applicable to every RFQ.

## 8.2 Standards Applicability Logic

Implement three separate layers.

**Layer A — Suggested Standards**

Determine possible applicable standards based on product type, market, application, and customer.

**Layer B — Explicit RFQ Requirements**

Extract standards and editions stated in the actual customer documentation.

**Layer C — Approved Rule Registry**

Load the applicable engineering checks from the approved, version-controlled rules database.

If there are contradictory standards or editions, flag them for review.

If a standard is unavailable in the approved library, mark it:

**REFERENCE NOT AVAILABLE / REQUIRES REVIEW**

Do not fabricate clause content or declare compliance without an actual approved rule.

## 8.3 Standards Selection Screen

Allow the user to see:

- Identified standard.
- Standard edition.
- Why it was suggested.
- Whether the customer explicitly requested it.
- Applicable equipment tags.
- Availability of approved rules.
- Engineering confirmation status.

Users with appropriate permissions may confirm or change the applicable standards.

---

# 9. STEP 5 — ENGINEERING COMPLIANCE ENGINE

**THIS IS ONE OF THE MOST IMPORTANT COMPONENTS IN BIDFIT 2.0.**

Do not simply ask an LLM to determine whether a document complies with a standard.

Build a structured, evidence-based compliance evaluation engine.

## 9.1 Compliance Matrix

Each evaluation result should contain:

- Criterion ID.
- Product category.
- Equipment tag.
- Requirement description.
- Source document.
- Source page / worksheet.
- Standard reference.
- Standard edition.
- Clause identifier, when verified.
- Customer requirement.
- Extracted parameter.
- Required limit or condition.
- Actual or available capability.
- Evaluation method.
- Evaluation result.
- Supporting evidence.
- Severity.
- Engineering remarks.
- Clarification required.
- Reviewer.
- Approval status.

## 9.2 Evaluation Statuses

Support at least:

- COMPLIANT.
- NON-COMPLIANT.
- DEVIATION.
- NOT APPLICABLE.
- NOT VERIFIED.
- MISSING INFORMATION.
- CONFLICTING INFORMATION.
- REQUIRES ENGINEERING REVIEW.

Distinguish extraction uncertainty from engineering compliance.

A confident extraction is not evidence that a pump satisfies a requirement.

## 9.3 Severity Classification

Support:

- HARD STOP.
- CRITICAL.
- MAJOR.
- MINOR.
- INFORMATIONAL.

Severity must come from approved, configurable rules.

Do not use an LLM's opinion alone to assign a mandatory engineering hard stop.

## 9.4 Initial Engineering Checks

Build a framework for checking:

- Pump category compatibility.
- Pump configuration.
- Hydraulic duty information.
- NPSH requirements.
- BEP operating range requirements.
- Flow-to-BEP ratio.
- Head rise to shutoff.
- Minimum continuous stable flow.
- Temperature limits.
- Pressure limits.
- Material requirements.
- Mechanical seal requirements.
- Required standards.
- Customer approval requirements.
- 9COM requirements.
- Manufacturing capability.
- Required documentation.
- Inspection and testing requirements.

Where authoritative limits or capability information are unavailable, show NOT VERIFIED.

## 9.5 Configurable Rules

Use an approved rule configuration system.

Suggested fields:

- rule_id.
- rule_name.
- product_type.
- market_area.
- application.
- standard_id.
- standard_edition.
- clause_reference.
- input_parameters.
- operator.
- threshold.
- units.
- severity.
- applicability_conditions.
- decision_impact.
- source_reference.
- effective_date.
- approval_status.
- approved_by.
- version.

Only approved rules may generate definitive automated compliance findings.

Use deterministic code for numerical evaluation and applicability logic.

## 9.6 Detailed Findings Interface

Every result row should be expandable.

The expanded view must explain:

**What the customer requested.**

**Which standard or approved rule applies.**

**What evidence is available.**

**How the result was calculated or determined.**

**Whether additional engineering review is required.**

A user must never see a simple "API 610 Passed" claim without supporting clause-level or rule-level evidence.

---

# 10. STEP 6 — TECHNICAL BID/NO-BID DECISION

After the compliance evaluation, aggregate results into an explainable technical recommendation.

Support four primary outcomes:

### GO

Initial technical evidence supports proceeding with quotation preparation, subject to normal engineering approvals.

### CONDITIONAL GO

Potentially feasible, but some conditions require:

- Customer clarification.
- Engineering approval.
- Deviation acceptance.
- Additional product information.
- Confirmation of manufacturing capability.

### NO-GO

A confirmed mandatory constraint blocks the offer under an approved rule.

### INSUFFICIENT DATA

There is not enough reliable evidence to establish technical feasibility.

**Do not classify missing information as an automatic NO-GO.**

**Do not classify lack of detected contradictions as an automatic GO.**

## 10.1 Decision Report

Display:

- Overall technical recommendation.
- Decision justification.
- Critical requirements.
- Hard stops.
- Technical deviations.
- Missing information.
- Required clarifications.
- Source documents.
- Rule versions.
- Equipment-tag-specific results.
- Engineering review status.

## 10.2 Commercial and Strategic Assessment

Support a separate business evaluation using a configurable GOAL framework.

Potential assessment dimensions:

- Strategic attractiveness.
- Customer relationship.
- Likelihood of success.
- Opportunity size.
- Competitive positioning.
- Resource requirements.
- Commercial feasibility.
- Bid effort.

Do not mix commercial attractiveness and technical eligibility into a single unexplained score.

The business evaluation may influence the management-level bidding decision but must not override a confirmed technical hard stop.

## 10.3 Engineering Approval

Allow authorized users to:

- Accept.
- Reject.
- Request clarification.
- Override with justification.
- Return for correction.

Maintain an audit trail.

---

# 11. STEP 7 — BIDFIT SELECTION STUDIO

Implement the initial architecture and workflow screens now.

Do not delay Phase 1 waiting for a complete EasySelect analysis.

The detailed hydraulic selection engine will be expanded later.

## 11.1 Selection Studio Objective

Use previously extracted RFQ information to support intelligent product selection.

The selection workflow should be different for:

- Pumps.
- Valves.
- Spare Parts.

## 11.2 Pump Selection

Expected future inputs:

- Duty point.
- Liquid properties.
- Temperature.
- Required pump design.
- Installation conditions.
- Frequency.
- Materials.
- Applicable standards.
- Operating range.
- NPSH conditions.
- Approved product references.

Expected future outputs:

- Candidate pump families.
- Candidate models.
- Hydraulic performance references.
- Operating range compatibility.
- Efficiency.
- Power.
- Materials compatibility.
- Compliance findings.
- Technical deviations.
- Engineering selection status.

## 11.3 Valve Selection

Prepare the workflow for:

- Type.
- Size.
- Pressure class.
- Material.
- Fluid service.
- Operating conditions.
- Actuation.
- Technical standards.
- Testing requirements.
- Product compatibility.

## 11.4 Spare Parts Selection

Prepare the workflow for:

- Model identification.
- Part-number matching.
- Compatibility.
- Technical revision.
- Approved alternatives.
- Quantity.
- Availability.

## 11.5 Knowledge Sources

Design the selection module to consume authorized data from:

- Product Library.
- Engineering Rules.
- Historical Selections.
- Approved Technical Datasheets.
- Performance Curves.
- Authorized EasySelect References.
- Future officially supported integrations.

Implement a modular adapter interface for future sources.

Do not hardcode the application to depend on a Claude browser session.

## 11.6 EasySelect

EasySelect is an existing KSB pump selection system.

A separate authorized research effort will study its visible workflows, required parameters, outputs, and engineering selection behavior.

Our future selection engine should be independent and based on properly authorized technical data and independently validated engineering methods.

Do not claim to reproduce unavailable proprietary algorithms.

## 11.7 Current Development Scope

Implement:

- Selection Studio navigation.
- Selected RFQ context.
- Equipment tag selection.
- Read-only extracted inputs where available.
- Product family reference structure.
- Candidate data schema.
- Selection status.
- Evidence references.
- Engineering review workflow.
- Future integration interface.

Do not generate fictitious pump selections for real customers.

If approved performance data are not available, the interface should explicitly report the limitation.

---

# 12. STEP 8 — COSTING & PRICING STUDIO

Prepare the architecture for later integration with:

**ICAP — Industrial Cost Architecture Project.**

ICAP is an existing KSB Arabia initiative focused on industrial cost measurement, standard activity rates, cost governance, and pricing excellence.

The pricing system should eventually consume:

- Approved technical configuration.
- Equipment quantity.
- Factory price references.
- Local manufacturing cost.
- Industrial rate cards.
- Buy-out component costs.
- Engineering activities.
- Testing costs.
- Surface treatment.
- Packaging.
- Freight.
- Additional services.
- Currency.
- Commercial margins.
- Pricing approvals.

### Required Price Distinction

Separate:

1. Base Product Price.
2. Factory Cost.
3. Local Industrial Cost.
4. Landed Cost.
5. Total Estimated Cost.
6. Target Selling Price.
7. Approved Selling Price.

Do not automatically treat a historical quotation price as a valid current price.

Every price must have:

- Source.
- Currency.
- Validity.
- Revision.
- Approval status.

### Current Development Scope

Create the module foundation, data structure, navigation, and appropriate configuration screens.

Do not fabricate pricing formulas or commercial values.

Actual pricing activation will depend on approved cost data and ICAP integration requirements.

---

# 13. STEP 9 — QUOTATION GENERATION

Create the foundation for generating technical and commercial offer documents.

Expected outputs:

- Technical Offer.
- Commercial Offer.
- Scope of Supply.
- Price Schedule.
- Clarification List.
- Deviation List.
- Compliance Matrix.
- Equipment Summary.
- Supporting Datasheet References.
- Inclusions and Exclusions.
- Standard Terms and Conditions.

Use versioned templates.

The quotation must pull information from approved RFQ, selection, and pricing records.

Quotation creation must not invent missing prices, product configurations, guarantees, or engineering commitments.

All generated quotations must remain drafts until approved.

### Current Development Scope

Implement the quotation module structure and document generation interfaces where feasible.

Full automated technical and commercial quotation generation is a later development milestone.

---

# 14. STEP 10 — END-TO-END BID MANAGEMENT

Prepare future support for:

- RFQ revisions.
- Customer clarifications.
- Technical revisions.
- Commercial revisions.
- Approval workflows.
- Bid submission.
- Negotiation.
- Customer feedback.
- Won / Lost / Declined.
- Lessons learned.
- Historical project reuse.

Any material change to RFQ requirements must identify potentially affected downstream stages.

For example, changing a duty point may require:

- Technical reevaluation.
- Selection review.
- Pricing review.
- Quotation revision.

Preserve prior revisions and approvals.

---

# 15. KNOWLEDGE LIBRARY ARCHITECTURE

Create a shared information layer that supports the different BidFit modules.

Recommended entities include:

- Users.
- Roles.
- Customers.
- Market Areas.
- Applications.
- RFQ Projects.
- RFQ Documents.
- Document Revisions.
- Equipment Tags.
- Extracted Requirements.
- Verified Parameters.
- Standards.
- Standard Editions.
- Engineering Rules.
- Compliance Evaluations.
- Technical Decisions.
- Engineering Reviews.
- Product Families.
- Product Models.
- Product Configurations.
- Performance References.
- Historical Selections.
- Pricing References.
- Quotation Revisions.
- Audit Logs.

Adapt these entities to the existing database architecture instead of introducing unnecessary infrastructure.

## Data Provenance

Every important knowledge record should identify:

- Original source.
- Source revision.
- Extraction method.
- Verification status.
- Approving authority.
- Creation date.
- Last modification date.
- Applicable version.

Do not treat every historical selection as a correct engineering reference.

Historical selections must be verified before being used as authoritative examples.

---

# 16. AI ARCHITECTURE

The system must not require Codex or Claude Code to be running during normal operation.

These tools are used for development.

The deployed BidFit application should have an independent AI service interface.

Suggested components:

**Document Processing**

Parse files, extract tables and text, and manage OCR where enabled.

**LLM Extraction**

Convert relevant content into structured records.

**Retrieval Layer**

Retrieve authorized technical references and relevant approved rules.

**Engineering Rules Engine**

Perform deterministic technical evaluations.

**Decision Aggregation**

Combine evaluated findings into an explainable recommendation.

**Reporting Layer**

Generate structured and human-readable outputs.

## AI Provider Independence

Create an abstraction allowing supported LLM providers to be configured without rewriting the application.

Use the existing provider integration where practical.

Keep API credentials server-side.

Never expose provider keys to the browser.

## Machine Learning

Do not implement a custom ML training pipeline prematurely.

Future learning capabilities may include:

- Historical case classification.
- Recommendation ranking.
- Human feedback analysis.
- Retrieval improvements.
- Prediction based on validated datasets.

For now, prioritize reliable extraction, retrieval, rules, and engineering review.

---

# 17. USER INTERFACE AND KSB BRANDING

The application must follow a professional industrial and engineering visual identity based on **KSB brand colors**.

The project owner will attach an official KSB logo image together with this prompt.

**IMPORTANT: USE THE ATTACHED LOGO FILE AS THE AUTHORITATIVE LOGO ASSET.**

Do not invent or recreate the logo.

Do not replace it with a generic icon.

Do not distort its proportions.

## Color Direction

Use a clean, modern palette centered on:

- KSB Blue as the primary corporate color.
- Deep Blue for important navigation and headings where appropriate.
- Light Grey backgrounds.
- Medium Grey borders and secondary surfaces.
- White content panels.
- Dark Grey primary text.

Use official color values from supplied brand assets or existing approved brand tokens where available.

If exact official color codes are not available, use clearly documented provisional tokens that can be replaced later.

Do not claim that a guessed HEX value is an official brand standard.

## Visual Style

The application should feel like:

**A modern industrial engineering platform, not a generic chatbot dashboard.**

Use:

- Professional typography.
- Clear section hierarchy.
- Compact engineering data tables.
- Consistent spacing.
- Structured cards.
- Clean forms.
- Technical status indicators.
- Responsive layouts.
- Clear workflow navigation.

## Recommended Layout

**Login Screen**

KSB branding, BidFit identity, secure login.

**Dashboard**

Left navigation, recent RFQs, statuses, and new RFQ action.

**New RFQ Wizard**

Product → Market → Application → Customer → Upload.

**RFQ Workspace**

Project header, workflow stepper, technical content, and status.

**Summary View**

Equipment tags, extracted requirements, missing values, editable parameters.

**Compliance View**

Detailed standards matrix, findings, and source evidence.

**Decision View**

Bid recommendation, explanation, approval and export.

**Selection Studio**

Technical input summary, product candidates and evidence.

**Pricing Studio**

Structured cost and price sections.

**Quotation Studio**

Draft document generation and approvals.

## Branding Implementation Requirements

Create centralized design tokens or theme variables.

Do not scatter hardcoded brand colors throughout the application.

Place the supplied logo within the existing asset system.

Ensure the logo is visible in the login and main navigation in a proportionate manner.

Use accessible color contrast.

### Important Priority

Do not spend most of the development effort on cosmetic redesign.

**Engineering workflow and functional correctness take priority over visual polishing.**

Implement consistent baseline branding without delaying functionality.

---

# 18. SECURITY REQUIREMENTS

Even though the application is currently a prototype, implement baseline security now.

At minimum:

- Secure password handling.
- Access control.
- Protected authenticated routes.
- Server-side authorization.
- Proper user session management.
- Upload size and type restrictions.
- Safe file handling.
- Protection against malicious ZIP paths.
- Tenant/project/user data isolation as applicable.
- No secrets in the frontend.
- No credentials committed to GitHub.
- Safe API error handling.
- Audit logging for critical changes.
- Secure configuration management.

Do not store raw passwords.

Do not automatically publish the application to an unrestricted public environment.

Do not migrate confidential customer files to external AI providers without verified authorization.

Do not introduce real user records into public demonstration environments.

Advanced security hardening and production certification can follow later, but these baseline controls are required from the start.

---

# 19. IMPLEMENTATION PRIORITIES

Do not attempt to complete all future phases in one large untested change.

Use the following development packages.

## PACKAGE A — RFQ WORKFLOW FOUNDATION

**PRIORITY: P0 — IMPLEMENT FIRST**

Tasks:

1. Inspect existing application.
2. Preserve current functionality.
3. Implement Product Classification.
4. Implement six Market Areas.
5. Implement Application Subcategories.
6. Implement Customer Classification.
7. Implement persistent RFQ Workspace.
8. Upgrade document management.
9. Separate extraction from technical evaluation.
10. Implement RFQ Summary Review.

Acceptance criteria:

- New RFQ can be created.
- Classification is stored correctly.
- Documents are uploaded and associated with the RFQ.
- Summary displays extracted information.
- User can correct extracted parameters.
- Data persists between screens.
- Existing RFQ history remains functional.

## PACKAGE B — STANDARDS & COMPLIANCE

**PRIORITY: P0 — IMPLEMENT IMMEDIATELY AFTER PACKAGE A**

Tasks:

1. Standards Registry.
2. Standards applicability suggestions.
3. Rule Registry.
4. Requirement-to-rule mapping.
5. Evidence tracking.
6. Compliance evaluation.
7. Compliance Matrix UI.
8. Missing information detection.
9. Technical findings.
10. Explainable Bid/No-Bid Decision.
11. Review and approval status.
12. Exportable report.

Acceptance criteria:

- No unsupported compliance claims.
- Each finding has an evidence reference or clear missing-evidence status.
- Missing data cannot silently become a pass.
- A verified hard stop can block an RFQ under approved rules.
- Engineer can review and override with justification.
- Decision is auditable and reproducible.

## PACKAGE C — SELECTION FOUNDATION

**PRIORITY: P1 — CAN PROCEED IN PARALLEL**

Tasks:

1. Product Library Schema.
2. Product Family Management.
3. Selection Studio Interface.
4. Equipment Tag Integration.
5. Candidate Selection Data Model.
6. Engineering Review Status.
7. Future EasySelect Reference Interface.

Do not claim that the selection engine is complete without validated product performance data.

## PACKAGE D — PRICING & QUOTATION FOUNDATION

**PRIORITY: P2**

Tasks:

1. Pricing Module Navigation.
2. Pricing Data Schema.
3. ICAP Integration Interface.
4. Quotation Template Management.
5. Quotation Draft Status.
6. Future Approval Workflow.

Build usable foundations without fabricating commercial data.

---

# 20. REQUIRED DEVELOPMENT PROCESS

Before changing the code:

## Step A — Repository Inspection

Identify:

- Framework.
- Directory structure.
- Database.
- Authentication implementation.
- File upload implementation.
- AI integration.
- Existing RFQ analysis logic.
- Current routes and pages.
- Testing framework.
- Existing styling system.
- Deployment configuration.

Produce a short architecture inventory.

## Step B — Gap Assessment

Compare existing functionality with BidFit 2.0 requirements.

Classify each requirement:

- Existing and Working.
- Existing but Needs Improvement.
- Missing.
- Blocked by Data.
- Future Phase.

## Step C — Implementation Plan

Create a concise, actionable implementation backlog.

Preserve compatibility with existing data and APIs whenever feasible.

## Step D — Implement Package A

Create working code, migrations where needed, and tests.

## Step E — Implement Package B

Create the engineering rules and compliance foundation.

Use synthetic, explicitly labeled test examples when approved technical data are missing.

## Step F — Implement Package C Foundation

Create the selection module structure without inventing engineering calculations or product capabilities.

## Step G — Test Everything

Run existing and new tests.

Fix failures introduced by your changes.

Check basic security controls.

Verify that current application functionality still works.

---

# 21. IMPORTANT TEST CASES

Build automated tests around synthetic scenarios.

### Case 1 — Complete Pump RFQ

The system successfully extracts all required information and identifies applicable approved rules.

### Case 2 — Missing NPSHA

The system identifies missing data and does not claim confirmed hydraulic feasibility.

### Case 3 — Unsupported Pump Type

A verified product-boundary restriction produces a technically justified finding.

### Case 4 — Possible Deviation

A technical requirement is not satisfied, but a deviation may be requested.

Expected result: Conditional Go or engineering review, depending on applicable approved rules.

### Case 5 — Mixed Package

An RFQ contains pumps, valves, and spare parts.

The system creates separate line-item evaluations.

### Case 6 — Contradictory Documents

The RFQ datasheet and another applicable document contain inconsistent operating values.

The system flags the conflict rather than silently choosing one.

### Case 7 — New Document Revision

The user uploads a revised RFQ.

The system preserves prior versions and identifies affected evaluation results.

### Case 8 — Standards Not Available

The system identifies a customer-required standard but lacks an approved corresponding rule.

Expected result: Not Verified / Review Required, not an invented compliance assessment.

### Case 9 — Historical RFQ Access

Existing RFQ records remain available after the upgrade.

### Case 10 — Unauthorized Access

A user cannot access protected project data or restricted administrative actions without sufficient permissions.

---

# 22. DELIVERABLES IN THE REPOSITORY

Produce and maintain:

1. Working BidFit 2.0 code changes.
2. Database migrations, if required.
3. Updated navigation and UI components.
4. Product and application classification configuration.
5. RFQ Workspace.
6. Document extraction review interface.
7. Standards Registry.
8. Engineering Rule Registry.
9. Compliance Matrix.
10. Explainable Bid/No-Bid Decision View.
11. Product Selection Studio foundation.
12. Pricing and Quotation module foundations where feasible.
13. Automated tests.
14. Updated README.
15. Development backlog.
16. Architecture and data model documentation.

Suggested documentation files:

- `docs/BIDFIT_2_0_FUNCTIONAL_SPEC.md`
- `docs/SYSTEM_ARCHITECTURE.md`
- `docs/ENGINEERING_RULES.md`
- `docs/STANDARDS_REGISTRY.md`
- `docs/DATA_MODEL.md`
- `docs/IMPLEMENTATION_BACKLOG.md`
- `docs/TEST_EVIDENCE.md`
- `docs/FUTURE_SELECTION_ENGINE.md`

Follow the repository's existing documentation conventions if they differ.

---

# 23. IMPLEMENTATION REPORTING

At the end of each completed development package, report:

**A. Implemented Features**

What code was actually changed.

**B. Working Functionality**

Which features were tested successfully.

**C. Tests**

Which tests were executed and their results.

**D. Remaining Gaps**

Which requirements remain incomplete.

**E. Engineering Dependencies**

Which functions require approved KSB product data or engineer validation.

**F. Next Recommended Package**

What should be developed next.

Do not claim success for untested functionality.

Do not treat a page rendering successfully as proof of engineering correctness.

---

# 24. PROJECT OWNER'S NON-NEGOTIABLE EXPECTATIONS

The following requirements are mandatory:

1. Do not lose existing application functionality.
2. Do not rebuild the entire website without justification.
3. Preserve the approved product and application classification.
4. Maintain one continuous RFQ workspace.
5. Show the RFQ summary before technical evaluation.
6. Display detailed standards comparisons.
7. Explain every Bid/No-Bid recommendation.
8. Preserve document and rule traceability.
9. Never invent engineering compliance results.
10. Prepare a separate selection module.
11. Keep pricing ready for future ICAP integration.
12. Preserve a clear path toward end-to-end bidding.
13. Apply KSB Blue and Grey visual styling.
14. Use the official logo attached by the project owner.
15. Maintain appropriate baseline security.
16. Build real, tested features, not merely presentation screens.

---

# 25. FINAL EXECUTION INSTRUCTION

**BEGIN WORKING ON THE EXISTING REPOSITORY NOW.**

Your first actions must be:

1. Inspect the current codebase.
2. Identify the current application's capabilities and gaps.
3. Check the current Git branch and repository state.
4. Preserve existing work and avoid destructive changes.
5. Create an actionable implementation plan.
6. Start implementing Development Package A.
7. Add tests and verify the working user journey.
8. Continue to Development Package B where feasible.
9. Establish the foundational architecture for Package C.
10. Report actual implementation status.

Do not wait for a complete EasySelect research report.

Do not wait for all engineering documents before building the workflow foundation.

Use synthetic data and configurable placeholders where required, clearly marked as such.

Do not implement fake engineering rules or unsupported pump selection results.

If a specific engineering rule is unavailable, build the infrastructure and identify the missing data rather than inventing a value.

**This is an implementation assignment. The expected outcome is a working upgrade to the existing BidFit application, not merely a strategy document.**

**Immediate goal: A functional BidFit 2.0 workflow covering classification, RFQ understanding, standards-based evaluation, and an explainable preliminary Bid/No-Bid recommendation.**

**Long-term vision: A complete AI-powered engineering selection, costing, pricing, quotation, and bid management platform.**

Proceed with implementation using the current repository and environment.
