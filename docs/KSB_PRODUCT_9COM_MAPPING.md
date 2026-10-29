# Owner-supplied KSB product/9COM mapping

Source description: `KSB PA main persentation 2026.pptx`, slides 2 and 3 as
identified by the owner. The actual presentation is NOT attached or inspected.
Mappings are REPORTED_MAPPING_SOURCE_PENDING, not current customer certificates,
validated performance data or automatically applicable contractual standards.

| Series | Classification | 9COM | Design-reference identifiers | Reported slide |
|---|---|---|---|---|
| MegaCPK | OH1 – Horizontal Foot-Mounted, Radially Split | 6000002350 | ISO 2858 / ISO 5199 | 2 |
| Etanorm | Horizontal General Service | 6000002283 | HI / EN 733 | 2 |
| RPH | OH2 – Horizontal Centerline-Mounted, Radially Split | 6000002356 | API 610 / ISO 13709 | 2 |
| Omega | BB1 – Axially Split | 6000002355 | HI; BB1 with deviations from API 610 | 2 |
| WKB | VS1 – Vertically Suspended | 6000002288 | API 610 / ISO 13709 | 3 |
| RPH-V | VS4 – Vertically Suspended Sump Pump | 6000002288 | API 610 / ISO 13709 | 3 |
| WKTR | VS6 – Double-Casing Vertically Suspended | 6000002288 | API 610 / ISO 13709 | 3 |
| Movitec | Vertical Inline Multistage | 6000002346 | Manufacturer Standard | 3 |

The three series under `6000002288` are separate product rows linked through the
mapping table. No one-to-one code/series restriction exists. Re-engineered machined
or welded parts `6000011675` have their own commodity row and no pump-model link.
Valves do not inherit pump mappings, even inside a mixed RFQ.

Selecting a series adds its design identifiers to the existing suggested-reference
layer of the Standards view. This never marks them contractually applicable or
certified. Customer-source facts and the engineer's applicability review remain
separate. Editions and licensed clauses are unknown. No curve, model size,
material compatibility, operating limit or current manufacture capability was
created by this integration.

Omega always retains its API 610 deviation warning. When an API 610 requirement
or applicable review exists, ARAMCO-011 explicitly requests configuration-specific
deviation review and acceptance. A BB1 classification or firewater commodity
match does not establish full API 610 compliance.
