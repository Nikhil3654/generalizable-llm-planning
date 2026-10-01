import tempfile
import unittest

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from src.validator import (
    classify_val_output,
    validate_plan,
    write_plan,
)


class TestValidator(unittest.TestCase):

    def test_classify_valid_plan(self):
        output = """
        Checking plan: plan.txt
        Plan executed successfully - checking goal
        Plan valid
        """

        result = classify_val_output(output)

        self.assertEqual(
            result,
            "valid",
        )

    def test_classify_precondition_failure(self):
        output = """
        Plan failed because a precondition
        was not satisfied.
        """

        result = classify_val_output(output)

        self.assertEqual(
            result,
            "precondition_failure",
        )

    def test_classify_goal_failure(self):
        output = """
        Plan executed.
        Goal not satisfied.
        """

        result = classify_val_output(output)

        self.assertEqual(
            result,
            "goal_not_reached",
        )

    def test_write_plan(self):
        with tempfile.TemporaryDirectory() as tmp:

            plan_path = Path(tmp) / "plan.txt"

            actions = [
                "(pick-up a)",
                "(stack a b)",
            ]

            write_plan(
                actions,
                plan_path,
            )

            self.assertTrue(
                plan_path.exists()
            )

            text = plan_path.read_text(
                encoding="utf-8"
            )

            self.assertEqual(
                text,
                "(pick-up a)\n(stack a b)\n",
            )

    @patch("src.validator.subprocess.run")
    def test_validate_plan_valid(
        self,
        mock_run,
    ):
        with tempfile.TemporaryDirectory() as tmp:

            tmp = Path(tmp)

            validator = tmp / "Validate"
            domain = tmp / "domain.pddl"
            problem = tmp / "problem.pddl"
            plan = tmp / "plan.txt"

            validator.write_text("")
            domain.write_text("(domain)")
            problem.write_text("(problem)")
            plan.write_text("(action)\n")

            mock_run.return_value = SimpleNamespace(
                returncode=0,
                stdout="Plan valid\n",
                stderr="",
            )

            result = validate_plan(
                validator_path=validator,
                domain_file=domain,
                problem_file=problem,
                plan_file=plan,
            )

            self.assertTrue(
                result["valid"]
            )

            self.assertEqual(
                result["status"],
                "valid",
            )

    @patch("src.validator.subprocess.run")
    def test_validate_plan_invalid(
        self,
        mock_run,
    ):
        with tempfile.TemporaryDirectory() as tmp:

            tmp = Path(tmp)

            validator = tmp / "Validate"
            domain = tmp / "domain.pddl"
            problem = tmp / "problem.pddl"
            plan = tmp / "plan.txt"

            validator.write_text("")
            domain.write_text("(domain)")
            problem.write_text("(problem)")
            plan.write_text("(bad-action)\n")

            mock_run.return_value = SimpleNamespace(
                returncode=0,
                stdout="""
                Plan executed.
                Goal not satisfied.
                """,
                stderr="",
            )

            result = validate_plan(
                validator_path=validator,
                domain_file=domain,
                problem_file=problem,
                plan_file=plan,
            )

            self.assertFalse(
                result["valid"]
            )

            self.assertEqual(
                result["status"],
                "goal_not_reached",
            )


if __name__ == "__main__":
    unittest.main()
