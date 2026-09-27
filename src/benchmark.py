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

def extract_problem_id(path):
    """
    Extract a trailing numeric problem ID from a PDDL filename.

    Examples
    --------
    instance-1.pddl -> 1
    problem-12.pddl -> 12
    p03.pddl -> 3

    Returns
    -------
    int or None
        Trailing numeric ID when present.
    """
    import re

    path = Path(path)

    match = re.search(
        r"(\d+)$",
        path.stem,
    )

    if not match:
        return None

    return int(
        match.group(1)
    )

def instance_number(path):
    """
    Return a sortable key for problem filenames.
    """
    path = Path(path)

    problem_id = extract_problem_id(
        path
    )

    if problem_id is not None:
        return (
            0,
            problem_id,
        )

    return (
        1,
        path.stem,
    )


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
    Classify a PDDL domain using its declared requirements.

    The classification separates ordinary propositional classical
    planning from ADL, numeric, temporal, derived, and other advanced
    planning features.

    A domain does not need to explicitly declare :strips to be treated
    as classical. Some benchmark domains declare only extensions such
    as :typing or :equality.

    Parameters
    ----------
    requirements : iterable[str]
        PDDL requirement flags.

    Returns
    -------
    dict
        Classification flags and planning type.
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

    advanced_requirements = {
        ":preferences",
        ":constraints",
        ":goal-utilities",
    }

    basic_classical_requirements = {
        ":strips",
        ":typing",
        ":equality",
        ":negative-preconditions",
        ":action-costs",
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

    is_advanced = bool(
        requirements & advanced_requirements
    )

    has_action_costs = (
        ":action-costs" in requirements
    )

    # Requirements that our simple classical subset does not support.
    unsupported_requirements = (
        requirements
        - basic_classical_requirements
    )

    is_classical_core = (
        not is_temporal
        and not is_numeric
        and not is_adl
        and not is_derived
        and not is_advanced
        and not unsupported_requirements
    )

    # Classical problems including action-cost domains.
    classical_eligible = (
        is_classical_core
    )

    # Simplest first benchmark:
    # classical propositional planning without action costs.
    baseline_eligible = (
        is_classical_core
        and not has_action_costs
    )

    if is_temporal and is_numeric:
        planning_type = "temporal_numeric"

    elif is_temporal:
        planning_type = "temporal"

    elif is_numeric:
        planning_type = "numeric"

    elif is_derived:
        planning_type = "derived"

    elif is_adl:
        planning_type = "adl"

    elif is_advanced:
        planning_type = "advanced"

    elif is_classical_core and has_action_costs:
        planning_type = "classical_cost"

    elif is_classical_core:
        planning_type = "classical"

    else:
        planning_type = "other"

    return {
        "planning_type": planning_type,

        "is_strips": (
            ":strips" in requirements
        ),

        "is_adl": is_adl,
        "is_numeric": is_numeric,
        "is_temporal": is_temporal,
        "is_derived": is_derived,
        "is_advanced": is_advanced,

        "has_action_costs":
            has_action_costs,

        "classical_eligible":
            classical_eligible,

        "baseline_eligible":
            baseline_eligible,

        "unsupported_requirements":
            tuple(
                sorted(
                    unsupported_requirements
                )
            ),
    }

FAMILY_PREFIXES = [
    # More specific prefixes must come before broader ones.
    ("mystery-prime", "mystery"),

    ("pipesworld-no-tankage", "pipesworld"),
    ("pipesworld-tankage", "pipesworld"),
    ("pipesworld", "pipesworld"),

    ("blocks", "blocks"),
    ("logistics", "logistics"),
    ("gripper", "gripper"),
    ("assembly", "assembly"),
    ("grid", "grid"),
    ("movie", "movie"),
    ("mystery", "mystery"),

    ("elevators", "elevator"),
    ("elevator", "elevator"),

    ("schedule", "schedule"),
    ("freecell", "freecell"),

    ("depots", "depots"),
    ("driverlog", "driverlog"),
    ("rovers", "rovers"),
    ("satellite", "satellite"),
    ("zenotravel", "zenotravel"),

    ("airport", "airport"),
    ("psr", "psr"),
    ("promela", "promela"),
    ("umts", "umts"),

    ("openstacks", "openstacks"),
    ("pathways", "pathways"),
    ("storage", "storage"),
    ("trucks", "trucks"),

    ("floor-tile", "floortile"),
    ("floortile", "floortile"),

    ("visit-all", "visitall"),
    ("visitall", "visitall"),

    ("open-stacks", "openstacks"),
    ("openstacks", "openstacks"),

    ("pegsol", "pegsol"),
    ("sokoban", "sokoban"),
    ("transport", "transport"),
    ("visitall", "visitall"),
    ("woodworking", "woodworking"),
    ("scanalyzer", "scanalyzer"),

    ("barman", "barman"),
    ("parking", "parking"),
    ("hiking", "hiking"),
    ("tidybot", "tidybot"),

    ("tpp", "tpp"),
    ("floortile", "floortile"),
    ("nomystery", "nomystery"),
    ("parcprinter", "parcprinter"),

    ("citycar", "citycar"),
    ("maintenance", "maintenance"),
    ("childsnack", "childsnack"),
    ("cavediving", "cavediving"),
    ("tetris", "tetris"),
    ("snake", "snake"),
    ("termes", "termes"),
]


def normalize_planning_family(domain_variant):
    """
    Convert an IPC domain variant name into a broader planning family.

    Examples
    --------
    blocks-strips-typed
        -> blocks

    logistics-round-1-strips
        -> logistics

    barman-sequential-optimal
        -> barman

    pipesworld-no-tankage-nontemporal-strips
        -> pipesworld

    Parameters
    ----------
    domain_variant : str
        Directory/domain variant name.

    Returns
    -------
    str
        Normalized planning-family name.
    """

    import re

    name = str(
        domain_variant
    ).lower().strip()

    name = name.replace(
        "_",
        "-",
    )

    # First use explicit family prefixes.
    for prefix, family in FAMILY_PREFIXES:
        if name == prefix:
            return family

        if name.startswith(
            prefix + "-"
        ):
            return family

    # Generic fallback for domains that are not yet
    # listed in FAMILY_PREFIXES.
    split_patterns = [
        r"-round-\d+",
        r"-strips",
        r"-adl",
        r"-numeric",
        r"-nontemporal",
        r"-temporal",
        r"-sequential",
        r"-propositional",
        r"-metric",
    ]

    for pattern in split_patterns:
        match = re.search(
            pattern,
            name,
        )

        if match:
            name = name[
                :match.start()
            ]
            break

    trailing_qualifiers = [
        "-typed",
        "-untyped",
        "-automatic",
        "-hand-coded",
        "-optimal",
        "-satisficing",
        "-multi-core",
        "-agile",
    ]

    changed = True

    while changed:
        changed = False

        for suffix in trailing_qualifiers:
            if name.endswith(suffix):
                name = name[
                    :-len(suffix)
                ]

                changed = True

    name = name.strip("-")

    if not name:
        return str(
            domain_variant
        ).lower()

    return name

def build_benchmark_index(dataset_root):
    """
    Build a problem-level index of the PDDL benchmark dataset.

    Paths are stored relative to dataset_root so the benchmark
    remains portable across machines and Kaggle users.
    """

    dataset_root = Path(dataset_root)

    if not dataset_root.exists():
        raise FileNotFoundError(
            f"Dataset root not found: {dataset_root}"
        )

    rows = []

    for domain in discover_domains(dataset_root):

        domain_file = Path(
            domain["domain_file"]
        )
        
        planning_family = (
            normalize_planning_family(
                domain["name"]
            )
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

        requirements = extract_requirements(
            domain_file
        )

        classification = classify_requirements(
            requirements
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

            problem_id = extract_problem_id(
                problem_file
            )

            rows.append(
                {
                    "competition":
                        competition,

                    "domain_variant":
                        domain["name"],

                    "planning_family":
                        planning_family,

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

                    "is_advanced":
                        classification[
                            "is_advanced"
                        ],

                    "has_action_costs":
                        classification[
                            "has_action_costs"
                        ],

                    "classical_eligible":
                        classification[
                            "classical_eligible"
                        ],

                    "baseline_eligible":
                        classification[
                            "baseline_eligible"
                        ],

                    "unsupported_requirements":
                        " ".join(
                            classification[
                                "unsupported_requirements"
                            ]
                        ),

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
        "planning_family",
        "problem",
        "problem_id",
        "requirements",
        "planning_type",
        "is_strips",
        "is_adl",
        "is_numeric",
        "is_temporal",
        "is_derived",
        "is_advanced",
        "has_action_costs",
        "classical_eligible",
        "baseline_eligible",
        "unsupported_requirements",
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
                "planning_family",
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