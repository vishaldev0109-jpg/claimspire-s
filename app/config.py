"""Local prototype configuration. No AWS account or credentials required."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./claimspire_admin.db')
JWT_SECRET = os.getenv('JWT_SECRET', 'local-demo-secret-do-not-use-in-production')
JWT_EXPIRE_MINUTES = int(os.getenv('JWT_EXPIRE_MINUTES', '120'))
SEED_DEMO_DATA = os.getenv('SEED_DEMO_DATA', 'true').strip().lower() in ('1', 'true', 'yes')
