# Approval data provenance and limitations

## What was supplied

The owner supplied a structured implementation request on 29 October 2026. Its
verbatim content is retained in `ARAMCO_IMPLEMENTATION_REQUEST.md`. The seed stores
that input reference, a deterministic structured-input hash and source metadata.
This is provenance for an owner-supplied transcription, not authentication of the
underlying documents or independent verification of a customer approval.

| Named source | Metadata supplied | Actual file state |
|---|---|---|
| Aramco Approval Notification Letter for KSB Pumps Arabia Ltd..pdf | Issuer Saudi Arabian Oil Company, Supplier Relationship Management; SQU-26-24; 1 April 2024; vendor 10066368; plant 30008606; seven codes | Not provided, not imported, not inspected; attachment PENDING; page unknown |
| KSB PA main persentation 2026.pptx | Owner-reported 2026 presentation; slide 1 category list, slide 2 horizontal products, slide 3 vertical products | Not provided, not imported, not inspected; attachment PENDING; slides are reported references |

The file-title strings are metadata only, not fabricated filesystem paths or
claims that original protected files are present. The two actual files could not
be reconciled against their transcription. No live 2026 approval query was made.
No additional initial code, plant, vendor, series, validity or certification was
invented. Manufacturing location, source pages, exact presentation date/revision,
validity/expiry and current verification remain unknown where not supplied.

## Separation of claims

1. Original historical commodity listing: **reported by owner; source attachment
   pending**, not falsely labelled confirmed by an uploaded letter.
2. Product-to-code association: **internal mapping reported by owner; source
   presentation pending**, not an official customer product certificate.
3. Current approval: **verification required** for all seven initial records.
4. Configuration/duty/material/standards compliance: independent evaluation;
   approved engineering data, curves, customer clauses and selection remain absent.
5. Commercial eligibility, pricing and participation: independent existing workflow.

These limitations appear in registry screens, RFQ summaries, findings and frozen
exports. Demo RFQs use fictional training duties and do not represent real
Aramco requests. Their product/code identifiers demonstrate matching only.

## Future authorized data onboarding

Obtain permission to handle the actual letter/presentation and any current source,
then implement the approved document-scanning and authority validation boundary.
Store originals privately, verify hashes and dates, inspect actual page/slide
references, reconcile discrepancies with the owner, and append source revisions
and designated verification reviews. Do not silently replace historical evidence.
Current-source metadata or a checkbox alone must never confer authority.

The minimal working admin interface supports supplied metadata, reference
revisions, mapping changes, conditions, synthetic private test attachments and
append-only verification history today. Original customer-document attachment
and genuine current verification are deliberately unavailable until that boundary
is implemented. Live customer system access, component/9CAT sources, contract
editions/clauses, configuration evidence and approved blocking policies remain
specific dependencies. Synthetic tests exercise storage/history without pretending
to resolve those dependencies. Source originals and secrets are excluded from
repository/package delivery.
