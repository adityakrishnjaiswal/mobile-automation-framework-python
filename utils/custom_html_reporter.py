"""Lightweight custom HTML reporter for pytest.

The reporter renders a standalone HTML page summarizing test outcomes. It is
designed to be CI-friendly and independent of pytest-html. Use
``--custom-html-report`` to override the output path.
"""

from __future__ import annotations

from datetime import datetime
from html import escape
from pathlib import Path
from typing import Dict, List

from _pytest.reports import TestReport


class CustomHtmlReporter:
    """Aggregate test results and persist them as HTML."""

    def __init__(self, config):
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_opt = config.getoption("--custom-html-report")
        default_path = Path("reports/custom") / f"custom-report-{timestamp}.html"
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
            "session_start": self.session_start,
            "session_end": finished,
            "duration_seconds": round((finished - self.session_start).total_seconds(), 4),
            "exitstatus": exitstatus,
            "counts": _tally(self.results),
            "results": self.results,
        }

        html = _render_html(summary)
        self.report_path.write_text(html, encoding="utf-8")

        terminal = session.config.pluginmanager.getplugin("terminalreporter")
        if terminal:
            terminal.write_line(f"Custom HTML report written to {self.report_path}")


def _render_html(summary: Dict[str, object]) -> str:
    counts = summary["counts"]
    rows = [
        _render_row(entry)
        for entry in summary["results"]
    ]

    return """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <title>Custom Test Report</title>
  <style>
    body { font-family: -apple-system, Segoe UI, sans-serif; margin: 24px; color: #0f172a; }
    h1 { margin-bottom: 8px; }
    .meta { color: #475569; margin-bottom: 16px; }
    .summary { display: flex; gap: 8px; margin-bottom: 16px; }
    .badge { padding: 6px 10px; border-radius: 6px; font-weight: 600; }
    .passed { background: #ecfdf3; color: #166534; }
    .failed { background: #fef2f2; color: #991b1b; }
    .skipped { background: #f8fafc; color: #334155; }
    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 8px 10px; border-bottom: 1px solid #e2e8f0; text-align: left; }
    th { background: #f1f5f9; }
    .nodeid { word-break: break-word; }
    .pill { padding: 4px 8px; border-radius: 999px; font-size: 12px; font-weight: 600; display: inline-block; }
    .pill.passed { background: #dcfce7; color: #166534; }
    .pill.failed { background: #fee2e2; color: #991b1b; }
    .pill.skipped { background: #e2e8f0; color: #334155; }
  </style>
</head>
<body>
  <h1>Custom Test Report</h1>
  <div class=\"meta\">
    <div>Session start: {start}</div>
    <div>Session end: {end}</div>
    <div>Duration: {duration}s | Exit status: {exitstatus}</div>
  </div>
  <div class=\"summary\">
    <div class=\"badge passed\">Passed: {passed}</div>
    <div class=\"badge failed\">Failed: {failed}</div>
    <div class=\"badge skipped\">Skipped: {skipped}</div>
    <div class=\"badge\">Total: {total}</div>
  </div>
  <table>
    <thead>
      <tr><th>Test</th><th>Outcome</th><th>Duration (s)</th><th>Details</th></tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>
</body>
</html>
""".format(
        start=summary["session_start"].isoformat(timespec="seconds"),
        end=summary["session_end"].isoformat(timespec="seconds"),
        duration=summary["duration_seconds"],
        exitstatus=summary["exitstatus"],
        passed=counts.get("passed", 0),
        failed=counts.get("failed", 0),
        skipped=counts.get("skipped", 0),
        total=counts.get("total", 0),
        rows="\n      ".join(rows),
    )


def _render_row(entry: Dict[str, object]) -> str:
    outcome = entry.get("outcome", "")
    detail_parts = []
    if entry.get("reason"):
        detail_parts.append(f"Reason: {escape(str(entry['reason']))}")
    if entry.get("longrepr"):
        detail_parts.append(f"Trace: {escape(str(entry['longrepr']))}")
    if entry.get("wasxfail"):
        detail_parts.append(f"xfail: {escape(str(entry['wasxfail']))}")

    details = "<br>".join(detail_parts) if detail_parts else ""

    return "<tr><td class='nodeid'>{node}</td><td><span class='pill {cls}'>{outcome}</span></td><td>{duration}</td><td>{details}</td></tr>".format(
        node=escape(str(entry.get("nodeid", ""))),
        cls=escape(outcome),
        outcome=escape(outcome),
        duration=entry.get("duration_seconds", 0),
        details=details,
    )


def _tally(results: List[Dict[str, object]]) -> Dict[str, int]:
    totals: Dict[str, int] = {"total": len(results)}
    for outcome in ["passed", "failed", "skipped", "xfailed", "xpassed"]:
        totals[outcome] = sum(1 for r in results if r.get("outcome") == outcome)
    return totals


def _extract_skip_reason(report: TestReport) -> str:
    if isinstance(report.longrepr, tuple) and len(report.longrepr) >= 3:
        return str(report.longrepr[2])
    return str(report.longrepr)


__all__ = ["CustomHtmlReporter"]
