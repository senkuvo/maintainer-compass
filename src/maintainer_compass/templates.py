from __future__ import annotations

from pathlib import Path


TEMPLATES: dict[str, str] = {
    "CONTRIBUTING.md": """# Contributing

Thanks for helping improve this project.

## Pull Requests

- Keep changes focused.
- Add tests for behavior changes.
- Update documentation for user-facing changes.
""",
    "SECURITY.md": """# Security Policy

Please report suspected vulnerabilities privately to the maintainer contact listed on the repository profile.

Include affected versions, reproduction steps, and suggested mitigations when possible.
""",
    ".github/ISSUE_TEMPLATE/bug_report.md": """---
name: Bug report
about: Report something that is not working
title: "[Bug]: "
labels: bug
---

## What happened?

## Steps to reproduce

## Expected behavior

## Environment
""",
    ".github/ISSUE_TEMPLATE/feature_request.md": """---
name: Feature request
about: Suggest an improvement
title: "[Feature]: "
labels: enhancement
---

## Problem

## Proposed solution

## Alternatives considered
""",
    ".github/PULL_REQUEST_TEMPLATE.md": """## Summary

## Testing

## Review notes
""",
    ".github/dependabot.yml": """version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
""",
}


def write_templates(root: str | Path, overwrite: bool = False) -> list[Path]:
    base = Path(root).expanduser().resolve()
    written: list[Path] = []
    for relative, content in TEMPLATES.items():
        path = base / relative
        if path.exists() and not overwrite:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(path)
    return written
