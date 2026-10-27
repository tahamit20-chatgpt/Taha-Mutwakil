# Local operation and future release gates

Run `infra/dev.py` from the existing isolated repository checkout. Do not create a worktree. Retained state: PostgreSQL Docker volume, `.runtime/objects`, `.runtime/session-secret`, dependency caches/build output. Live processes must restart. The supervisor checks occupied ports instead of killing existing services. Logs are under ignored `.runtime/`; do not log confidential documents there. This demo has no public deployment.

Readiness: `GET /api/v1/ready` must report database and object storage `ok`; it does not prove authentication/provider production readiness. Failed jobs are visible with bounded retries. Reclaimed leases preserve idempotency; completion inserts facts/pages and marks the job done atomically. After a permanent failure, upload corrected source with a new idempotency key/document version. Coverage gaps remain unresolved; removing relevant evidence from consideration needs an approved policy (not provided).

Synthetic backup rehearsal (requires quiescing the demo first):

1. Ctrl+C the supervisor. Keep the database container running.
2. `mkdir -p .runtime/backup`
3. `docker compose -f infra/compose.yml exec -T db pg_dump -U bidfit -Fc bidfit > .runtime/backup/bidfit.dump`
4. `tar -czf .runtime/backup/objects.tgz .runtime/objects .runtime/session-secret`
5. Restore **only to a new isolated database/storage directory**, never overwrite an unrelated active checkout. Create a separate database and `pg_restore` the dump there, restore objects to an isolated path, configure endpoint/DB accordingly, run readiness and verify one original SHA/report hash before use.

Backup commands are a runbook; no managed recovery SLA or production restore certification is claimed. RPO/RTO, encrypted backups, offsite retention, object versioning, legal holds, deletion and incident response require owner policy and an actual rehearsal before real data. For an incident, stop demo processes, retain minimal logs, revoke server sessions and rotate configured secrets through secure settings, then investigate in isolation.
