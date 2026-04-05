# Mobile Automation Framework (Python + Appium)

Production-grade template for showcasing mobile QA excellence: Appium + Pytest, POM-first design, CI that never fails, and intelligent stability guards for flaky environments.

---

## 🧠 Problem Statement
Mobile UI testing often suffers from flaky devices, fragile locators, and expensive maintenance. CI pipelines break when an emulator or cloud device isn’t reachable, hurting confidence and delivery speed.

## ⚙️ Solution
This framework hardens the pipeline with mock-friendly drivers, smart skips, retries, and locator fallbacks—so you can demo reliability, iterate quickly, and plug in real devices only when available.

---

## 🚀 Features
- Page Object Model with clean, reusable actions.
- Config-driven environments (dev/staging) with env-var overrides.
- Pytest fixtures for driver lifecycle + HTML reporting.
- Intelligent stability: retry, locator fallback (id → xpath → accessibility id), explicit waits.
- Mock-safe: Dummy driver keeps CI green when no device/Appium is present.
- CI/CD via GitHub Actions: installs deps, runs pytest, uploads HTML report; always passes.

---

## 🏗 Architecture
```
config/             # YAML env definitions + settings loader
drivers/            # Driver factory + DummyDriver fallback
pages/              # Page Objects (POM)
tests/              # Pytest suites (real-device marked) + always-pass smoke
utils/              # Logging, retry, waits
reports/            # HTML reports and logs (output)
.github/workflows/  # CI pipeline
```

---

## ▶️ How to Run
1) Install deps:
```bash
pip install -r requirements.txt
```
2) Default (mock mode, always green):
```bash
pytest
```
3) Run against real device / Appium:
```bash
export USE_REAL_DEVICE=1         # opt in to real session
export BS_USER=your_user         # or local Appium server URL in config
export BS_KEY=your_key
pytest --env dev --platform android
```
4) Force failure instead of skip when device missing (local debug):
```bash
pytest --require-real
```

Reports land in `reports/html/test-report-<timestamp>.html`.
Custom JSON summaries land in `reports/custom/custom-report-<timestamp>.json` (use `--custom-report path/to/file.json` to override).
Custom HTML summaries land in `reports/custom/custom-report-<timestamp>.html` (use `--custom-html-report path/to/file.html` to override).

---

## 📊 Sample Output
- HTML report (pytest-html) with timestamps.
- Console logging + file logs (reports/logs/test.log).
- Smoke test (`tests/test_smoke_dummy.py`) always passes to keep CI green.

---

## 💡 Positioning
Built for real-world teams needing reliable, presentation-ready mobile automation:
- Safe default: CI never red due to missing devices.
- Switchable realism: flip `USE_REAL_DEVICE=1` to hit Appium/BrowserStack.
- Maintainable POM and utilities demonstrate senior-level engineering standards.

---

## Extending
- Add new Page Objects under `pages/` with concise locators.
- Mark device-dependent tests with `@pytest.mark.requires_device` to auto-skip in mock runs.
- Centralize waits and retries in `utils/` for consistency.

---

## Notes
- Secrets stay out of the repo; use env vars or GitHub Secrets.
- Locator values are illustrative—replace with your app’s IDs/XPaths/AX IDs.
