"""Run only isolated demo test DB tests inside the local Docker application image."""
import os,sys,subprocess
import psycopg
from psycopg import sql
from sqlalchemy.engine import make_url
url=make_url(os.environ['DATABASE_URL'])
name=(url.database or 'bidfit')+'_test'
assert name.endswith('_test')
with psycopg.connect(host=url.host,port=url.port or 5432,user=url.username,password=url.password,dbname='postgres',autocommit=True) as conn:
    if not conn.execute('SELECT 1 FROM pg_database WHERE datname=%s',(name,)).fetchone():
        conn.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(name)))
env={**os.environ,'TEST_DATABASE_URL':url.set(database=name).render_as_string(hide_password=False)}
raise SystemExit(subprocess.call([sys.executable,'-m','pytest','backend/tests','-q'],env=env))
