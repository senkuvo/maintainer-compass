# Maintainer Compass

Maintainer Compass is a dependency-free CLI that audits an open-source repository for maintainer readiness. It checks the small-but-important signals that make a project easier to review, secure, release, and hand off: contribution docs, issue templates, CI, security policy, release notes, ownership files, package manifests, tests, and automation.

The goal is not to shame projects with a score. The goal is to give maintainers a fast, local report they can use before a release, before onboarding new contributors, or before applying for ecosystem support programs.

## Install

```bash
python -m pip install maintainer-compass
```

For local development from this repository:

```bash
python -m pip install -e .
python -m unittest
```

## Use

Scan the current repository:

```bash
maintainer-compass scan .
```

Emit Markdown for an issue, pull request, or release checklist:

```bash
maintainer-compass scan . --format markdown --output maintainer-report.md
```

Fail CI when a repository falls below a threshold:

```bash
maintainer-compass scan . --fail-under 80
```

Generate starter GitHub community-health files:

```bash
maintainer-compass init .
```

## Example

```text
Maintainer Compass report for my-project
Score: 82/100

Category          Score
onboarding        22/25
security          18/25
automation        20/25
release           22/25

Needs attention
- Add SECURITY.md so reporters know how to disclose vulnerabilities.
- Add .github/dependabot.yml to keep dependency updates visible.
```

## What It Checks

- Onboarding: README, contributing guide, code of conduct, issue templates, pull request template.
- Security: security policy, license, dependency update configuration, code ownership.
- Automation: CI workflows, test directory, package manifest, lint or test commands in workflows.
- Release: changelog, release workflow, git tags, version metadata.

## Why This Exists

Open-source maintainers spend a lot of time on invisible work: triaging issues, reviewing pull requests, keeping releases safe, and preserving trust for users downstream. Maintainer Compass turns that invisible work into a concrete report that can be shared with collaborators, sponsors, and project governance groups.

## Roadmap

- GitHub API ingestion for issue and pull request triage metrics.
- SARIF output for security posture findings.
- Suggested GitHub labels and saved triage views.
- Release-readiness reports that compare changed files against ownership and test coverage signals.

## Contributing

Contributions are welcome. Start with [CONTRIBUTING.md](CONTRIBUTING.md), open an issue for larger changes, and keep pull requests focused.

## License

MIT
