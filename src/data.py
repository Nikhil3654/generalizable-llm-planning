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

    if not file_path.exists():
        raise FileNotFoundError(
            f"PDDL file not found: {file_path}"
        )

    return file_path.read_text(encoding="utf-8")


def find_kaggle_dataset(dataset_name):
    """
    Locate a dataset inside /kaggle/input without depending on
    a specific Kaggle username or account path.
    """

    kaggle_root = Path("/kaggle/input")

    if not kaggle_root.exists():
        raise FileNotFoundError(
            "Kaggle input directory was not found."
        )

    matches = [
        path
        for path in kaggle_root.rglob("*")
        if path.is_dir()
        and path.name.lower() == dataset_name.lower()
    ]

    if not matches:
        raise FileNotFoundError(
            f"Could not find Kaggle dataset: {dataset_name}"
        )

    return matches[0]