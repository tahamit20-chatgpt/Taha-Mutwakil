# Codex development master prompt — BidFit Phase 1
Version 1.0 • Self-contained implementation brief • 18 October 2026

You are implementing a limited standalone prototype of BidFit for KSB Pumps Arabia. Deliver functioning code, migrations, fixtures, automated tests and deployment instructions. This brief authorizes implementation in an appropriate development workspace, not deployment, purchases, private-system access or confidential-data transfer. This research assignment itself has produced specifications only.

## Outcome
Authenticated users upload synthetic RFQ PDFs/TXT, review extracted requirements per pump tag with source pages, run deterministic technical rules, record separate commercial assessment and engineer disposition, and export preliminary evaluation reports. Do not build a chatbot interface as the primary product. No SAP, Salesforce, C4C, EasySelect API or corporate login dependency. Do not reproduce vendor data or claim certified pump selection.

## Required stack and repository
React/TypeScript/Vite UI, Python/FastAPI/Pydantic backend, SQLAlchemy/Alembic PostgreSQL, private S3-compatible storage, same-codebase worker with PostgreSQL durable queue and managed OIDC sessions. Production model/provider is environment-configurable; provide a deterministic fake extraction adapter for CI and local demos.

Create frontend/, backend/app/{api,auth,documents,extraction,facts,rules,evaluations,reviews,reports,jobs,knowledge}, backend/tests/, migrations/, fixtures/synthetic/, infra/, docs/. Use one Python application modularized by domain, not microservices. Serve built static UI behind the same origin. Local Compose may use development OIDC and S3-compatible services; label development-only defaults and do not expose them publicly. Pin supported dependency versions at implementation time and record licenses. Never commit credentials or real customer files.

## Core entities
Tenant, UserMembership, ProjectMembership, Project, Tag, Document, immutable DocumentVersion, Page, EvidenceSpan, RequirementFact, FactReview, Conflict, ExtractionRun, RulePack/RuleVersion, CapabilityVersion, CustomerApproval, EvaluationRun, RuleResult, Clarification, Deviation, Adjudication, CommercialAssessment, ManagementDecision, Job, Export and AuditEvent. UUIDs and tenant_id everywhere; scoped FKs stop cross-tenant relationships. lock_version for mutable edits; UTC timestamps. Approved versions and evaluation results are immutable. Product/curve entities may be migration stubs until Phase 2.

## Ingestion
Accept English text PDF/TXT only in committed scope. Limits: 25 MiB/file, 20 files/project, 500 pages/project, configurable. Quarantine, verify signature/MIME, malware-scan and reject unsupported/encrypted files with useful reasons. Preserve original bytes and SHA-256, page count, page text, source spans, parser and extraction versions. Unsupported relevant files count as coverage gaps. Do not silently omit drawings or scanned pages. OCR is optional adapter; unavailable OCR returns NEEDS_REVIEW with page coverage gaps.

Document states: UPLOAD_PENDING, QUARANTINED, VALIDATED, PARSING, EXTRACTING, NEEDS_REVIEW, READY_FOR_EVALUATION, PARTIAL, FAILED, CANCELLED. Jobs use a lease, heartbeat, retry attempts, stage checkpoints and idempotency keys. Claim via FOR UPDATE SKIP LOCKED. Default maximum 3 transient retries, then visible failure. Restarting a worker must not create duplicate documents/facts/runs.

## Extraction schema and review
Extract per tag: pump type/configuration, quantity, liquid/composition, Q min/rated/max, H min/rated/max, temperature, density, viscosity and basis, suction/discharge pressures and gauge/absolute basis, NPSHA and datum, frequency/rpm, materials by component, applicable standard+edition, customer/factory approval requirements, MCSF/BEP/head-rise requirements, and mandatory/preferred/informative modality. Missing values are null. Unsupported field names and invented citations fail schema validation.

Each fact includes raw value/unit, normalized SI value/unit, duty basis, tag, evidence document-version ID, one-based physical page or TXT line range, source span, extraction method/warnings and review status. LLM output only proposes facts. Require exact evidence-span matches. Documents cannot instruct the model to change the system, invoke tools or relax rules. No external links are fetched.

