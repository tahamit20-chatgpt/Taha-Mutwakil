# BidFit — Phase 1 synthetic prototype

**Windows beginner? Open WINDOWS-START-HERE.txt or WINDOWS_START_HERE.html first.**

A working RFQ → cited requirements → engineer review → deterministic technical screening → frozen report workflow. **Demonstration only: no genuine AI extraction in demo mode, no validated engineering conclusions, no KSB product data.**

Repository: `tahamit20-chatgpt/Taha-Mutwakil`; implementation branch `bidfit/phase1`. The checkout was empty (no commits or files) when work began. The three supplied specifications are preserved under `docs/specifications/`.

## Browser access from a downloaded ZIP

If you use ChatGPT without an IDE, read [START_HERE.md](START_HERE.md). The packaged Docker launcher runs the app on your own computer with no separate Python/Node installation. There is no supported externally accessible cloud preview in this chat.

## Start locally

Prerequisites: Python 3.12, uv, Node 24, npm, Docker with Compose. Use the existing isolated checkout; no worktree is needed.

```bash
cd /workspace/Taha-Mutwakil
./infra/install.sh
.venv/bin/python infra/dev.py
```

Open `http://127.0.0.1:8000` in a browser on the same machine, or forward port 8000 over your development connection. The cloud onboarding UI does not provide a hosted preview. API documentation: `/docs`. The supervisor starts PostgreSQL, private loopback S3 emulator, API/static UI and separate durable worker. It waits for readiness. Ctrl+C stops its API/worker/storage children; PostgreSQL retains data in a Docker volume. To stop that database: `docker compose -f infra/compose.yml stop db`. Start again using the same command; do not remove the volume or `.runtime/objects` to retain your demo documents.

The prepared instance already includes **Example — reviewed synthetic cooling-water RFQ**. To add it in a fresh instance, run `.venv/bin/python infra/seed_demo.py` while the supervisor is active; it uses only synthetic data and is repeatable.

No credentials are needed for the local synthetic workflow. All bundled database/storage credentials are development-only and must never be exposed publicly. The private S3 emulator is **not** a production storage service.

## Five-minute walkthrough

1. Enter the local demo as Alice (engineer). Create a project with tag `P-101`.
2. Download `go.txt` from the new-project fixture links (or use `fixtures/synthetic/go.txt`). Upload it under Documents. The worker parses it asynchronously.
3. Open Evidence review. Compare source lines with proposed facts, edit a value if desired, and click **Accept / correct** for each fact. Every correction requires a rationale and retains the original quote/raw value. Reject superseded facts, with justification, to resolve contradictory evidence.
4. Open Technical evaluation → Run technical evaluation. The complete fixture produces synthetic **GO**; this only confirms the fictional demo contract, not actual pump suitability.
5. Export HTML (open and print to PDF), JSON or CSV. Each uses the same immutable run and includes its hash and evidence. Later edits do not change old exports.
6. Try separate projects with `conditional.txt`, `no-go.txt`, `missing.txt`, and `conflict.txt` for CONDITIONAL GO, NO-GO, INSUFFICIENT DATA, and unresolved conflict respectively. For `multi-tag.txt`, create tags `P-101, P-102`.
7. Change an accepted head value and re-evaluate. Prior results are marked historical; stale acknowledgement returns 409. Commercial notes are a separate screen and cannot change the technical outcome. Engineer dispositions acknowledge/decline and never rewrite computed results.

Demo extraction recognizes exact `Tag: P-101` headings and `field: value unit` lines. It does not claim to understand arbitrary RFQs. Supported fields and canonical units are in `backend/app/extraction/service.py`; incompatible/ambiguous units remain unknown. Only synthetic English text PDF/TXT is supported; encrypted, invalid, unreadable and unsupported documents produce explicit coverage gaps. A sample two-page PDF is included as `fixtures/synthetic/go.pdf`.

## Validate

Run with the development supervisor active (storage + PostgreSQL required):

```bash
.venv/bin/python infra/test.py
npm --prefix frontend run build
npm --prefix frontend run test:e2e
PYTHONPATH=backend .venv/bin/python infra/benchmark.py
```

Tests use a separate `bidfit_test` database, never clear the demo DB, and make no real model calls. Browser tests use installed `/usr/bin/chromium`; set `CHROMIUM_PATH` for a different executable, or install the Playwright browser if no system Chromium is available.

See [validation](docs/VALIDATION.md), [architecture and remaining gaps](docs/ARCHITECTURE.md), [integration configuration](docs/CONFIGURATION.md), and [operations](docs/OPERATIONS.md). This is the complete first workflow milestone, **not the entire production-readiness contract**.
