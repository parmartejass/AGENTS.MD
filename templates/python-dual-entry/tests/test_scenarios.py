import subprocess
import sys
import unittest
from pathlib import Path

from myapp.core.verification import compare_text_files
from myapp.logging_config import setup_logging
from myapp.runner import run_job
from myapp.scenarios import list_scenario_files, load_scenario


TEMPLATE_ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = Path(__file__).resolve().parent
SCENARIOS_DIR = TESTS_DIR / "scenarios"
OUTPUT_DIR = TESTS_DIR / "output"


class ScenarioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        setup_logging(event_log=OUTPUT_DIR / "scenario_suite.events.jsonl")

    def test_all_scenarios(self) -> None:
        scenario_files = list_scenario_files(SCENARIOS_DIR)
        self.assertGreater(len(scenario_files), 0, f"No scenarios found in: {SCENARIOS_DIR}")

        for scenario_path in scenario_files:
            with self.subTest(scenario=scenario_path.name):
                scenario = load_scenario(scenario_path)

                if scenario.job.output_path.exists() and scenario.job.output_path.is_file():
                    scenario.job.output_path.unlink()

                result = run_job(scenario.job)
                self.assertEqual(
                    scenario.expected.success,
                    result.success,
                    f"Expected success={scenario.expected.success} got success={result.success}; errors={result.errors}",
                )

                if scenario.expected.success:
                    self.assertTrue(scenario.job.output_path.exists(), f"Output file not created: {scenario.job.output_path}")
                    if scenario.expected.output_path is not None:
                        verification = compare_text_files(
                            expected_path=scenario.expected.output_path,
                            actual_path=scenario.job.output_path,
                        )
                        self.assertTrue(verification.matches, f"Output mismatch:\n{verification.diff}")

    def test_cli_happy_path(self) -> None:
        scenario_path = SCENARIOS_DIR / "scenario_001_happy_path.json"
        event_log_path = OUTPUT_DIR / "scenario_cli.events.jsonl"
        if event_log_path.exists():
            event_log_path.unlink()

        try:
            proc = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "myapp",
                    "--cli",
                    "--scenario",
                    str(scenario_path),
                    "--verify",
                    "--event-log",
                    str(event_log_path),
                ],
                cwd=str(TEMPLATE_ROOT),
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
            )
        finally:
            if event_log_path.exists():
                event_log_path.unlink()

        self.assertEqual(
            proc.returncode,
            0,
            f"CLI failed.\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}",
        )


if __name__ == "__main__":
    unittest.main()
