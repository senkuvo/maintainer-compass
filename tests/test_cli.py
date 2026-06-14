import tempfile
import unittest
import os
from pathlib import Path

from maintainer_compass.cli import main


def temporary_workspace():
    base = os.environ.get("MAINTAINER_COMPASS_TEST_TMP")
    if base:
        Path(base).mkdir(parents=True, exist_ok=True)
        return tempfile.TemporaryDirectory(dir=base)
    return tempfile.TemporaryDirectory()


class CliTests(unittest.TestCase):
    def test_cli_writes_json_report(self) -> None:
        with temporary_workspace() as directory:
            tmp_path = Path(directory)
            (tmp_path / "README.md").write_text("# Demo", encoding="utf-8")
            output = tmp_path / "report.json"

            exit_code = main(["scan", str(tmp_path), "--format", "json", "--output", str(output)])

            self.assertEqual(exit_code, 0)
            self.assertIn('"score"', output.read_text(encoding="utf-8"))

    def test_fail_under_returns_distinct_status(self) -> None:
        with temporary_workspace() as directory:
            exit_code = main(["scan", directory, "--fail-under", "100"])

            self.assertEqual(exit_code, 2)

    def test_cli_can_write_only_failures_report(self) -> None:
        with temporary_workspace() as directory:
            tmp_path = Path(directory)
            (tmp_path / "README.md").write_text("# Demo", encoding="utf-8")
            output = tmp_path / "report.md"

            exit_code = main(
                [
                    "scan",
                    str(tmp_path),
                    "--format",
                    "markdown",
                    "--only-failures",
                    "--output",
                    str(output),
                ]
            )

            report = output.read_text(encoding="utf-8")
            self.assertEqual(exit_code, 0)
            self.assertIn("**needs attention:** Security policy is present", report)
            self.assertNotIn("**pass:** README is present", report)

    def test_init_writes_templates(self) -> None:
        with temporary_workspace() as directory:
            tmp_path = Path(directory)
            exit_code = main(["init", str(tmp_path)])

            self.assertEqual(exit_code, 0)
            self.assertTrue((tmp_path / "SECURITY.md").exists())
            self.assertTrue((tmp_path / ".github" / "PULL_REQUEST_TEMPLATE.md").exists())


if __name__ == "__main__":
    unittest.main()