Normalize Q to m³/s, H to m, density to kg/m³, pressure to Pa with explicit basis, temperature to K and viscosity to Pa·s. Never guess US versus imperial gpm, fluid density or gauge/absolute basis. Preserve contradictory facts until engineer resolution under an explicit precedence policy. Latest upload time alone does not supersede requirements. Corrections append FactReview, preserve original evidence and create a new accepted fact snapshot.

## Rule interpreter
Implement an allowlisted typed JSON rule schema; no eval, SQL expressions or LLM-written executable logic. Fields: schema_version, criterion_id, scope (project/tag/candidate), applicability, required_inputs, operator (range, enum_in, approved_record, margin, coverage), parameters, units, severity, waiver_policy, missing_impact, authority, version, status, effective interval, approved_by/at and immutable content hash. Explicitly evaluate applicability to applicable/not_applicable/unknown, retaining reason.

Draft/unapproved required rules return UNKNOWN and block a GO. Synthetic approved rules run only on synthetic datasets in a separate namespace. Live KSB thresholds remain null/pending until supplied by engineering. Test fixture NPSH margin 1.5 m must never become a real default.

Rule results: PASS, FAIL, UNKNOWN, NOT_APPLICABLE. Store criterion, extracted fact IDs, requirement and capability evidence separately, rule version, validation result, severity, uncertainty, calculation, remarks, required clarification and decision impact. A missing capability or empty search is UNKNOWN, not confirmed incompatibility.

## Decision logic (implement exactly)
Candidate FAIL eliminates only that candidate. A tag NO-GO requires confirmed non-waivable project prohibition, or an engineer-approved complete current portfolio scope in which every permitted solution fails a mandatory non-waivable constraint. No complete coverage → cannot conclude NO-GO from candidate failures.

Precedence per tag: (1) confirmed hard prohibition → NO-GO; (2) unresolved decision-critical facts/conflicts/applicability/required rules/capability/processing coverage → INSUFFICIENT DATA; (3) explicit waivable deviation or noncritical action → CONDITIONAL GO; (4) every mandatory applicable check positively supported and minimum screening coverage met → GO. All are preliminary screening outcomes.

Project default is complete-package scope: required-tag NO-GO dominates, then INSUFFICIENT DATA, then CONDITIONAL GO, then GO. Partial lots require explicit permission and selected subset while all original results remain visible. Technical and commercial dimensions are distinct. No invented official GOAL weights. Management can decline technical GO but cannot bypass mandatory engineering/regulatory prohibition.

Human review appends adjudication with original result, requested disposition, actor, reason, evidence and scope. Never overwrite computed results. A corrected fact or accepted waivable deviation triggers a new evaluation. Non-waivable constraint cannot be changed by free-text override. New document/fact/rule/capability state makes prior approval stale for the current project; preserve historic approval of its old snapshot.

## Engineering functions
Implement tested dimensional conversion and power functions now: Q[m³/h]/3600; P_h=ρgQH; P_shaft=P_h/η with 0<η≤1, g=9.80665. Pressure-to-head requires density and pressure basis. No motor selection from duty power alone. Stub hydraulic selection as UNVERIFIED until approved curves and conditions are available. Never synthesize curves, NPSHR, approvals or compatibility from LLM knowledge. Future curve function uses bounded piecewise linear interpolation and rejects extrapolation.

## API and UI
Under /api/v1 implement session; scoped projects/tags/documents; upload/content/process; job polling; facts/reviews; evaluation creation/results; adjudications; commercial assessment; management decision; exports; rule-pack submission/engineering approval. Mutations use idempotency or expected lock_version as appropriate. 409 for stale snapshots, 415 unsupported files, 422 semantic errors. Server-generated UUIDs and object keys. Use typed OpenAPI client.

Screens: login, dashboard, project/tag/manifest, upload/progress, side-by-side source/fact review, technical rule results, clarification/deviation register, separate commercial assessment, review/history and export. Clearly distinguish missing data, unsupported files, and unresolved rules from technical failures. Do not show a model shortlist pretending hydraulic validation in Phase 1.

## Security and operations
Invite-only OIDC authorization code+PKCE; secure HttpOnly SameSite cookies and CSRF protection, state/nonce validation, session rotation/revocation; no localStorage tokens. Backend checks tenant and project membership for every object including jobs/exports. Private storage with authorized 60-second signed downloads. TLS, least privilege roles, secrets manager, parser sandbox/resource limits and outbound provider allowlist. Escape HTML and neutralize CSV formula injection. Log correlations, costs and states, not RFQ bodies/secrets. Synthetic-only default with provider egress disabled until configured. Add retention/deletion hooks, backup/restore runbook and health/readiness endpoints.

