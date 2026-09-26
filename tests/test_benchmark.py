import tempfile
import unittest

from pathlib import Path

from src.benchmark import (
    discover_domains,
    discover_problems,
)


class TestBenchmark(unittest.TestCase):

    def test_discover_domains(self):

        with tempfile.TemporaryDirectory() as tmp:

            root = Path(tmp)

            domain_dir = (
                root
                / "ipc-2000"
                / "domains"
                / "blocks"
            )

            instances_dir = (
                domain_dir
                / "instances"
            )

            instances_dir.mkdir(
                parents=True
            )

            (
                domain_dir / "domain.pddl"
            ).write_text(
                "(define (domain blocks))",
                encoding="utf-8",
            )

            (
                instances_dir / "instance-1.pddl"
            ).write_text(
                "(define (problem p1))",
                encoding="utf-8",
            )

            domains = discover_domains(root)

            self.assertEqual(
                len(domains),
                1,
            )

            self.assertEqual(
                domains[0]["name"],
                "blocks",
            )

            self.assertEqual(
                domains[0]["num_instances"],
                1,
            )

    def test_discover_problems_numeric_order(self):

        with tempfile.TemporaryDirectory() as tmp:

            domain_dir = Path(tmp)

            instances_dir = (
                domain_dir / "instances"
            )

            instances_dir.mkdir()

            for number in [
                10,
                2,
                1,
            ]:
                (
                    instances_dir
                    / f"instance-{number}.pddl"
                ).write_text(
                    "(problem)",
                    encoding="utf-8",
                )

            problems = discover_problems(
                domain_dir
            )

            names = [
                problem.name
                for problem in problems
            ]

            self.assertEqual(
                names,
                [
                    "instance-1.pddl",
                    "instance-2.pddl",
                    "instance-10.pddl",
                ],
            )


if __name__ == "__main__":
    unittest.main()