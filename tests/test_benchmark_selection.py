import tempfile
import unittest

from pathlib import Path

import pandas as pd
import yaml

from src.benchmark_selection import (
    build_research_benchmark,
    load_benchmark_config,
    validate_research_benchmark,
)


class TestBenchmarkSelection(unittest.TestCase):

    def create_test_dataframe(self):

        rows = []

        for family, variant, competition in [
            (
                "blocks",
                "blocks-strips-typed",
                "ipc-2000",
            ),
            (
                "logistics",
                "logistics-strips-typed",
                "ipc-2000",
            ),
        ]:

            for problem_id in range(1, 6):

                rows.append(
                    {
                        "planning_family": family,
                        "competition": competition,
                        "domain_variant": variant,

                        "problem":
                            f"instance-{problem_id}.pddl",

                        "problem_id":
                            problem_id,

                        "baseline_eligible":
                            True,

                        "domain_file":
                            f"{family}/domain.pddl",

                        "problem_file":
                            (
                                f"{family}/instances/"
                                f"instance-{problem_id}.pddl"
                            ),
                    }
                )

        return pd.DataFrame(rows)

    def create_config(self, directory):

        config = {
            "benchmark": {
                "name":
                    "test-benchmark",

                "seed":
                    42,

                "max_instances_per_family":
                    3,

                "development_families": {
                    "blocks": {
                        "competition":
                            "ipc-2000",

                        "variant":
                            "blocks-strips-typed",
                    }
                },

                "held_out_families": {
                    "logistics": {
                        "competition":
                            "ipc-2000",

                        "variant":
                            "logistics-strips-typed",
                    }
                },
            }
        }

        path = (
            Path(directory)
            / "benchmark.yaml"
        )

        with open(
            path,
            "w",
            encoding="utf-8",
        ) as file:
            yaml.safe_dump(
                config,
                file,
            )

        return path

    def test_load_config(self):

        with tempfile.TemporaryDirectory() as tmp:

            config_path = (
                self.create_config(tmp)
            )

            config = load_benchmark_config(
                config_path
            )

            self.assertEqual(
                config["name"],
                "test-benchmark",
            )

    def test_build_research_benchmark(self):

        with tempfile.TemporaryDirectory() as tmp:

            benchmark_df = (
                self.create_test_dataframe()
            )

            config_path = (
                self.create_config(tmp)
            )

            selected = (
                build_research_benchmark(
                    benchmark_df,
                    config_path,
                )
            )

            self.assertEqual(
                len(selected),
                6,
            )

            self.assertEqual(
                selected[
                    "benchmark_family"
                ].nunique(),
                2,
            )

            self.assertEqual(
                set(
                    selected[
                        "benchmark_split"
                    ]
                ),
                {
                    "development",
                    "held_out",
                },
            )

    def test_validate_research_benchmark(self):

        with tempfile.TemporaryDirectory() as tmp:

            benchmark_df = (
                self.create_test_dataframe()
            )

            config_path = (
                self.create_config(tmp)
            )

            selected = (
                build_research_benchmark(
                    benchmark_df,
                    config_path,
                )
            )

            result = (
                validate_research_benchmark(
                    selected
                )
            )

            self.assertTrue(
                result["valid"]
            )

            self.assertEqual(
                result["duplicate_rows"],
                0,
            )

            self.assertEqual(
                result["family_overlap"],
                [],
            )


if __name__ == "__main__":
    unittest.main()