## Reports
HTML printable report plus JSON and CSV exports from the same frozen evaluation. Include project/tag scope, preliminary outcome, requirement/capability/rule citations, raw and normalized values, rule results, missing/contradictory data, clarifications, deviations, human review, run hash and versions. Exports must never rebuild from latest mutable facts. Branded formatting can be simple; factual traceability takes priority.

## Test matrix and definition of done
1. Four synthetic expected outcomes; hard failure dominates while remaining unknowns stay visible.
2. Missing head/approval/NPSH basis, empty catalogue, required draft rules and failed relevant page prevent GO.
3. Two candidate failures with incomplete search scope do not yield tag NO-GO.
4. Multi-tag complete-package and explicitly permitted partial-lot rollups.
5. Unit conversions including ambiguous gpm, null versus zero, invalid density and η boundaries.
6. Exact source-page citation and contradiction preservation; prompt-injection text cannot modify rules.
7. Cross-project/tenant denial across files, source spans, jobs, results and downloads.
8. Concurrent fact edit returns 409; rule change invalidates current approval; historic export remains identical.
9. Worker restart, expired lease and idempotency reuse do not duplicate results.
10. Mandatory non-waivable failure cannot be overridden through UI or direct API.
11. HTML/CSV injection, file limits/signatures and unsupported/encrypted PDF handling.
12. Measured evaluation p95 target ≤2 seconds for 20 tags×40 rules after extraction, separately from ingestion; report actual host and timings, not an untested guarantee.

Run backend unit/integration tests, UI typecheck/build and end-to-end happy/error paths. Provide independent golden expected values: synthetic Q=100 m³/h, H=50 m, ρ=1000, η=.75 → hydraulic 13.6203472 kW, shaft 18.1604630 kW. No model/API network calls in ordinary CI. Document unsupported cases, open defects and production gaps. No claim of certified engineering validation.

## Delivery sequence
Days 1–2: scaffold, data, auth and project UI. Days 3–5: upload/jobs/parse/extract/review. Days 6–8: rules/rollup/review/commercial separation. Days 9–10: exports, security/restart tests, demo and runbook. Assumes two experienced developers with 120 total focused hours plus engineering reviewer. Deliver a local reproducible demo even if approved cloud configuration is pending. Defer advanced OCR, RAG embeddings, ML, certified hydraulic selection, pricing and integrations.

Use the companion blueprint/data architecture/workbooks when available. If absent, this prompt contains the minimum implementation contract. Report actual completed behavior and test results, not merely planned components. Ask only for blocked secrets/configuration through secure channels; never request passwords in chat.


## Appendix: initial machine-readable rule contract

