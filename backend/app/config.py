import os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+psycopg://bidfit:local-synthetic-only@127.0.0.1:55432/bidfit')
S3_ENDPOINT = os.getenv('S3_ENDPOINT', 'http://127.0.0.1:59000')
S3_BUCKET = os.getenv('S3_BUCKET', 'bidfit-private')
DEMO = os.getenv('BIDFIT_MODE', 'demo') == 'demo'
PROVIDER = os.getenv('EXTRACTION_PROVIDER', 'demo')
