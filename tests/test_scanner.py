import tempfile
import unittest
import os
from pathlib import Path

from maintainer_compass.scanner import scan_repository


def write(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def temporary_workspace():
    base = os.environ.get("MAINTAINER_COMPASS_TEST_TMP")
    if base:
        Path(base).mkdir(parents=True, exist_ok=True)
        return tempfile.TemporaryDirectory(dir=base)
    return tempfile.TemporaryDirectory()


class ScannerTests(unittest.TestCase):
    def test_scan_rewards_expected_maintenance_files(self) -> None:
        with temporary_workspace() as directory:
            tmp_path = Path(directory)
            write(tmp_path / "README.md", "# Demo")
            write(tmp_path / "CONTRIBUTING.md", "# Contributing")
            write(tmp_path / "CODE_OF_CONDUCT.md", "# Conduct")
            write(tmp_path / "SECURITY.md", "# Security")
            write(tmp_path / "LICENSE", "MIT")
            write(tmp_path / "CHANGELOG.md", "# Changelog")
            write(tmp_path / "pyproject.toml", "[project]\nname = 'demo'\n")
            write(tmp_path / ".github" / "ISSUE_TEMPLATE" / "bug.md", "bug")
            write(tmp_path / ".github" / "PULL_REQUEST_TEMPLATE.md", "testing")
            write(tmp_path / ".github" / "dependabot.yml", "version: 2")
            write(tmp_path / ".github" / "CODEOWNERS", "* @demo/maintainers")
            write(tmp_path / ".github" / "workflows" / "ci.yml", "name: CI\nrun: pytest")
            (tmp_path / "tests").mkdir()

            result = scan_repository(tmp_path)

            self.assertGreaterEqual(result.score, 80)
            self.assertTrue(any(f.id == "readme" and f.passed for f in result.findings))
            self.assertTrue(any(f.id == "workflow-tests" and f.passed for f in result.findings))

    def test_scan_reports_missing_files(self) -> None:
        with temporary_workspace() as directory:
            tmp_path = Path(directory)
            write(tmp_path / "README.md", "# Demo")

            result = scan_repository(tmp_path)

            self.assertLess(result.score, 50)
            self.assertTrue(any(f.id == "security-policy" and not f.passed for f in result.failures))
            self.assertTrue(any(f.id == "ci" and not f.passed for f in result.failures))


if __name__ == "__main__":
    unittest.main()
