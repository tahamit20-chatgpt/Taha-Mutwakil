# Selection and commercial foundations

Selection Studio consumes the same RFQ tag/accepted requirement context. Engineers can reference a tenant-scoped product family and manual model/evidence, then append reference review. Category mismatch, cross-tenant IDs and stale input hashes are rejected. Candidate status remains UNVERIFIED; a reference review does not certify performance. No curves, pump models, efficiency, NPSHR, motor choice, approvals or compatibility are generated.

`backend/app/knowledge/adapters.py` defines approved-performance and ICAP source contracts with explicit NotConfigured implementations. There is no proprietary browser/Claude/EasySelect dependency. Actual adapter activation requires authorized source scope, approved curves/conditions, validation and secure configuration.

Pricing Studio stores manually sourced draft references with price kind/currency/validity/revision; it does not invent totals/margins or turn historical prices into current approved prices. Approved Selling Price is rejected until approval infrastructure exists. ICAP is marked Requires Configuration.

Quotation Studio creates versioned immutable technical draft exports from a current frozen evaluation and a versioned demonstration template. Missing product configuration, prices, terms and submission approval remain explicit. It never copies unapproved pricing references into a selling-price promise. Full technical/commercial templates, live approval and submission automation are future packages.
