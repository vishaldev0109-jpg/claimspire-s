from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.config import SEED_DEMO_DATA
from app.database import Base, SessionLocal, engine
from app import models  # ensure SQLAlchemy metadata registered
from app.seed import seed_demo_data
from app.demo_extensions import seed_admin_extensions
from app.routers import auth, tenants, people, configuration, operations, audit, readiness, organization

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Prototype convenience only. Production should use versioned migrations.
    Base.metadata.create_all(bind=engine)
    if SEED_DEMO_DATA:
        with SessionLocal() as db:
            seed_demo_data(db)
            seed_admin_extensions(db)
    yield

app=FastAPI(title='ClaimSpire Admin Backend (Local Demo)',version='0.3.0',description='Local-only mock Admin control plane. Synthetic claims/QA/finance, no AWS integration. Not production-ready.',lifespan=lifespan)
# Local UI defaults; change origins for an actual frontend and environment.
app.add_middleware(CORSMiddleware,allow_origins=['http://localhost:3000','http://localhost:5173'],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])

@app.get('/health',tags=['Health'])
def health():
    return {'status':'ok','mode':'local-demo','demo_ui': True,'version':'0.3.0','aws_required':False}

for router in (auth.router,tenants.router,people.router,configuration.router,operations.router,audit.router,readiness.router,organization.router):
    app.include_router(router,prefix='/api/v1')

# Self-contained demo UI; served by FastAPI so no npm, React or additional server is needed.
STATIC_DIR = Path(__file__).parent / 'static'
app.mount('/demo-assets', StaticFiles(directory=STATIC_DIR), name='demo-assets')

@app.get('/demo', include_in_schema=False)
def demo_ui():
    return FileResponse(STATIC_DIR / 'index.html')


# Quality-of-life defaults for browser visits.
@app.get('/', include_in_schema=False)
def home():
    return RedirectResponse(url='/demo', status_code=307)

@app.get('/favicon.ico', include_in_schema=False)
def favicon():
    return Response(status_code=204)
