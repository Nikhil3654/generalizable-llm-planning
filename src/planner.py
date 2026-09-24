from pathlib import Path
import subprocess


def run_fast_downward(
    fast_downward_path,
    domain_file,
    problem_file,
    plan_file,
    alias="lama-first",
):
    fast_downward_path = Path(fast_downward_path)
    domain_file = Path(domain_file)
    problem_file = Path(problem_file)
    plan_file = Path(plan_file)

    if not fast_downward_path.exists():
        raise FileNotFoundError(
            f"Fast Downward not found: {fast_downward_path}"
        )

    if not domain_file.exists():
        raise FileNotFoundError(
            f"Domain file not found: {domain_file}"
        )

    if not problem_file.exists():
        raise FileNotFoundError(
            f"Problem file not found: {problem_file}"
        )

    command = [
        "python",
        str(fast_downward_path),
        "--alias",
        alias,
        "--plan-file",
        str(plan_file),
        str(domain_file),
        str(problem_file),
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "plan_file": str(plan_file),
        "plan_found": plan_file.exists(),
    }


def read_plan(plan_file):
    plan_file = Path(plan_file)

    if not plan_file.exists():
        return []

    actions = []

    for line in plan_file.read_text().splitlines():
        line = line.strip()

        if not line:
            continue

        if line.startswith(";"):
            continue

        actions.append(line)

    return actions