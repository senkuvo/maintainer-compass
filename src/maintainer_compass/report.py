from __future__ import annotations

import json
from dataclasses import asdict

from .scanner import ScanResult


def render_text(result: ScanResult) -> str:
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


def render_markdown(result: ScanResult) -> str:
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
    for finding in result.findings:
        status = "pass" if finding.passed else "needs attention"
        lines.append(f"- **{status}:** {finding.title} ({finding.category}, {finding.points} pts)")
        if not finding.passed:
            lines.append(f"  - {finding.help_text}")
    return "\n".join(lines)


def render_json(result: ScanResult) -> str:
    payload = {
        "path": str(result.path),
        "score": result.score,
        "earned": result.earned,
        "possible": result.possible,
        "categories": [asdict(category) for category in result.categories],
        "findings": [asdict(finding) for finding in result.findings],
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def render(result: ScanResult, output_format: str) -> str:
    if output_format == "text":
        return render_text(result)
    if output_format == "markdown":
        return render_markdown(result)
    if output_format == "json":
        return render_json(result)
    raise ValueError(f"Unsupported format: {output_format}")
