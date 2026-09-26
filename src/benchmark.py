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