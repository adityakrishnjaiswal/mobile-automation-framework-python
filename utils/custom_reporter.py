"""Lightweight custom pytest reporter that writes a JSON summary to disk.

The reporter collects per-test outcomes and durations and stores them in a
self-contained JSON file under ``reports/custom`` by default. A custom output
path can be provided with ``--custom-report``.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from _pytest.reports import TestReport


class CustomJsonReporter:
    """Aggregate test results and persist them as JSON."""

    def __init__(self, config):
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_opt = config.getoption("--custom-report")
        default_path = Path("reports/custom") / f"custom-report-{timestamp}.json"
        self.report_path = Path(output_opt) if output_opt else default_path
        self.report_path.parent.mkdir(parents=True, exist_ok=True)

        self.results: List[Dict[str, object]] = []
        self.session_start = datetime.now()

    # pytest hook
    def pytest_runtest_logreport(self, report: TestReport) -> None:  # noqa: D401
        """Capture the outcome for each test (including skips)."""
        if report.when != "call" and not report.skipped:
            return

        entry: Dict[str, object] = {
            "nodeid": report.nodeid,
            "outcome": report.outcome,
            "duration_seconds": round(report.duration or 0.0, 4),
            "stage": report.when,
        }

        if report.skipped and report.longrepr:
            entry["reason"] = _extract_skip_reason(report)
        if report.failed and report.longrepr:
            entry["longrepr"] = str(report.longrepr)
        if getattr(report, "wasxfail", None):
            entry["wasxfail"] = report.wasxfail

        self.results.append(entry)

    # pytest hook
    def pytest_sessionfinish(self, session, exitstatus):  # noqa: D401
        """Write aggregated results to disk at the end of the run."""
        finished = datetime.now()
        summary = {
            "session_start": self.session_start.isoformat(),
            "session_end": finished.isoformat(),
            "duration_seconds": round((finished - self.session_start).total_seconds(), 4),
            "exitstatus": exitstatus,
            "counts": _tally(self.results),
            "results": self.results,
        }
        self.report_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

        terminal = session.config.pluginmanager.getplugin("terminalreporter")
        if terminal:
            terminal.write_line(f"Custom JSON report written to {self.report_path}")


def _tally(results: List[Dict[str, object]]) -> Dict[str, int]:
    totals: Dict[str, int] = {"total": len(results)}
    for outcome in ["passed", "failed", "skipped", "xfailed", "xpassed"]:
        totals[outcome] = sum(1 for r in results if r.get("outcome") == outcome)
    return totals


def _extract_skip_reason(report: TestReport) -> str:
    if isinstance(report.longrepr, tuple) and len(report.longrepr) >= 3:
        return str(report.longrepr[2])
    return str(report.longrepr)


__all__ = ["CustomJsonReporter"]
