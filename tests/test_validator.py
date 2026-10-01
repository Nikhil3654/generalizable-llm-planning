from pathlib import Path
from unittest.mock import MagicMock, patch

from src.validator import write_plan, validate_plan, _plan_looks_valid


def test_write_plan_roundtrip(tmp_path):
    plan_file = tmp_path / "plan.txt"
    actions = ["(pick-up b1)", "(stack b1 b2)"]

    write_plan(actions, plan_file)

    text = plan_file.read_text(encoding="utf-8")
    assert "(pick-up b1)" in text
    assert "(stack b1 b2)" in text


def test_write_plan_skips_blank_actions(tmp_path):
    plan_file = tmp_path / "emptyish.txt"
    write_plan(["", "  ", "(unstack a b)"], plan_file)

    lines = [
        line for line in plan_file.read_text().splitlines() if line.strip()
    ]
    assert lines == ["(unstack a b)"]


def test_plan_looks_valid_from_text():
    assert _plan_looks_valid("Plan valid", "", 1) is True
    assert _plan_looks_valid("Plan invalid", "", 0) is False
    assert _plan_looks_valid("", "", 0) is True
    assert _plan_looks_valid("", "", 1) is False


def test_validate_plan_returns_expected_keys(tmp_path):
    validator = tmp_path / "Validate"
    domain = tmp_path / "domain.pddl"
    problem = tmp_path / "problem.pddl"
    plan = tmp_path / "plan.txt"

    validator.write_text("", encoding="utf-8")
    domain.write_text("(define (domain blocks))", encoding="utf-8")
    problem.write_text("(define (problem p))", encoding="utf-8")
    plan.write_text("(pick-up b1)\n", encoding="utf-8")

    fake = MagicMock()
    fake.returncode = 0
    fake.stdout = "Plan valid\n"
    fake.stderr = ""

    with patch("src.validator.subprocess.run", return_value=fake) as run:
        result = validate_plan(validator, domain, problem, plan)

    run.assert_called_once()
    assert result["valid"] is True
    assert result["status"] == "valid"
    assert result["returncode"] == 0
    assert "stdout" in result
    assert "stderr" in result


def test_validate_plan_invalid(tmp_path):
    validator = tmp_path / "Validate"
    domain = tmp_path / "domain.pddl"
    problem = tmp_path / "problem.pddl"
    plan = tmp_path / "plan.txt"

    for path in (validator, domain, problem, plan):
        path.write_text("x", encoding="utf-8")

    fake = MagicMock()
    fake.returncode = 1
    fake.stdout = "Plan invalid\n"
    fake.stderr = ""

    with patch("src.validator.subprocess.run", return_value=fake):
        result = validate_plan(validator, domain, problem, plan)

    assert result["valid"] is False
    assert result["status"] == "invalid"


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        test_write_plan_roundtrip(tmp_path)
        test_write_plan_skips_blank_actions(tmp_path)
        test_plan_looks_valid_from_text()
        test_validate_plan_returns_expected_keys(tmp_path)
        test_validate_plan_invalid(tmp_path)

    print("Validator tests passed.")
