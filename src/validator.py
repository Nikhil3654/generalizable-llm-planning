from pathlib import Path
import subprocess


def _require_file(path, label):
    """
    Check that a required file exists.

    Parameters
    ----------
    path : str or Path
        File to check.
    label : str
        Human-readable name used in the error message.

    Returns
    -------
    Path
        Resolved Path object.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"{label} not found: {path}"
        )

    return path


def classify_val_output(output):
    """
    Convert VAL's text output into a simple status.

    This is intentionally conservative. The primary result used by the
    project is whether VAL reports 'Plan valid'.

    Parameters
    ----------
    output : str
        Combined stdout/stderr produced by VAL.

    Returns
    -------
    str
        Validation status.
    """
    text = output.lower()

    if "plan valid" in text:
        return "valid"

    if (
        "precondition" in text
        and (
            "not satisfied" in text
            or "false" in text
            or "failed" in text
        )
    ):
        return "precondition_failure"

    if (
        "unknown operator" in text
        or "unknown action" in text
        or "undeclared" in text
    ):
        return "unknown_action"

    if (
        "goal" in text
        and (
            "not satisfied" in text
            or "not achieved" in text
            or "failed" in text
            or "false" in text
        )
    ):
        return "goal_not_reached"

    if "plan failed" in text or "failed plans" in text:
        return "invalid"

    if not text.strip():
        return "validator_error"

    return "invalid"


def validate_plan(
    validator_path,
    domain_file,
    problem_file,
    plan_file,
):
    """
    Validate a PDDL plan using VAL.

    Parameters
    ----------
    validator_path : str or Path
        Path to VAL's Validate executable.
    domain_file : str or Path
        PDDL domain file.
    problem_file : str or Path
        PDDL problem file.
    plan_file : str or Path
        Text file containing the proposed plan.

    Returns
    -------
    dict
        Validation result and diagnostic information.
    """
    validator_path = _require_file(
        validator_path,
        "VAL validator",
    )
    domain_file = _require_file(
        domain_file,
        "Domain file",
    )
    problem_file = _require_file(
        problem_file,
        "Problem file",
    )
    plan_file = _require_file(
        plan_file,
        "Plan file",
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

    stdout = result.stdout or ""
    stderr = result.stderr or ""

    combined_output = "\n".join(
        part
        for part in [stdout, stderr]
        if part
    )

    status = classify_val_output(
        combined_output
    )

    return {
        "valid": status == "valid",
        "status": status,
        "returncode": result.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "command": command,
    }


def write_plan(actions, plan_file):
    """
    Write a sequence of planning actions to a plan file.

    Parameters
    ----------
    actions : iterable[str]
        Plan actions such as '(pick-up a)'.
    plan_file : str or Path
        Output location.

    Returns
    -------
    Path
        Path to the written plan file.
    """
    plan_file = Path(plan_file)
    plan_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    cleaned_actions = []

    for action in actions:
        action = str(action).strip()

        if action:
            cleaned_actions.append(action)

    text = "\n".join(cleaned_actions)

    if text:
        text += "\n"

    plan_file.write_text(
        text,
        encoding="utf-8",
    )

    return plan_file
