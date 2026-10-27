"""Create only the isolated test database, then run API/domain tests."""
import os, subprocess
import psycopg
url=os.getenv('TEST_DATABASE_URL','postgresql://bidfit:local-synthetic-only@127.0.0.1:55432/bidfit_test')
assert url.rsplit('/',1)[1].endswith('_test')
with psycopg.connect(url.rsplit('/',1)[0]+'/postgres',autocommit=True) as conn:
    if not conn.execute('SELECT 1 FROM pg_database WHERE datname=%s',(url.rsplit('/',1)[1],)).fetchone():
        from psycopg import sql
        conn.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(url.rsplit('/',1)[1])))
raise SystemExit(subprocess.call(['.venv/bin/pytest','backend/tests','-q'],env={**os.environ,'PYTHONPATH':'backend'}))
