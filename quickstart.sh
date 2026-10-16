#!/usr/bin/env bash
set -euo pipefail
if [ ! -d .venv ]; then python -m venv .venv; fi
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
if [ ! -f .env ]; then cp .env.example .env; fi
exec uvicorn app.main:app --reload
