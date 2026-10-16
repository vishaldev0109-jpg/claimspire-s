# Corrected ClaimSpire Admin demo — Mac instructions

**This ZIP contains the Admin interface** (not only the FastAPI endpoints). It lives in a differently named folder to avoid accidentally running the original API-only starter.

1. Stop any old running server with `Ctrl+C` in its terminal.
2. Unzip `ClaimSpire_Admin_Demo_FIXED.zip` into Downloads.
3. In Terminal:

```bash
cd ~/Downloads/ClaimSpire_Admin_Demo_FIXED
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload
```

4. Visit **http://127.0.0.1:8000/** (redirects to **/demo**).
5. Demo login: **platform@claimspire.local** / **DemoAdmin123!**.
6. Swagger is at **http://127.0.0.1:8000/docs**.

Quick checks:

```bash
curl -i http://127.0.0.1:8000/
curl -i http://127.0.0.1:8000/demo
curl -s http://127.0.0.1:8000/health
```

The health response should include `"demo_ui": true`, and `/demo` should return `HTTP/1.1 200 OK`. If health does **not** include `demo_ui`, you are still running an old API-only version or a different app. Stop it, check your working directory with `pwd`, and restart from the new folder. The project uses local SQLite and synthetic data; AWS is not required.

This is a nonproduction demonstration. Do not deploy with the included demo JWT secret or credentials.


## New in v0.3
Open **Organization Setup** to review/complete an organization, then **Workforce Lifecycle** to see teams and staff availability. To demonstrate the submit → approval handoff, log in first as `admin@harbor.local`, complete Harbor's missing sections and submit, then sign in as `platform@claimspire.local` to approve. Or simply sign in as Platform Ops and approve Summit's already-submitted IA setup. All data is local and synthetic.
