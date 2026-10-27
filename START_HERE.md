# Windows users: start here

Read **WINDOWS-START-HERE.txt** or open **WINDOWS_START_HERE.html** in Chrome. Install/open Docker Desktop, then double-click **START_BIDFIT_WINDOWS.bat**. No Python, Node.js or Git installation is required. Use **STOP_BIDFIT_WINDOWS.bat** to stop while keeping local data. This package is synthetic-only and requires first-run internet downloads.

# Open BidFit on your own computer

This is the runnable local BidFit prototype. **The ChatGPT cloud workspace has no supported browser preview or port-forwarding tool. This download runs on your computer instead.** Nothing is published to the internet.

## What you need

- Windows or macOS with **Docker Desktop installed and running**, using Linux containers. Docker Desktop includes Docker Compose. Linux users can use Docker Engine + Compose v2.
- Internet for the first build to download container images and pinned Python/npm dependencies. This ZIP includes source, built UI, dependency manifests/lockfiles, synthetic PDF/TXT fixtures, tests and launchers. It is **not an offline installer**: Docker images and OS-specific dependency binaries are not bundled.
- No Python, Node, database installation or paid AI/API key is required on your computer.

## Windows

1. Extract **the whole ZIP** to a normal folder (not inside the ZIP viewer).
2. Open Docker Desktop; wait for the engine to be ready.
3. Double-click **start-local.bat**. Keep the window open during the first build.
4. When database/storage/API readiness checks pass, the launcher creates the synthetic example and opens your browser automatically.

If Windows marks a downloaded launcher as blocked, you can instead open PowerShell in the extracted folder and run the explicit Docker commands in `docs/LOCAL_START.md`. The Windows launcher itself has not been executed on Windows in this workspace.

## macOS

1. Extract the whole ZIP. Open Docker Desktop and wait until it is ready.
2. Open Terminal, type `cd ` (with a trailing space), drag the extracted **BidFit-MVP** folder into Terminal, and press Enter.
3. Run:

   ```bash
   bash start-local.sh
   ```

4. The launcher waits for readiness, creates the synthetic example and opens your default browser. No macOS system startup changes are needed. The launcher has been checked in Linux; native macOS execution has not been verified here.

## Try the workflow

- Enter the local demo as **Alice (engineer)**.
- Open **Example — reviewed synthetic cooling-water RFQ** to inspect a completed synthetic PDF workflow and export a report.
- To do it yourself: create a project with tag `P-101`, upload `fixtures/synthetic/go.txt` or `go.pdf`, wait for processing, review/accept each proposed fact, run technical evaluation, and export HTML/JSON/CSV.
- Use `conditional.txt`, `no-go.txt`, `missing.txt` and `conflict.txt` in separate projects to inspect the other decisions and unresolved conflicts.

**Synthetic demonstration only. Pattern extraction is not AI. Fictional rules and demo approvals/materials do not represent KSB data or validated engineering conclusions. Use no confidential files.**

## Stop or restart

Open a terminal in this folder:

```bash
docker compose --env-file .env -f compose.local.yml down
```

Run the same launcher again to restart. Database and original-document Docker volumes persist. Do **not** add `--volumes` to the stop command if you want to keep your work.

If port 8000 is busy, edit the generated `.env` and change `BIDFIT_PORT=8000` to `BIDFIT_PORT=8001`, then rerun the launcher. It opens the actual mapped local address; there is no cloud URL.

More: `docs/LOCAL_START.md`, `docs/ARCHITECTURE.md`, `docs/VALIDATION.md`, `docs/CONFIGURATION.md`, `README.md`. The Docker Compose profile publishes only the app and binds it to your computer's loopback address; PostgreSQL and object storage stay inside the private Docker network. Do not change that binding or use this local demo as public hosting.
