from pathlib import Path

import pandas as pd


def discover_domains(dataset_root):
    """
    Discover PDDL domain directories inside a dataset.

    A valid domain directory must contain:
        domain.pddl
        instances/

    Parameters
    ----------
    dataset_root : str or Path
        Root directory containing the planning dataset.

    Returns
    -------
    list[dict]
        Information about each discovered domain variant.
    """
    dataset_root = Path(dataset_root)

    if not dataset_root.exists():
        raise FileNotFoundError(
            f"Dataset root not found: {dataset_root}"
        )

    domains = []

    for domain_file in dataset_root.rglob("domain.pddl"):
        domain_directory = domain_file.parent
        instance_directory = domain_directory / "instances"

        if not instance_directory.exists():
            continue

        problem_files = list(
            instance_directory.glob("*.pddl")
        )

        domains.append(
            {
                "name": domain_directory.name,
                "domain_file": domain_file,
                "instance_directory": instance_directory,
                "num_instances": len(problem_files),
            }
        )

    return sorted(
        domains,
        key=lambda item: str(item["domain_file"]),
    )


def instance_number(path):
    """
    Extract a numeric suffix from filenames such as instance-12.pddl.

    Files without a numeric suffix fall back to lexical ordering.
    """
    path = Path(path)

    try:
        return int(path.stem.split("-")[-1])
    except ValueError:
        return path.stem


def discover_problems(domain_directory):
    """
    Discover problem instances for one PDDL domain directory.

    Parameters
    ----------
    domain_directory : str or Path
        Directory containing domain.pddl and instances/.

    Returns
    -------
    list[Path]
        Problem files sorted by instance number when possible.
    """
    domain_directory = Path(domain_directory)

    instance_directory = (
        domain_directory / "instances"
    )

    if not instance_directory.exists():
        raise FileNotFoundError(
            f"Instance directory not found: "
            f"{instance_directory}"
        )

    problems = list(
        instance_directory.glob("*.pddl")
    )

    return sorted(
        problems,
        key=instance_number,
    )


def get_competition(path):
    """
    Extract the IPC competition folder from a path.

    Example
    -------
    ipc-2000/domains/blocks/domain.pddl
        -> ipc-2000
    """
    path = Path(path)

    for part in path.parts:
        if part.startswith("ipc-"):
            return part

    return "unknown"


def build_benchmark_index(dataset_root):
    """
    Build a problem-level index of the PDDL benchmark dataset.

    Paths stored in the returned DataFrame are relative to dataset_root
    so that the index remains portable across machines and Kaggle users.

    Parameters
    ----------
    dataset_root : str or Path
        Root directory containing IPC benchmark folders.

    Returns
    -------
    pandas.DataFrame
        One row per planning problem.
    """
    dataset_root = Path(dataset_root)

    if not dataset_root.exists():
        raise FileNotFoundError(
            f"Dataset root not found: {dataset_root}"
        )

    rows = []

    for domain in discover_domains(dataset_root):
        domain_file = Path(domain["domain_file"])
        domain_directory = domain_file.parent

        relative_domain_file = (
            domain_file.relative_to(dataset_root)
        )

        competition = get_competition(
            relative_domain_file
        )

        problems = discover_problems(
            domain_directory
        )

        for problem_file in problems:
            relative_problem_file = (
                problem_file.relative_to(dataset_root)
            )

            try:
                problem_id = int(
                    problem_file.stem.split("-")[-1]
                )
            except ValueError:
                problem_id = None

            rows.append(
                {
                    "competition": competition,
                    "domain_variant": domain["name"],
                    "problem": problem_file.name,
                    "problem_id": problem_id,
                    "domain_file": str(relative_domain_file),
                    "problem_file": str(relative_problem_file),
                }
            )

    columns = [
    "competition",
    "domain_variant",
    "problem",
    "problem_id",
    "domain_file",
    "problem_file",
    ]

    benchmark_df = pd.DataFrame(
        rows,
        columns=columns,
    )

    if benchmark_df.empty:
        return benchmark_df

    benchmark_df = benchmark_df.sort_values(
        by=[
            "competition",
            "domain_variant",
            "problem_id",
            "problem_file",
        ],
        na_position="last",
    ).reset_index(drop=True)

    return benchmark_df