This JSON Schema is a starting validation contract, not an approved engineering rule pack. No real thresholds are supplied. Implement operator-specific semantic validation in addition to JSON Schema: range needs at least one bound; margin needs its required threshold(s) and matching units; enum_in needs allowed_values; approved_record needs registry_type; coverage needs a valid coverage_policy_id. Unknown applicability contributes UNKNOWN, not NOT_APPLICABLE. Required null thresholds prevent publication. Parameter key changes require schema migration; approved numeric threshold changes require only a new rule version and engineering approval.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "BidFitRuleV1",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version",
    "criterion_id",
    "scope",
    "applicability",
    "required_inputs",
    "operator",
    "parameters",
    "severity",
    "waiver_policy",
    "missing_impact",
    "authority",
    "version",
    "status",
    "synthetic_only",
    "approval"
  ],
  "properties": {
    "schema_version": {
      "const": "1.0"
    },
    "criterion_id": {
      "type": "string",
      "pattern": "^[TD][0-9]{2}$"
    },
    "scope": {
      "enum": [
        "project",
        "tag",
        "candidate"
      ]
    },
    "applicability": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "field",
        "operator",
        "value"
      ],
      "properties": {
        "field": {
          "type": "string"
        },
        "operator": {
          "enum": [
            "equals",
            "in",
            "exists"
          ]
        },
        "value": {}
      }
    },
    "required_inputs": {
      "type": "array",
      "minItems": 1,
      "uniqueItems": true,
      "items": {
        "type": "string"
      }
    },
    "operator": {
      "enum": [
        "range",
        "enum_in",
        "approved_record",
        "margin",
        "coverage"
      ]
    },
    "parameters": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "unit": {
          "type": [
            "string",
            "null"
          ]
        },
        "minimum": {
          "type": [
            "number",
            "null"
          ]
        },
        "maximum": {
          "type": [
            "number",
            "null"
          ]
        },
        "inclusive": {
          "type": "boolean"
        },
        "margin_mode": {
          "enum": [
            "difference",
            "ratio",
            "both",
            null
          ]
        },
        "allowed_values": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "registry_type": {
          "type": [
            "string",
            "null"
          ]
        },
        "coverage_policy_id": {
          "type": [
            "string",
            "null"
          ]
        }
      }
    },
    "severity": {
      "enum": [
        "BLOCKER",
        "REVIEW",
        "INFO"
      ]
    },
    "waiver_policy": {
      "enum": [
        "NON_WAIVABLE",
        "WAIVABLE",
        "BY_REQUIREMENT"
      ]
    },
    "missing_impact": {
      "enum": [
        "INSUFFICIENT DATA",
        "CONDITIONAL GO"
      ]
    },
    "authority": {
      "type": [
        "object",
        "null"
      ],
      "properties": {
        "source_version_id": {
          "type": "string"
        },
        "location": {
          "type": "string"
        },
        "standard_edition": {
          "type": [
            "string",
            "null"
          ]
        }
      },
      "required": [
        "source_version_id",
        "location"
      ],
      "additionalProperties": false
    },
    "version": {
      "type": "integer",
      "minimum": 1
    },
    "status": {
      "enum": [
        "DRAFT",
        "APPROVED",
        "RETIRED"
      ]
    },
    "synthetic_only": {
      "type": "boolean"
    },
    "approval": {
      "type": [
        "object",
        "null"
      ],
      "additionalProperties": false,
      "required": [
        "approved_by",
        "approved_at",
        "valid_from",
        "valid_to",
        "content_hash"
      ],
      "properties": {
        "approved_by": {
          "type": "string"
        },
        "approved_at": {
          "type": "string",
          "format": "date-time"
        },
        "valid_from": {
          "type": "string",
          "format": "date-time"
        },
        "valid_to": {
          "type": [
            "string",
            "null"
          ],
          "format": "date-time"
        },
        "content_hash": {
          "type": "string",
          "pattern": "^[a-f0-9]{64}$"
        }
      }
    }
  },
  "allOf": [
    {
      "if": {
        "properties": {
          "status": {
            "const": "APPROVED"
          }
        }
      },
      "then": {
        "properties": {
          "authority": {
            "type": "object"
          },
          "approval": {
            "type": "object"
          }
        }
      }
    }
  ]
}
```

Draft NPSH example, intentionally not executable as an approved technical rule:

```json
{
  "schema_version": "1.0",
  "criterion_id": "T09",
  "scope": "candidate",
  "applicability": {
    "field": "npsh_check_required",
    "operator": "equals",
    "value": true
  },
  "required_inputs": [
    "npsha_m",
    "npsh3_m",
    "duty_conditions"
  ],
  "operator": "margin",
  "parameters": {
    "unit": "m",
    "minimum": null,
    "maximum": null,
    "inclusive": true,
    "margin_mode": "difference"
  },
  "severity": "BLOCKER",
  "waiver_policy": "BY_REQUIREMENT",
  "missing_impact": "INSUFFICIENT DATA",
  "authority": null,
  "version": 1,
  "status": "DRAFT",
  "synthetic_only": false,
  "approval": null
}
```

Publication service must verify reviewer authority, immutable content hash, source license/scope, threshold completeness, interval validity and operator semantic checks. Schema validation alone is insufficient. Serialize a canonical payload excluding the derived approval hash to avoid hashing a self-referential value. Runtime binds pack and rule hashes in each evaluation.

## Delivery boundary

- Established: self-contained build contract and test expectations
- Uncertain: implementation runtime/provider versions and real data
- Engineering approval: production rules and acceptance of real engineering results
- Implement immediately: synthetic Phase 1 prototype
- Postpone: production operation and certified hydraulic selection
