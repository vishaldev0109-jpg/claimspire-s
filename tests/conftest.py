import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.main import app
from app.seed import seed_demo_data
from app.demo_extensions import seed_admin_extensions

@pytest.fixture(scope='module')
def client():
    engine = create_engine('sqlite+pysqlite://', connect_args={'check_same_thread':False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    with factory() as db:
        seed_demo_data(db)
        seed_admin_extensions(db)

    def override_db():
        with factory() as db:
            yield db

    app.dependency_overrides[get_db] = override_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)
    engine.dispose()

@pytest.fixture(scope='module')
def platform_headers(client):
    r=client.post('/api/v1/auth/login',json={'email':'platform@claimspire.local','password':'DemoAdmin123!'})
    assert r.status_code==200,r.text
    return {'Authorization':'Bearer '+r.json()['access_token']}

@pytest.fixture(scope='module')
def harbor_headers(client):
    r=client.post('/api/v1/auth/login',json={'email':'admin@harbor.local','password':'DemoAdmin123!'})
    assert r.status_code==200,r.text
    return {'Authorization':'Bearer '+r.json()['access_token']}
