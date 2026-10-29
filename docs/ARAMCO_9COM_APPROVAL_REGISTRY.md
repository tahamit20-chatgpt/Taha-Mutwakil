# Saudi Aramco approval registry

This is an additive BidFit 2.0 upgrade on branch `bidfit/aramco-approvals`.
The seven initial classifications and eight product references come from the
owner's implementation request, not inspected certificates or a live customer
system. The named PDF and PPTX are absent. Both source attachments are PENDING;
current status is REQUIRES_VERIFICATION for every initial commodity.

## Initial profile and commodities

Customer Saudi Aramco; manufacturer KSB Pumps Arabia Ltd.; vendor `10066368`;
plant `30008606`; original reported date `2024-04-01`; reference `SQU-26-24`.
Manufacturing location, source page, validity start/end and last verification
are unknown (NULL). These identifiers are strings throughout the database/API.

| 9COM | Owner-supplied official description | Category |
|---|---|---|
| 6000002283 | PUMP; CENTRIFUGAL; GENERAL SERVICE; HORIZONTAL | Pump / Pump Set |
| 6000002288 | PUMP; CENTRIFUGAL; VERTICALLY SUSPENDED | Pump / Pump Set |
| 6000002346 | PUMP; CENTRIFUGAL; GENERAL SERVICE; VERTICAL | Pump / Pump Set |
| 6000002350 | PUMP; CENT, HORIZ, ASMEB73.1 OR ISO5199 | Pump / Pump Set |
| 6000002355 | PUMP; CENTRIFUGAL; MAIN FIREWATER; HORIZONTAL | Pump / Pump Set |
| 6000002356 | PUMP; CENTRIFUGAL; END SUCTION; SINGLE STAGE | Pump / Pump Set |
| 6000011675 | RE-ENGINEERED MACHINED OR WELDED PARTS | Spare Parts |

A historical listing never covers every model, configuration, material, duty or
manufacturing condition. Missing from the seven records does not prove current
non-approval.

## Data relationships and migration

Migration `0002` adds six tables without changing or deleting existing RFQs:

- `approval_profiles`: tenant/customer/vendor/plant identity, unique composite key.
- `approval_evidence`: source metadata; immutable attached bytes and SHA-256 when supplied.
- `approval_commodities`: unique tenant/profile/code, foreign keys to profile and evidence.
- `approval_product_series`: unique tenant/name, design-reference metadata only.
- `approval_product_mappings`: many-to-many series/commodity associations with tenant-scoped foreign keys to product, commodity, profile and evidence.
- `approval_verifications`: append-only source-linked reviews, with explicit supersedes foreign key.

Relationships use composite tenant/identifier foreign keys. Extensible metadata
uses the existing SQLAlchemy JSON convention. `approval_event`,
`approval_assignment` and versioned `approval_policy` reuse the existing domain
record table. Every modification retains before/after metadata in the audit
history. Verification records and old evaluation snapshots are never overwritten.
This is application-enforced append-only behavior, not a certified tamper-proof
archive or PostgreSQL RLS deployment.

`alembic upgrade head` applies the additive migration. Startup scripts already run
this command. First authorized lookup imports `configuration/aramco_seed.json`
under a transaction advisory lock. Running lookup/seed repeatedly preserves the
same identities; it does not overwrite later administrative revisions.

## User interface

1. Knowledge Library → Customer Approvals → Saudi Aramco: profile, seven
   classifications, filters, sources, current status and verification history.
2. Product Library → KSB Product Series: design references and sourced
   many-to-many commodity mappings, separately from existing manual family records.
3. Saudi Aramco RFQ → RFQ summary: review explicit required 9COM, select a
   candidate reference, enter proposed manufacturing identifiers and review
   component applicability. Saving changes requires a fresh summary acknowledgement.
4. Compliance & decision: item-level ARAMCO checks plus the existing independent
   engineering checks; frozen approval inputs also appear in HTML/JSON/CSV reports.

The RFQ creation classification steps remain unchanged. Matching a selected
customer/profile/end user to Saudi Aramco activates the module. Other customers
receive no automatic Aramco eligibility checks.

## Management and protected evidence

Alice is the local demo configuration administrator and designated verification
reviewer. Bob and Viewer cannot change shared references. Production identity
providers must assign `configuration`, `engineering_approval` and
`approval_verification` permissions deliberately; demo roles are not corporate
credentials.

Expand **Manage approval references & append review history**. Working operations
add source metadata, add/revise commodities, series and mappings, append
verification reviews, version the limited evidence policy and inspect audit history.
Optimistic revision checks reject stale edits. Existing evidence must be referenced;
cross-category product mappings are rejected. No source-code edit is required for
routine supplied reference updates. The initial profile identity is read-only in
this version; multi-customer/profile administration is future work.

Only labelled synthetic UTF-8 TXT attachments can be stored through the demo
approval evidence endpoint (2 MiB). They stay private in existing S3-compatible
storage; authenticated same-tenant users can inspect/download shared registry
sources. Cross-tenant and anonymous requests are denied. Object keys remain
server-side. Each download is audited, and attachments cannot be overwritten.
Actual customer documents remain blocked pending approved ingestion/scanning and
authority validation. A metadata entry labelled CURRENT_CUSTOMER_SOURCE is not
sufficient to verify status. No protected PDF/PPTX is bundled or publicly hosted.

## API overview

All routes use existing session authentication and CSRF protection for writes.

| Route under /api/v1 | Purpose |
|---|---|
| GET /approvals/registry | Profile/catalog; category, classification, code, series, status filters |
| GET/POST /approvals/products | Lookup or controlled series revision |
| POST /approvals/commodities | Add or revise a commodity with expected version |
| POST /approvals/mappings | Add or revise a many-to-many association |
| GET/POST /approvals/evidence | Specific-source GET by ID; POST new metadata |
| POST /approvals/evidence/{id}/attachment | Immutable synthetic test attachment |
| GET /approvals/evidence/{id}/content | Authenticated protected download |
| POST /approvals/commodities/{id}/verifications | Append designated-reviewer record |
| GET /approvals/history | Configuration administrator audit history |
| PUT /approvals/policy | Designated engineer appends evidence-policy version |
| GET /projects/{id}/approvals | Project-authorized item-level assessment |
| PUT /projects/{id}/approvals/assignment | Engineer candidate/identifier/component review |

Full request contracts are in `docs/openapi.json` and authenticated server API
responses. See APPROVAL_VERIFICATION_LOGIC.md and APPROVAL_DATA_PROVENANCE.md.
