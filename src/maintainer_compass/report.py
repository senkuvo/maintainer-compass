from __future__ import annotations

import json
from dataclasses import asdict

from .scanner import ScanResult


def render_text(result: ScanResult, *, only_failures: bool = False) -> str:
    lines = [
        f"Maintainer Compass report for {result.path.name}",
        f"Score: {result.score}/100 ({result.earned}/{result.possible} points)",
        "",
        "Category          Score",
    ]
    for category in result.categories:
        lines.append(f"{category.category:<17} {category.earned}/{category.possible}")

    if result.failures:
        lines.extend(["", "Needs attention"])
        for finding in result.failures:
            lines.append(f"- {finding.title}: {finding.help_text}")
    else:
        lines.extend(["", "No missing checks found. Nice maintenance posture."])
    return "\n".join(lines)


def render_markdown(result: ScanResult, *, only_failures: bool = False) -> str:
    lines = [
        f"# Maintainer Compass Report: {result.path.name}",
        "",
        f"**Score:** {result.score}/100 ({result.earned}/{result.possible} points)",
        "",
        "## Category Scores",
        "",
        "| Category | Score |",
        "| --- | ---: |",
    ]
    for category in result.categories:
        lines.append(f"| {category.category} | {category.earned}/{category.possible} |")

    lines.extend(["", "## Findings", ""])
    findings = result.failures if only_failures else result.findings
    if not findings:
        lines.append("No missing checks found.")
        return "\n".join(lines)

    for finding in findings:
        status = "pass" if finding.passed else "needs attention"
        lines.append(f"- **{status}:** {finding.title} ({finding.category}, {finding.points} pts)")
        if not finding.passed:
            lines.append(f"  - {finding.help_text}")
    return "\n".join(lines)


def render_json(result: ScanResult, *, only_failures: bool = False) -> str:
    findings = result.failures if only_failures else result.findings
    payload = {
        "path": str(result.path),
        "score": result.score,
        "earned": result.earned,
        "possible": result.possible,
        "only_failures": only_failures,
        "categories": [asdict(category) for category in result.categories],
        "findings": [asdict(finding) for finding in findings],
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def render(result: ScanResult, output_format: str, *, only_failures: bool = False) -> str:
    if output_format == "text":
        return render_text(result, only_failures=only_failures)
    if output_format == "markdown":
        return render_markdown(result, only_failures=only_failures)
    if output_format == "json":
        return render_json(result, only_failures=only_failures)
    raise ValueError(f"Unsupported format: {output_format}")
