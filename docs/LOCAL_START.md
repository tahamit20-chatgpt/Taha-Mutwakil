# Local package startup and troubleshooting

Start with `START_HERE.md` in the ZIP root. Docker Desktop must be running and use Linux containers. No credentials or external AI calls are required. The first build downloads dependencies; the ZIP is not an offline bundle.

## Explicit commands (Windows PowerShell)

Open PowerShell in the extracted project folder:

```powershell
if (!(Test-Path .env)) { Copy-Item .env.example .env }
docker compose --env-file .env -f compose.local.yml up --build -d --wait --wait-timeout 240
docker compose --env-file .env -f compose.local.yml exec -T api python infra/seed_demo.py
docker compose --env-file .env -f compose.local.yml port api 8000
```

The last command prints the address mapped **on your computer**. Use `http://` followed by that address in your browser. Do not use an address from the remote ChatGPT workspace. If startup fails, do not assume that the app is ready merely because containers exist; inspect the failed service below.

## Explicit commands (macOS / Linux Terminal)

```bash
cp -n .env.example .env
docker compose --env-file .env -f compose.local.yml up --build -d --wait --wait-timeout 240
docker compose --env-file .env -f compose.local.yml exec -T api python infra/seed_demo.py
docker compose --env-file .env -f compose.local.yml port api 8000
```

The convenience `bash start-local.sh` runs these steps and opens your browser. The Windows `.bat` launcher does the same.

## Check / stop / retain data

```bash
docker compose --env-file .env -f compose.local.yml ps
docker compose --env-file .env -f compose.local.yml logs --tail 80
docker compose --env-file .env -f compose.local.yml down
```

`down` stops and removes containers/networks but retains the named volumes holding database, original documents and session state. Rerunning the launcher restores your local work. Do not delete volumes to troubleshoot unless you deliberately want to erase the demo.

## Troubleshooting

- **Docker not found / cannot connect to daemon:** install/open Docker Desktop and wait until it reports ready. On Windows select Linux containers and enable the WSL2 backend if Docker Desktop requests it.
- **Image/package download fails:** the first run requires access to Docker Hub, PyPI/files.pythonhosted.org and registry.npmjs.org. Retry after correcting network/proxy access. Do not disable TLS, signatures or checksums.
- **Port conflict:** change `BIDFIT_PORT` in `.env` to an unused port and rerun the launcher. Never set the host binding to `0.0.0.0` to fix a local port conflict.
- **Login denied:** use Alice's explicit local demo button. Managed OIDC is unconfigured. The Docker-only profile accepts private bridge peers for local demo login; host access is loopback-only, not public authentication.
- **Upload has no facts:** demo extraction expects the documented fixture grammar (`Tag: P-101`, `head: 50 m`, etc.). Unsupported/encrypted/unreadable files remain coverage gaps. This is not real AI extraction.
- **Stale evaluation:** a fact/commercial edit changes the project revision. Run a new technical evaluation. Older reports remain historical.
- **Different desktop architecture:** the Dockerfiles use official multi-architecture images. Linux x86-64 is tested here; Windows Docker Desktop and Apple Silicon/macOS runs are not independently verified. Report any build error rather than weakening dependency verification.

## Tests inside the downloaded stack

Backend tests use an isolated `bidfit_test` DB and the same private storage service, with real-model egress disabled:

```bash
docker compose --env-file .env -f compose.local.yml exec -T api python infra/container_tests.py
```

Browser tests and source development commands are in the original README. They need Node/Chromium locally; they are not prerequisites for using the packaged demo.
