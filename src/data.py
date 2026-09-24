from pathlib import Path


def find_pddl_files(dataset_path):
    dataset_path = Path(dataset_path)

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset directory not found: {dataset_path}"
        )

    return sorted(dataset_path.rglob("*.pddl"))


def find_domain_files(dataset_path, domain_name):
    files = find_pddl_files(dataset_path)

    domain_name = domain_name.lower()

    return [
        file
        for file in files
        if domain_name in str(file).lower()
    ]


def read_pddl(file_path):
    file_path = Path(file_path)

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()