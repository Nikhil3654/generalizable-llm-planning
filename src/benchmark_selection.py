from pathlib import Path

import pandas as pd
import yaml


def load_benchmark_config(config_path):
    """
    Load benchmark configuration from YAML.
    """
    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(
            f"Benchmark config not found: {config_path}"
        )

    with open(
        config_path,
        "r",
        encoding="utf-8",
    ) as file:
        config = yaml.safe_load(file)

    if "benchmark" not in config:
        raise ValueError(
            "Config must contain a 'benchmark' section."
        )

    return config["benchmark"]


def _select_family(
    benchmark_df,
    family_name,
    family_config,
    split_name,
    max_instances,
):
    """
    Select one configured family/variant from the benchmark index.
    """

    competition = family_config["competition"]
    variant = family_config["variant"]

    selected = benchmark_df[
        (
            benchmark_df["planning_family"]
            == family_name
        )
        &
        (
            benchmark_df["competition"]
            == competition
        )
        &
        (
            benchmark_df["domain_variant"]
            == variant
        )
        &
        (
            benchmark_df["baseline_eligible"]
        )
    ].copy()

    if selected.empty:
        raise ValueError(
            "No eligible problems found for "
            f"{family_name}: "
            f"{competition}/{variant}"
        )

    selected = selected.sort_values(
        by=[
            "problem_id",
            "problem_file",
        ],
        na_position="last",
    )

    if len(selected) < max_instances:
        raise ValueError(
            f"Family '{family_name}' contains only "
            f"{len(selected)} eligible problems, "
            f"but {max_instances} were requested."
        )

    selected = selected.head(
        max_instances
    ).copy()

    selected["benchmark_split"] = split_name
    selected["benchmark_family"] = family_name

    return selected


def build_research_benchmark(
    benchmark_df,
    config_path,
):
    """
    Select the reproducible research benchmark defined in YAML.

    Returns
    -------
    pandas.DataFrame
        Selected benchmark problems with development/held-out labels.
    """

    config = load_benchmark_config(
        config_path
    )

    max_instances = config[
        "max_instances_per_family"
    ]

    selected_groups = []

    sections = [
        (
            "development_families",
            "development",
        ),
        (
            "held_out_families",
            "held_out",
        ),
    ]

    for config_section, split_name in sections:

        families = config.get(
            config_section,
            {},
        )

        for family_name, family_config in families.items():

            selected = _select_family(
                benchmark_df=benchmark_df,
                family_name=family_name,
                family_config=family_config,
                split_name=split_name,
                max_instances=max_instances,
            )

            selected_groups.append(
                selected
            )

    if not selected_groups:
        raise ValueError(
            "Benchmark configuration selected no problems."
        )

    result = pd.concat(
        selected_groups,
        ignore_index=True,
    )

    result = result.sort_values(
        by=[
            "benchmark_split",
            "benchmark_family",
            "problem_id",
        ],
        na_position="last",
    ).reset_index(
        drop=True
    )

    return result


def validate_research_benchmark(
    benchmark_df,
):
    """
    Run basic integrity checks over a selected research benchmark.

    Returns
    -------
    dict
        Validation summary.
    """

    required_columns = {
        "benchmark_split",
        "benchmark_family",
        "competition",
        "domain_variant",
        "problem",
        "problem_file",
        "domain_file",
        "baseline_eligible",
    }

    missing_columns = (
        required_columns
        - set(benchmark_df.columns)
    )

    if missing_columns:
        raise ValueError(
            "Benchmark is missing columns: "
            + ", ".join(
                sorted(missing_columns)
            )
        )

    duplicate_rows = benchmark_df.duplicated(
        subset=[
            "competition",
            "domain_variant",
            "problem_file",
        ]
    ).sum()

    development_families = set(
        benchmark_df.loc[
            benchmark_df[
                "benchmark_split"
            ] == "development",
            "benchmark_family",
        ]
    )

    held_out_families = set(
        benchmark_df.loc[
            benchmark_df[
                "benchmark_split"
            ] == "held_out",
            "benchmark_family",
        ]
    )

    family_overlap = (
        development_families
        & held_out_families
    )

    all_eligible = bool(
        benchmark_df[
            "baseline_eligible"
        ].all()
    )

    return {
        "num_problems":
            len(benchmark_df),

        "num_families":
            benchmark_df[
                "benchmark_family"
            ].nunique(),

        "duplicate_rows":
            int(duplicate_rows),

        "family_overlap":
            sorted(family_overlap),

        "all_baseline_eligible":
            all_eligible,

        "valid":
            (
                duplicate_rows == 0
                and not family_overlap
                and all_eligible
            ),
    }