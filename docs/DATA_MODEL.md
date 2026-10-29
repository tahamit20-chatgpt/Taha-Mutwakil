# Additive domain model

The existing `records` table (UUID, tenant_id, project_id, kind, JSON data, lock_version, UTC creation timestamp) and `jobs` table remain. Composite tenant/project and tenant/document FKs and server-side membership checks protect resources. No schema change is needed to add JSON domain kinds; Alembic's existing initial schema remains valid.

Project JSON adds `workflow_version`, classification, equipment register, summary notes and updated timestamp. Legacy records missing these fields remain readable/evaluable. Classification edits preserve tag IDs/names and append a classification review. Changing a material input bumps project lock_version, makes frozen runs historical and invalidates the reviewed-summary hash where appropriate.

New tenant-scoped kinds:

| Kind | Provenance / version behavior |
|---|---|
| master_config / configuration_history | approved initial taxonomy retained; customer/application additions revisioned |
| standard_ref | identifier/edition/category/source only; unavailable until authorized data supplied |
| engineering_rule / rule_approval | draft creation, immutable approved content hash/version; designated synthetic approval |
| summary_review | actor/reason/hash and acknowledged missing/conflicting data |
| standard_review | tag/reference/edition applicability, reason, actor; append-only |
| document_review | prior metadata, justification and actor; original bytes/hash never replaced |
| product_family | source/revision/category, explicitly unverified |
| selection_candidate / selection_review | RFQ inputs hash, referenced family snapshot, manual evidence and review; performance remains unverified |
| price_reference | separate price kind, amount or null, currency, validity, source/revision, DRAFT_UNAPPROVED |
| quote_template / quotation | versioned template and frozen draft snapshot; no fabricated prices or guarantees |
| branding_audit | uploader/hash of exact original public brand PNG; not an RFQ document |

Existing document rows add revision_of, revision number, category confirmation and optional parent_archive_id. ZIP originals and every accepted child are retained; unsafe archives produce visible failures without extracting filesystem paths. Source spans now preserve PDF physical page, TXT line, Word paragraph, or Excel worksheet/cell range. Parse versions and exact projected source text remain attached.

Evaluation snapshots add classification, summary hash/review, standards layers, complete matrix, exact active rule versions/hash and original fact reviews. Changes to the active approved registry invalidate current approval even if project facts did not change. Exports always render that stored snapshot. Post-run adjudications remain append-only in History and do not retroactively change historic reports. Candidate/pricing/quotation drafts do not silently alter technical facts.

Full normalization, DB-enforced immutable triggers/RLS, retention/deletion workflows and administrative membership management remain future work; API immutability does not claim database-operator protection.


## Customer approval extension (migration 0002)

`approval_profiles` → `approval_commodities`; `approval_product_series` ↔
`approval_commodities` via `approval_product_mappings`; each association records
profile, source and plant. `approval_evidence` stores private source provenance;
`approval_verifications` appends dated, superseding reviews. Composite tenant keys
enforce association isolation. Domain approval events, assignments and evidence
policies reuse existing records. See ARAMCO_9COM_APPROVAL_REGISTRY.md.
