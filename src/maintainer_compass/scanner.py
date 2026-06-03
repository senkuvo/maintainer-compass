from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable


@dataclass(frozen=True)
class Check:
    id: str
    category: str
    title: str
    points: int
    help_text: str
    predicate: Callable[[Path], bool]


@dataclass(frozen=True)
class Finding:
    id: str
    category: str
    title: str
    passed: bool
    points: int
    help_text: str


@dataclass(frozen=True)
class CategoryScore:
    category: str
    earned: int
    possible: int


@dataclass(frozen=True)
class ScanResult:
    path: Path
    findings: tuple[Finding, ...]

    @property
    def earned(self) -> int:
        return sum(f.points for f in self.findings if f.passed)

    @property
    def possible(self) -> int:
        return sum(f.points for f in self.findings)

    @property
    def score(self) -> int:
        if self.possible == 0:
            return 0
        return round((self.earned / self.possible) * 100)

    @property
    def failures(self) -> tuple[Finding, ...]:
        return tuple(f for f in self.findings if not f.passed)

    @property
    def categories(self) -> tuple[CategoryScore, ...]:
        names = sorted({f.category for f in self.findings})
        scores = []
        for name in names:
            category_findings = [f for f in self.findings if f.category == name]
            earned = sum(f.points for f in category_findings if f.passed)
            possible = sum(f.points for f in category_findings)
            scores.append(CategoryScore(name, earned, possible))
        return tuple(scores)


def scan_repository(path: str | Path) -> ScanResult:
    root = Path(path).expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"Repository path does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Repository path is not a directory: {root}")

    findings = tuple(
        Finding(
            id=check.id,
            category=check.category,
            title=check.title,
            passed=check.predicate(root),
            points=check.points,
            help_text=check.help_text,
        )
        for check in CHECKS
    )
    return ScanResult(root, findings)


def has_any(root: Path, names: Iterable[str]) -> bool:
    lowered = {name.lower() for name in names}
    for child in root.rglob("*"):
        if ".git" in child.parts:
            continue
        if child.is_file() and child.name.lower() in lowered:
            return True
    return False


def has_path(root: Path, relative_paths: Iterable[str]) -> bool:
    return any((root / relative).exists() for relative in relative_paths)


def has_glob(root: Path, pattern: str) -> bool:
    return any(path.is_file() for path in root.glob(pattern))


def workflow_contains(root: Path, needles: Iterable[str]) -> bool:
    workflow_dir = root / ".github" / "workflows"
    if not workflow_dir.exists():
        return False
    lowered_needles = [needle.lower() for needle in needles]
    for path in workflow_dir.glob("*"):
        if not path.is_file():
            continue
        haystack = f"{path.name}\n{safe_read(path)}".lower()
        if any(needle in haystack for needle in lowered_needles):
            return True
    return False


def has_git_tags(root: Path) -> bool:
    if not (root / ".git").exists():
        return False
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), "tag", "--list"],
            check=False,
            capture_output=True,
            text=True,
            timeout=3,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return bool(completed.stdout.strip())


def safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


