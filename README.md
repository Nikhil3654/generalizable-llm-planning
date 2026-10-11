# Generalizable LLM Planning

Research project investigating generalization in language-model-based classical AI planning.

The initial work focuses on establishing reproducible planning baselines using public PDDL planning problems before testing methods intended to improve generalization across unseen planning domains.

## Project Structure

```text
configs/       Experiment configurations
src/           Core project code
kaggle/        Kaggle experiment notebooks
experiments/   Experiment results
tests/         Basic project tests
outputs/       Generated outputs
```

## Dataset

The project uses public classical planning problems represented in PDDL.

The working dataset is accessed through Kaggle so that experiments can run without manually transferring the full dataset between machines.

### Accessing the Dataset in Kaggle

Open the project notebook in Kaggle and select:

**Add Input → Datasets**

Search for the planning dataset used by the project and attach it to the notebook.

Kaggle datasets are normally available under:

```text
/kaggle/input/
```

For example:

```text
/kaggle/input/DATASET-NAME/
```

The exact dataset name and folder path will be updated here once the initial benchmark dataset is finalized.

The notebook should not modify the original dataset. Generated files should instead be written to:

```text
/kaggle/working/
```

## Installation

For local development:

```bash
pip install -r requirements.txt
```

Kaggle already contains many common Python and machine-learning packages. Missing dependencies can be installed inside the notebook when required.

## Initial Goal

The first stage of the project is to create a functioning baseline pipeline:

```text
PDDL Problem
    ↓
Language Model
    ↓
Generated Plan
    ↓
Plan Evaluation
    ↓
Experimental Results
```

Further methods and evaluation procedures will be added after the baseline system is working.

## Plan Validation

Generated plans are checked using the VAL plan validation system.

The validation pipeline takes:

```text
PDDL Domain
      +
PDDL Problem
      +
Proposed Plan
      ↓
VAL
      ↓
VALID / INVALID
```

The reusable validation wrapper is located at:

`src/validator.py`

Unit tests are located at:

`tests/test_validator.py`

The Kaggle integration notebook is:

`kaggle/02_plan_validation.ipynb`

The notebook tests the validator using a correct Fast Downward plan and several deliberately modified plans.

VAL is built inside the Kaggle environment and is not stored in this repository.

## Dataset

The project uses classical PDDL planning instances from the
`potassco/pddl-instances` benchmark collection.

The benchmark contains planning domains and problem instances from
multiple International Planning Competitions (IPC).

For Kaggle experiments, the repository is imported as a Kaggle Dataset
and attached to the notebook as an input.

The dataset is available inside Kaggle under:

    /kaggle/input/<dataset-name>/

Dataset files are treated as read-only. Experiment outputs are written
to:

    /kaggle/working/