import os
os.environ['DATABASE_URL']=os.getenv('TEST_DATABASE_URL','postgresql+psycopg://bidfit:local-synthetic-only@127.0.0.1:55432/bidfit_test')
os.environ['S3_BUCKET']='bidfit-tests-private'
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import Base,engine
from app.documents.storage import initialize
@pytest.fixture(autouse=True)
def clean_test_db():
    assert engine.url.database.endswith('_test'), 'Never clear a non-test database'
    Base.metadata.drop_all(engine);Base.metadata.create_all(engine);initialize()
@pytest.fixture
def client():
    with TestClient(app) as c:
        login(c,'alice');yield c

def login(client,name):
    r=client.post('/api/v1/auth/demo/'+name,headers={'X-BidFit-Demo':'local'})
    assert r.status_code==200,r.text
    client.headers['X-CSRF-Token']=r.json()['csrf']
    return r.json()