CHECKS: tuple[Check, ...] = (
    Check(
        "readme",
        "onboarding",
        "README is present",
        8,
        "Add a README with project purpose, install steps, usage, and support expectations.",
        lambda root: has_any(root, ["README.md", "README.rst", "README.txt"]),
    ),
    Check(
        "contributing",
        "onboarding",
        "Contributing guide is present",
        6,
        "Add CONTRIBUTING.md so new contributors understand the review workflow.",
        lambda root: has_any(root, ["CONTRIBUTING.md", "CONTRIBUTING.rst"]),
    ),
    Check(
        "code-of-conduct",
        "onboarding",
        "Code of conduct is present",
        4,
        "Add CODE_OF_CONDUCT.md to set collaboration expectations.",
        lambda root: has_any(root, ["CODE_OF_CONDUCT.md", "CODE-OF-CONDUCT.md"]),
    ),
    Check(
        "issue-templates",
        "onboarding",
        "Issue templates are configured",
        4,
        "Add .github/ISSUE_TEMPLATE files to improve triage quality.",
        lambda root: has_glob(root, ".github/ISSUE_TEMPLATE/*"),
    ),
    Check(
        "pull-request-template",
        "onboarding",
        "Pull request template is configured",
        3,
        "Add a pull request template with testing and review prompts.",
        lambda root: has_path(
            root,
            [
                "PULL_REQUEST_TEMPLATE.md",
                ".github/PULL_REQUEST_TEMPLATE.md",
                "docs/PULL_REQUEST_TEMPLATE.md",
            ],
        ),
    ),
    Check(
        "security-policy",
        "security",
        "Security policy is present",
        8,
        "Add SECURITY.md with private disclosure instructions and support windows.",
        lambda root: has_any(root, ["SECURITY.md"]),
    ),
    Check(
        "license",
        "security",
        "License is present",
        5,
        "Add a license so downstream users know the legal terms.",
        lambda root: has_any(root, ["LICENSE", "LICENSE.md", "COPYING"]),
    ),
    Check(
        "dependabot",
        "security",
        "Dependency update automation is configured",
        6,
        "Add .github/dependabot.yml or equivalent dependency update automation.",
        lambda root: has_path(root, [".github/dependabot.yml", ".github/dependabot.yaml"]),
    ),
    Check(
        "codeowners",
        "security",
        "Code owners are configured",
        6,
        "Add CODEOWNERS so sensitive areas get the right reviewers.",
        lambda root: has_path(root, ["CODEOWNERS", ".github/CODEOWNERS", "docs/CODEOWNERS"]),
    ),
    Check(
        "ci",
        "automation",
        "CI workflow is present",
        8,
        "Add a CI workflow that runs tests on pull requests.",
        lambda root: has_glob(root, ".github/workflows/*"),
    ),
    Check(
        "tests",
        "automation",
        "Tests are present",
        6,
        "Add tests so maintainers can review changes with confidence.",
        lambda root: has_path(root, ["tests", "test", "spec", "__tests__"]),
    ),
    Check(
        "manifest",
        "automation",
        "Package or build manifest is present",
        5,
        "Add an ecosystem manifest such as pyproject.toml, package.json, Cargo.toml, or go.mod.",
        lambda root: has_any(
            root,
            [
                "pyproject.toml",
                "package.json",
                "Cargo.toml",
                "go.mod",
                "pom.xml",
                "build.gradle",
                "pubspec.yaml",
            ],
        ),
    ),
    Check(
        "workflow-tests",
        "automation",
        "CI workflow appears to run tests",
        6,
        "Ensure CI workflows run the project's test command.",
        lambda root: workflow_contains(
            root,
            ["pytest", "unittest", "npm test", "cargo test", "go test", "mvn test"],
        ),
    ),
    Check(
        "changelog",
        "release",
        "Changelog is present",
        7,
        "Add CHANGELOG.md so users can understand release impact.",
        lambda root: has_any(root, ["CHANGELOG.md", "CHANGES.md", "HISTORY.md"]),
    ),
    Check(
        "release-workflow",
        "release",
        "Release automation is present",
        7,
        "Add release automation or a release checklist to reduce maintainer toil.",
        lambda root: workflow_contains(root, ["release", "publish", "pypi", "npm publish", "cargo publish"]),
    ),
    Check(
        "version-metadata",
        "release",
        "Version metadata is present",
        5,
        "Track a visible version in your package manifest or source package.",
        lambda root: has_any(root, ["pyproject.toml", "package.json", "Cargo.toml"])
        or has_path(root, ["src"]),
    ),
    Check(
        "git-tags",
        "release",
        "Git tags exist",
        6,
        "Tag releases so downstream users can pin and audit versions.",
        has_git_tags,
    ),
)
