from pathlib import Path


def find_pddl_files(dataset_path):
    dataset_path = Path(dataset_path)

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset directory not found: {dataset_path}"
        )

    files = list(dataset_path.rglob("*.pddl"))

    return sorted(files)


if __name__ == "__main__":
    files = find_pddl_files("/kaggle/input")

    print(f"Found {len(files)} PDDL files")

    for file in files[:10]:
        print(file)