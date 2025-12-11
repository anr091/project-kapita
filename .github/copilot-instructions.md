## Purpose

This file guides AI coding agents (like Copilot or other assistants) to be productive in this repo. It focuses on the concrete architecture, key files, developer workflows, and project-specific conventions discovered in the codebase so the agent can make safe, minimal, and correct changes.

## Big picture

- **Framework/entrypoint**: The app is a Flask web application. The entrypoint is `app.py` which creates `app`, registers blueprints, and calls `app.run(...)` for local development.
- **Main packages**: `common/` contains core modules: `api_controller.py`, `login_manager.py`, `MongoConnection.py`, `session_manager.py`, `user_creator.py`, `config.py`.
- **UI**: HTML templates live in `templates/` and static assets in `static/` (see `static/assets/management-users/`). Templates are rendered with variables like `name`, `role`, `Perm`, `title`, `dbDat`.
- **Data**: MongoDB integration is centralized in `common/MongoConnection.py` and used across controllers.
- **Auth/session**: Authentication/session checks are performed through `common/login_manager.py` and `common/session_manager.py`. Many routes rely on `g.user` being set.

## Key files to read first

- `app.py` — app entry + route examples and blueprint registration.
- `common/api_controller.py` — API blueprint(s), `dashboardDataFetch()` and other server-side data assembly.
- `common/MongoConnection.py` — DB connection factory and usage patterns.
- `common/login_manager.py` — user blueprint, `check_login()` and how sessions are validated.
- `templates/*.html` — front-end expectations for rendering context variables.
- `tests/` and `conftest.py` — test fixtures and examples of how components are exercised.

## Developer workflows (concrete commands)

- Run local dev server: `python app.py` (dev mode: `app.run(debug=True)` in `app.py`).
- Run tests: `pytest tests/ -vv`
- Container build / CI: see `Dockerfile` and `cloudbuild.yaml` for image and cloud build configuration.
- Performance testing: `tests/k6-testing.js` (k6 script) — run with `k6 run tests/k6-testing.js` if k6 is installed.

## Project-specific conventions & patterns

- Blueprints: API and user auth are provided as Flask blueprints (`API_BP`, `user_bp`) defined in `common/api_controller.py` and `common/login_manager.py` respectively — register new routes as blueprints, not by patching `app.py` unless global behavior is required.
- Global request user: handlers expect `g.user` to be populated by `check_login()`; many templates assume `g.user` fields like `name`, `roleName`, `rolePerm`, `firstLogon`.
- DB access: use helper functions in `common/MongoConnection.py`; prefer using existing helper wrappers rather than creating new ad-hoc connections.
- Template contract: when rendering templates, pass `title` and `Perm` consistently; follow existing variable names rather than inventing synonyms.
- Secret handling: `app.secret_key` is set in `app.py` currently. Be cautious changing it — tests and session logic may depend on predictable session behavior in CI/dev.

## Integration points & external deps

- Database: MongoDB via `common/MongoConnection.py` (check `common/config.py` for connection details).
- Dependencies: see `requirements.txt` for Python packages; the repo contains a `Dockerfile` and `cloudbuild.yaml` for CI/build.
- Tests use `pytest`; `conftest.py` contains fixtures that mock or configure DB/session for tests — read it before changing tests or fixtures.

## When making changes

- Read the three key modules (`app.py`, `common/login_manager.py`, `common/api_controller.py`) before touching routes or authentication.
- Maintain template variable contracts — update both the view (controller) and template together.
- Update or add tests in `tests/` alongside behavior changes. Run `pytest tests/ -vv` locally.
- Avoid hardcoding credentials or secrets in commits. If a secret must change, note where tests/fixtures reference the value.

## Example micro-tasks (how to implement safely)

- Add a new API route: put it in `common/api_controller.py` as part of `API_BP`, use existing DB helpers, add a small unit test in `tests/`.
- Fix a template variable bug: search `templates/` for the variable name, update the controller function in `app.py` or the blueprint that renders it, then run tests that exercise that page.

## If you need clarification

- Ask for which files/features to prioritize. If behavior depends on external services (Mongo, cloud build), ask for local test credentials or a dev snapshot of the DB.

## Notes for merging with prior instructions

No existing `.github/copilot-instructions.md` was found. If merging with future content, preserve any project-specific run commands and the `app.py`/`common/` mapping.

-- End
