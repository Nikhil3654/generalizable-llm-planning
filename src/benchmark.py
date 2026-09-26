from pathlib import Path


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
        Information about each discovered domain.
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

        problem_files = sorted(
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
    Extract the numeric portion from filenames such as
    instance-12.pddl.

    Falls back to the filename when a numeric suffix is not present.
    """

    path = Path(path)

    try:
        return int(path.stem.split("-")[-1])
    except ValueError:
        return path.stem


def discover_problems(domain_directory):
    """
    Find problem instances for one planning domain.

    Parameters
    ----------
    domain_directory : str or Path
        Directory containing domain.pddl and instances/.

    Returns
    -------
    list[Path]
        Sorted problem files.
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