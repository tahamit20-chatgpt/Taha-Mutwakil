> Historical Phase 1 baseline. For the current 2.0 upgrade see SYSTEM_ARCHITECTURE.md and TEST_EVIDENCE.md.

# Downloadable local package validation

The ChatGPT workspace has no supported preview URL, port-forwarding tool or externally addressable application URL. No external preview was created or claimed. A remote loopback response is not evidence of access from your browser. The ZIP is the supported fallback deliverable and runs the application on your own computer.

## Included

Complete source and migrations, prebuilt React UI, Python requirements/lockfile, npm manifests/locks, local Dockerfiles/Compose, Windows and macOS/Linux launchers, `.env.example`, synthetic TXT/PDF fixtures, tests, system specifications, development/operations documentation and a SHA-256 file manifest. Docker images and platform-specific dependency binaries are downloaded at first build, not bundled as an offline installation.

Excluded: real `.env` files, `.git`, virtualenvs, node_modules, sessions/signing secrets, database contents, object-store contents, workspace logs, browser profiles and test-result directories. The example is regenerated from synthetic fixtures via the local API, not by shipping an authenticated database/session.

## Executed checks

- Built all app/init/worker/storage Docker images with the locked dependencies. Cloud build networking required build-only proxy DNS mappings and the platform trusted CA supplied as a transient BuildKit secret. These workspace settings/certificates/credentials are **not in the ZIP**. TLS verification was preserved. Typical Docker Desktop builds use their own normal network/trust configuration.
- Started an isolated Compose project with an independent PostgreSQL database and document volumes. Required initializer completed and database, object store and API readiness checks passed. Only API port was published, bound to host loopback; DB and storage had no host port mappings.
- Fixed S3 emulator path-style routing for Docker DNS hostnames. Non-root application files are readable, and runtime storage is writable on its dedicated volume.
- Ran the synthetic PDF seed through the actual separate worker: 10 reviewed facts with physical page 2 citations, fictional demo GO. After rebuilding/restarting containers, the seed found the existing example and did not duplicate it.
- **21 backend tests passed inside the Docker app image** in 17.08 seconds. Deprecation warnings and read-only optional pytest-cache warnings were reported, not skipped/failed tests. The test database is distinct from the application's demo database.
- **2 Chromium browser tests passed against the separate Docker application**, in 8.0 seconds: create project, upload, wait for the separate worker, accept/correct source facts, evaluate GO or missing-data abstention, download and inspect JSON report. Frontend TypeScript/build succeeded during Docker build.
- Shell launcher syntax validated; ZIP extracted, Compose configuration validated from the extracted directory, and every included file checked against its manifest. ZIP CRC validation passed.
- Native Windows/macOS desktop execution and automatic GUI browser opening were **not executed here**; this host is Linux x86-64. Both platform instructions/launchers are supplied. Docker Desktop's normal platform/network prerequisites still apply.

No public hosting, tunnels, paid service purchase or real-model calls were performed. Existing engineering/auth/provider/production gaps remain as documented in ARCHITECTURE.md.
