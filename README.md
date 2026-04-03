# Mobile App Automation Framework

Production-ready Python framework for Android/iOS UI tests using Appium and Pytest. Built with Page Object Model, environment-aware config, retry/fallback helpers, and CI-ready reporting.

## Architecture
- `config/` – YAML-driven environment config (`dev`, `staging`) resolved by `config/settings.py` with env-var overrides for secrets.
- `drivers/` – Driver factory and locator fallback utilities.
- `pages/` – Page Objects encapsulating screen locators and actions.
- `tests/` – Pytest suites using fixtures; sample login and navigation specs included.
- `utils/` – Logging and retry helpers.
- `reports/` – HTML reports and logs output directory.
- `.github/workflows/` – GitHub Actions pipeline to run tests and archive reports.

## Features
- Page Object Model for maintainability and reuse.
- Pytest fixtures for driver lifecycle, creds, and report wiring.
- Configurable environments/platforms via `--env` and `--platform` or env vars.
- Locator fallback helper to try alternate strategies when primary fails.
- Lightweight retry helper for flaky actions plus `pytest-rerunfailures` (1 retry by default).
- Structured logging to console and file.
- HTML reporting with `pytest-html`; timestamped report path.
- CI/CD: GitHub Actions runs tests on pushes/PRs and uploads reports.

## Setup
1) Install dependencies:
```bash
pip install -r requirements.txt
```
2) Provide BrowserStack/App paths via env vars (recommended) or edit `config/environments/*.yaml`:
```bash
export BS_USER=your_user
export BS_KEY=your_key
export APP_URL=bs://your-app-id   # optional override per run
export TEST_EMAIL=demo@example.com
export TEST_PASS=Password!23
```
3) Start Appium server if using local devices (`appium` on port 4723) or ensure BrowserStack credentials are set.

## Running Tests
- Default (dev/android):
```bash
pytest
```
- Specify env/platform:
```bash
pytest --env staging --platform ios
```
HTML report is written to `reports/html/test-report-<timestamp>.html`.

## CI/CD
GitHub Actions workflow `.github/workflows/ci.yml`:
- Sets up Python and dependencies.
- Runs `pytest --env dev --platform android --maxfail=1`.
- Uploads HTML report artifact for download.

## Sample Tests
- `tests/test_login.py` – Logs in and asserts user lands on chat tab.
- `tests/test_navigation.py` – Navigates to Calls tab after login.

## Extending
- Add new screens in `pages/` with clear locators and actions.
- Keep locators platform-specific via capabilities or conditional locators.
- Share cross-cutting helpers in `utils/`.

## Notes
- Secrets should be passed as env vars; YAML contains placeholders only.
- Locator names are illustrative—replace with real IDs/XPaths for your app.
