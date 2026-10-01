from pathlib import Path
import subprocess


def write_plan(actions, plan_file):
    """Write a list of action strings to a plan file."""
    plan_file = Path(plan_file)
    plan_file.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    for action in actions:
        action = str(action).strip()
        if not action:
            continue
        lines.append(action)

    text = "\n".join(lines)
    if text:
        text += "\n"

    plan_file.write_text(text, encoding="utf-8")
    return plan_file


def _plan_looks_valid(stdout, stderr, returncode):
    """
    Decide validity from VAL's exit code and output text.

    VAL typically returns 0 for a valid plan. Output may also contain
    phrases such as "Plan valid" / "Plan invalid".
    """
    combined = f"{stdout}\n{stderr}".lower()

    if "plan invalid" in combined or "failed plans" in combined:
        return False

    if "plan valid" in combined or "successful plans" in combined:
        return True

    return returncode == 0


def validate_plan(
    validator_path,
    domain_file,
    problem_file,
    plan_file,
):
    """
    Validate a plan with VAL's Validate executable.

    Returns a dict with at least:
        valid, status, returncode, stdout, stderr
    """
    validator_path = Path(validator_path)
    domain_file = Path(domain_file)
    problem_file = Path(problem_file)
    plan_file = Path(plan_file)

    if not validator_path.exists():
        raise FileNotFoundError(
            f"Validator not found: {validator_path}"
        )

    if not domain_file.exists():
        raise FileNotFoundError(
            f"Domain file not found: {domain_file}"
        )

    if not problem_file.exists():
        raise FileNotFoundError(
            f"Problem file not found: {problem_file}"
        )

    if not plan_file.exists():
        raise FileNotFoundError(
            f"Plan file not found: {plan_file}"
        )

    command = [
        str(validator_path),
        str(domain_file),
        str(problem_file),
        str(plan_file),
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    valid = _plan_looks_valid(
        result.stdout,
        result.stderr,
        result.returncode,
    )

    return {
        "valid": valid,
        "status": "valid" if valid else "invalid",
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "plan_file": str(plan_file),
    }
