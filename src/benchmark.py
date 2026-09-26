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

def read_pddl_text(file_path):
    """
    Read a PDDL file and remove line comments.

    PDDL comments begin with ';'.
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"PDDL file not found: {file_path}"
        )

    lines = []

    with open(
        file_path,
        "r",
        encoding="utf-8",
        errors="ignore",
    ) as file:
        for line in file:
            clean_line = line.split(";", 1)[0]
            lines.append(clean_line)

    return "\n".join(lines)


def extract_requirements(domain_file):
    """
    Extract PDDL :requirements from a domain file.

    Example
    -------
    (:requirements :strips :typing)

    returns

    (":strips", ":typing")
    """
    import re

    text = read_pddl_text(
        domain_file
    ).lower()

    match = re.search(
        r"\(:requirements\s+([^)]+)\)",
        text,
        flags=re.MULTILINE,
    )

    if not match:
        return tuple()

    requirements = re.findall(
        r":[a-z0-9_-]+",
        match.group(1),
    )

    return tuple(
        sorted(set(requirements))
    )


def classify_requirements(requirements):
    """
    Classify a PDDL domain from its declared requirements.

    Returns a dictionary containing useful planning-category flags.
    """
    requirements = set(requirements)

    temporal_requirements = {
        ":durative-actions",
        ":duration-inequalities",
        ":continuous-effects",
        ":timed-initial-literals",
    }

    numeric_requirements = {
        ":fluents",
        ":numeric-fluents",
    }

    adl_requirements = {
        ":adl",
        ":disjunctive-preconditions",
        ":existential-preconditions",
        ":universal-preconditions",
        ":quantified-preconditions",
        ":conditional-effects",
    }

    derived_requirements = {
        ":derived-predicates",
    }

    is_temporal = bool(
        requirements & temporal_requirements
    )

    is_numeric = bool(
        requirements & numeric_requirements
    )

    is_adl = bool(
        requirements & adl_requirements
    )

    is_derived = bool(
        requirements & derived_requirements
    )

    is_strips = (
        ":strips" in requirements
    )

    # A deliberately conservative subset for our first experiments.
    baseline_eligible = (
        is_strips
        and not is_temporal
        and not is_numeric
        and not is_adl
        and not is_derived
    )

    if is_temporal and is_numeric:
        planning_type = "temporal_numeric"

    elif is_temporal:
        planning_type = "temporal"

    elif is_numeric:
        planning_type = "numeric"

    elif is_adl:
        planning_type = "adl"

    elif is_derived:
        planning_type = "derived"

    elif is_strips:
        planning_type = "classical_strips"

    else:
        planning_type = "other"

    return {
        "planning_type": planning_type,
        "is_strips": is_strips,
        "is_adl": is_adl,
        "is_numeric": is_numeric,
        "is_temporal": is_temporal,
        "is_derived": is_derived,
        "baseline_eligible": baseline_eligible,
    }

def build_benchmark_index(dataset_root):
    """
    Build a problem-level index of the PDDL benchmark dataset.

    Paths are stored relative to dataset_root so the benchmark
    remains portable across machines and Kaggle users.
    """
    dataset_root = Path(
        dataset_root
    )

    if not dataset_root.exists():
        raise FileNotFoundError(
            f"Dataset root not found: "
            f"{dataset_root}"
        )

    rows = []

    for domain in discover_domains(
        dataset_root
    ):
        domain_file = Path(
            domain["domain_file"]
        )

        domain_directory = (
            domain_file.parent
        )

        relative_domain_file = (
            domain_file.relative_to(
                dataset_root
            )
        )

        competition = get_competition(
            relative_domain_file
        )

        requirements = (
            extract_requirements(
                domain_file
            )
        )

        classification = (
            classify_requirements(
                requirements
            )
        )

        problems = discover_problems(
            domain_directory
        )

        for problem_file in problems:

            relative_problem_file = (
                problem_file.relative_to(
                    dataset_root
                )
            )

            try:
                problem_id = int(
                    problem_file
                    .stem
                    .split("-")[-1]
                )

            except ValueError:
                problem_id = None

            rows.append(
                {
                    "competition":
                        competition,

                    "domain_variant":
                        domain["name"],

                    "problem":
                        problem_file.name,

                    "problem_id":
                        problem_id,

                    "requirements":
                        " ".join(
                            requirements
                        ),

                    "planning_type":
                        classification[
                            "planning_type"
                        ],

                    "is_strips":
                        classification[
                            "is_strips"
                        ],

                    "is_adl":
                        classification[
                            "is_adl"
                        ],

                    "is_numeric":
                        classification[
                            "is_numeric"
                        ],

                    "is_temporal":
                        classification[
                            "is_temporal"
                        ],

                    "is_derived":
                        classification[
                            "is_derived"
                        ],

                    "baseline_eligible":
                        classification[
                            "baseline_eligible"
                        ],

                    "domain_file":
                        str(
                            relative_domain_file
                        ),

                    "problem_file":
                        str(
                            relative_problem_file
                        ),
                }
            )

    columns = [
        "competition",
        "domain_variant",
        "problem",
        "problem_id",
        "requirements",
        "planning_type",
        "is_strips",
        "is_adl",
        "is_numeric",
        "is_temporal",
        "is_derived",
        "baseline_eligible",
        "domain_file",
        "problem_file",
    ]

    benchmark_df = pd.DataFrame(
        rows,
        columns=columns,
    )

    if benchmark_df.empty:
        return benchmark_df

    benchmark_df = (
        benchmark_df
        .sort_values(
            by=[
                "competition",
                "domain_variant",
                "problem_id",
                "problem_file",
            ],
            na_position="last",
        )
        .reset_index(
            drop=True
        )
    )

    return benchmark_df