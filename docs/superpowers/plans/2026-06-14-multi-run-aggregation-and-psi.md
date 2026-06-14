# Multi-Run Aggregation and PSI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make a completed 36-run mini pilot directly analyzable through validated run-level aggregation, Horizon random-exploration integration, standardised prompt effects, and project-defined PSI outputs.

**Architecture:** Extend the pilot writer so every logical run has a seed-specific filename and reproducibility metadata. Add a first-stage aggregator that validates raw JSON and writes one row per run plus a quality report, then add a second-stage PSI module that reads the flat table and writes descriptive summaries, effect rows, PSI rows, and an analysis report.

**Tech Stack:** Python 3.10+, standard-library `argparse`, `csv`, `hashlib`, `json`, `pathlib`, `statistics`, existing NumPy/SciPy Horizon choice model, `unittest`.

---

## File Structure

### Create

- `src/aggregate_experiment_results.py`
  - Raw JSON discovery, run identity, duplicate resolution, eligibility checks,
    paired-seed validation, derived metrics, Horizon model integration, CSV and
    quality-report writing.
- `src/compute_prompt_sensitivity.py`
  - Run-table loading, descriptive summaries, variance handling, signed
    standardised effects, PSI calculation, and analysis output writing.
- `tests/test_aggregate_experiment_results.py`
  - Synthetic JSON tests for aggregation, strict/incomplete behavior,
    duplicates, pairing, provenance, and Horizon integration.
- `tests/test_prompt_sensitivity.py`
  - Synthetic run-table tests for summaries, denominator rules, effects, PSI,
    and strict/incomplete behavior.

### Modify

- `src/run_llm_pilot.py`
  - Canonical task-seed derivation, seed-specific filenames, and provenance.
- `src/horizon_random_exploration.py`
  - Shared deterministic LLM run identifier helper.
- `tests/test_llm_pilot.py`
  - Filename, provenance, and subset seed-offset regression tests.
- `tests/test_horizon_random_exploration.py`
  - Run identifier behavior.
- `configs/experiment_config_stage01.json`
  - Primary PSI metric lists and variance policy.
- `README.md`
  - Current mini-pilot commands and analysis workflow.
- `docs/data_schema.md`
  - Run-level, quality-report, effect, and PSI schemas.
- `docs/next_steps_plan.md`
  - Mark aggregation/PSI implementation complete after verification.
- `docs/research_log.md`
  - Record implementation decisions and fresh test evidence.

## Task 1: Make Pilot Runs Seed-Safe and Reproducible

**Files:**
- Modify: `tests/test_llm_pilot.py`
- Modify: `src/run_llm_pilot.py`

- [ ] **Step 1: Add failing filename and provenance assertions**

Update the successful-pilot test to expect a seed-specific file and required
provenance:

```python
path = output_dir / "igt_baseline_seed-124.json"
self.assertTrue(path.exists())
data = json.loads(path.read_text(encoding="utf-8"))
self.assertEqual(data["seed"], 124)
self.assertEqual(data["config_name"], "experiment_config_stage01")
self.assertEqual(
    data["config_version"],
    str(load_config(Path("configs/experiment_config_stage01.json"))["version"]),
)
self.assertEqual(data["prompt_path"], "prompts/igt/baseline.md")
self.assertRegex(data["prompt_sha256"], r"^[0-9a-f]{64}$")
```

The expected IGT seed is `124` because canonical offsets are Horizon `+0`, IGT
`+1`, and BART `+2`, regardless of whether a subset is run.

- [ ] **Step 2: Add a failing subset-seed regression test**

```python
def test_single_task_uses_canonical_task_seed_offset(self):
    with tempfile.TemporaryDirectory() as tmpdir:
        result = run_llm_pilot(
            client=FakePilotClient(),
            model="gpt-test",
            seed=100,
            output_dir=Path(tmpdir),
            prompt_condition="risk_emphasis",
            task_names=("bart",),
        )

        self.assertEqual(result["bart"]["seed"], 102)
        self.assertTrue(
            (Path(tmpdir) / "bart_risk_emphasis_seed-102.json").exists()
        )
```

- [ ] **Step 3: Add a failing failed-output filename assertion**

Change the failure test to require:

```python
path = output_dir / "igt_baseline_seed-124_failed.json"
```

- [ ] **Step 4: Run the pilot tests and verify the expected failures**

Run:

```powershell
uv run python -m unittest tests.test_llm_pilot
```

Expected: failures because canonical subset offsets, seed-specific filenames,
summary seed fields, and provenance fields are not implemented.

- [ ] **Step 5: Implement canonical task seed derivation**

Add:

```python
TASK_SEED_OFFSETS = {
    task: index for index, task in enumerate(ALL_TASKS)
}


def task_seed(base_seed: int, task: str) -> int:
    try:
        return base_seed + TASK_SEED_OFFSETS[task]
    except KeyError as exc:
        raise ValueError(f"Unknown task name: {task!r}") from exc
```

Replace the `enumerate(task_names)` offset with:

```python
current_seed = task_seed(seed, task)
```

- [ ] **Step 6: Implement seed-specific paths**

Add:

```python
def pilot_output_path(
    output_dir: Path,
    *,
    task: str,
    prompt_condition: str,
    seed: int,
    failed: bool = False,
) -> Path:
    suffix = "_failed" if failed else ""
    return output_dir / (
        f"{task}_{prompt_condition}_seed-{seed}{suffix}.json"
    )
```

Use the helper for success, failure, and summary paths.

- [ ] **Step 7: Add prompt and configuration provenance**

Use the configured prompt path and hash the exact loaded template:

```python
import hashlib


def prompt_sha256(template: str) -> str:
    return hashlib.sha256(template.encode("utf-8")).hexdigest()
```

Pass the following into both complete and partial outputs:

```python
"config_name": str(config["config_name"]),
"config_version": str(config["version"]),
"prompt_path": str(config["tasks"][task]["prompt_paths"][prompt_condition]),
"prompt_sha256": prompt_sha256(template),
```

Include `"seed"` in each returned summary.

- [ ] **Step 8: Run pilot tests**

Run:

```powershell
uv run python -m unittest tests.test_llm_pilot
```

Expected: all pilot tests pass.

- [ ] **Step 9: Commit**

```powershell
git add src/run_llm_pilot.py tests/test_llm_pilot.py
git commit -m "feat: make pilot run outputs seed-safe"
```

## Task 2: Stabilize Horizon Run Identity

**Files:**
- Modify: `tests/test_horizon_random_exploration.py`
- Modify: `src/horizon_random_exploration.py`

- [ ] **Step 1: Add a failing deterministic run-ID test**

```python
from src.horizon_random_exploration import llm_run_id


def test_llm_run_id_uses_resolved_source_path_and_seed(self):
    path = Path("outputs/example.json")
    expected = f"{path.resolve().as_posix()}:seed=42"
    self.assertEqual(llm_run_id(path, 42), expected)
```

- [ ] **Step 2: Run the focused test and verify failure**

Run:

```powershell
uv run python -m unittest tests.test_horizon_random_exploration
```

Expected: import failure because `llm_run_id` does not exist.

- [ ] **Step 3: Implement and use the shared identifier**

```python
def llm_run_id(path: Path, seed: Any) -> str:
    return f"{path.resolve().as_posix()}:seed={seed}"
```

Replace the inline `run_id` construction in
`load_llm_choice_observations()` with this helper.

- [ ] **Step 4: Run Horizon model tests**

Run:

```powershell
uv run python -m unittest tests.test_horizon_random_exploration
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```powershell
git add src/horizon_random_exploration.py tests/test_horizon_random_exploration.py
git commit -m "refactor: stabilize horizon run identifiers"
```

## Task 3: Build the Run-Level Aggregation Core

**Files:**
- Create: `tests/test_aggregate_experiment_results.py`
- Create: `src/aggregate_experiment_results.py`

- [ ] **Step 1: Create reusable synthetic pilot fixture helpers**

In the test file, add:

```python
def write_pilot(
    path: Path,
    *,
    task: str,
    condition: str,
    seed: int,
    metrics: dict,
    done: bool = True,
    model: str = "gpt-test",
    prompt_hash: str = "a" * 64,
    config_version: str = "0.3",
    trial_records: list[dict] | None = None,
) -> Path:
    payload = {
        "task": task,
        "prompt_condition": condition,
        "model": model,
        "seed": seed,
        "done": done,
        "config_name": "experiment_config_stage01",
        "config_version": config_version,
        "prompt_path": f"prompts/{task}/{condition}.md",
        "prompt_sha256": prompt_hash,
        "trial_records": trial_records or [],
        "invalid_responses": [],
        "parse_success_rate": 1.0,
        "run_metrics": metrics,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path
```

- [ ] **Step 2: Add a failing run-row extraction test**

```python
def test_extract_run_row_flattens_metrics_and_derives_igt_learning_change(self):
    payload = {
        "task": "igt",
        "prompt_condition": "baseline",
        "model": "gpt-test",
        "seed": 11,
        "done": True,
        "config_name": "experiment_config_stage01",
        "config_version": "0.3",
        "prompt_path": "prompts/igt/baseline.md",
        "prompt_sha256": "a" * 64,
        "trial_records": [{}] * 100,
        "invalid_responses": [],
        "parse_success_rate": 1.0,
        "run_metrics": {
            "n_trials": 100,
            "advantageous_choice_rate": 0.7,
            "post_loss_switching_rate": 0.4,
            "block_wise_learning_curve": {
                "1": -4,
                "2": 0,
                "3": 4,
                "4": 8,
                "5": 12,
            },
        },
    }

    row = extract_run_row(Path("run.json"), payload)

    self.assertEqual(row["run_id"], "igt:baseline:11")
    self.assertEqual(row["n_trials"], 100)
    self.assertEqual(row["learning_curve_change"], 16.0)
    self.assertEqual(row["invalid_response_count"], 0)
```

- [ ] **Step 3: Add failing discovery and legacy-filename tests**

Create nested files whose names do not contain seeds, call
`discover_json_paths()`, then assert that eligibility and identity use JSON
content rather than filename conventions.

- [ ] **Step 4: Run the aggregation tests and verify failure**

Run:

```powershell
uv run python -m unittest tests.test_aggregate_experiment_results
```

Expected: import failure because the aggregation module does not exist.

- [ ] **Step 5: Implement discovery, loading, and row extraction**

Define:

```python
RUN_METADATA_COLUMNS = (
    "run_id",
    "task",
    "prompt_condition",
    "model",
    "seed",
    "config_name",
    "config_version",
    "prompt_path",
    "prompt_sha256",
    "done",
    "n_trials",
    "parse_success_rate",
    "invalid_response_count",
    "source_path",
)
```

Implement:

```python
def discover_json_paths(inputs: Iterable[Path]) -> list[Path]:
    paths: set[Path] = set()
    for input_path in inputs:
        if input_path.is_dir():
            paths.update(input_path.rglob("*.json"))
        elif input_path.suffix.lower() == ".json":
            paths.add(input_path)
    return sorted(path.resolve() for path in paths)


def load_candidate(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def logical_run_id(task: str, condition: str, seed: int) -> str:
    return f"{task}:{condition}:{seed}"


def extract_run_row(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    metrics = payload["run_metrics"]
    task = str(payload["task"])
    condition = str(payload["prompt_condition"])
    seed = int(payload["seed"])
    row: dict[str, Any] = {
        "run_id": logical_run_id(task, condition, seed),
        "task": task,
        "prompt_condition": condition,
        "model": str(payload["model"]),
        "seed": seed,
        "config_name": str(payload.get("config_name", "")),
        "config_version": str(payload.get("config_version", "")),
        "prompt_path": str(payload.get("prompt_path", "")),
        "prompt_sha256": str(payload.get("prompt_sha256", "")),
        "done": bool(payload["done"]),
        "n_trials": int(
            metrics.get("n_trials", len(payload.get("trial_records", [])))
        ),
        "parse_success_rate": float(payload.get("parse_success_rate", 0.0)),
        "invalid_response_count": len(payload.get("invalid_responses", [])),
        "source_path": str(path.resolve()),
    }
    for name, value in metrics.items():
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            row[name] = value
    curve = metrics.get("block_wise_learning_curve")
    if task == "igt" and isinstance(curve, dict):
        row["learning_curve_change"] = (
            float(curve["5"]) - float(curve["1"])
        )
    return row
```

`extract_run_row()` copies scalar numeric metrics and derives:

```python
curve = metrics.get("block_wise_learning_curve")
if task == "igt" and isinstance(curve, dict):
    row["learning_curve_change"] = float(curve["5"]) - float(curve["1"])
```

Use the top-level trial count only as a fallback:

```python
row["n_trials"] = metrics.get("n_trials", len(payload.get("trial_records", [])))
```

- [ ] **Step 6: Run focused tests**

Run:

```powershell
uv run python -m unittest tests.test_aggregate_experiment_results
```

Expected: extraction and discovery tests pass.

- [ ] **Step 7: Commit**

```powershell
git add src/aggregate_experiment_results.py tests/test_aggregate_experiment_results.py
git commit -m "feat: extract run-level experiment metrics"
```

## Task 4: Add Duplicate, Completeness, Pairing, and Provenance Validation

**Files:**
- Modify: `tests/test_aggregate_experiment_results.py`
- Modify: `src/aggregate_experiment_results.py`

- [ ] **Step 1: Add failing duplicate-policy tests**

Test default failure:

```python
with self.assertRaises(AggregationValidationError) as context:
    aggregate_experiment_results(
        [root],
        expected_runs_per_cell=1,
        duplicate_policy="error",
        allow_incomplete=False,
        config=config,
    )
self.assertIn("duplicate_run", context.exception.issue_codes)
```

Test `latest` selection by setting file modification times with `os.utime()` and
asserting the newer successful file is selected and both candidates appear in
the duplicate report.

- [ ] **Step 2: Add failing strict and incomplete missing-cell tests**

Build a synthetic batch with one absent condition:

```python
with self.assertRaises(AggregationValidationError):
    aggregate_experiment_results(
        [root],
        expected_runs_per_cell=3,
        allow_incomplete=False,
        config=config,
    )

result = aggregate_experiment_results(
    [root],
    expected_runs_per_cell=3,
    allow_incomplete=True,
    config=config,
)
self.assertFalse(result.quality_report["analysis_complete"])
self.assertIn(
    "missing_run",
    {issue["code"] for issue in result.quality_report["issues"]},
)
```

- [ ] **Step 3: Add failing paired-seed and provenance tests**

Cover:

- condition seed sets `{1, 2, 3}` versus `{1, 2, 4}` gives
  `unpaired_seed`;
- mixed model IDs give `mixed_model`;
- mixed configuration versions give `mixed_config_version`;
- more than one prompt hash inside the same `task x condition` gives
  `mixed_prompt_hash`;
- different hashes across different prompt conditions are valid.

- [ ] **Step 4: Add a failed-run audit test**

Write a `done=false` payload and assert that it is absent from rows but appears
as `failed_run` in the report.

- [ ] **Step 5: Run tests and verify validation failures**

Run:

```powershell
uv run python -m unittest tests.test_aggregate_experiment_results
```

Expected: new tests fail because validation and duplicate resolution are absent.

- [ ] **Step 6: Implement structured issues and exceptions**

Add:

```python
@dataclass(frozen=True)
class ValidationIssue:
    code: str
    severity: str
    message: str
    details: dict[str, Any]


class AggregationValidationError(ValueError):
    def __init__(self, issues: list[ValidationIssue]) -> None:
        self.issues = issues
        self.issue_codes = tuple(issue.code for issue in issues)
        super().__init__("Aggregation validation failed: " + ", ".join(self.issue_codes))
```

Add an `AggregationResult` dataclass containing rows and the quality report.

- [ ] **Step 7: Implement duplicate resolution**

Group candidates by:

```python
(payload["task"], payload["prompt_condition"], int(payload["seed"]))
```

For `latest`, select the completed candidate with the greatest:

```python
path.stat().st_mtime_ns
```

If no candidate is completed, retain no row and record `failed_run`.

- [ ] **Step 8: Implement completeness and pairing validation**

Use the configured task-condition matrix. For every cell:

- compare valid row count with `expected_runs_per_cell`;
- record `missing_run` or `unexpected_run`;
- compare condition seed sets within each task;
- record expected, observed, missing, and extra seeds.

Strict mode raises after the complete report is built. In incomplete mode,
errors remain in the report and `analysis_complete` is false.

- [ ] **Step 9: Implement provenance validation**

Rules:

- exactly one model across valid rows;
- exactly one `config_name + config_version` pair;
- exactly one prompt path and prompt hash inside each task-condition cell;
- legacy missing provenance is a warning in incomplete mode and an error in
  strict mode;
- different task-condition cells are expected to have different prompt hashes.

- [ ] **Step 10: Run aggregation tests**

Run:

```powershell
uv run python -m unittest tests.test_aggregate_experiment_results
```

Expected: duplicate, completeness, pairing, failed-run, and provenance tests
pass.

- [ ] **Step 11: Commit**

```powershell
git add src/aggregate_experiment_results.py tests/test_aggregate_experiment_results.py
git commit -m "feat: validate multi-run experiment batches"
```

## Task 5: Integrate Horizon Random-Exploration Estimates

**Files:**
- Modify: `tests/test_aggregate_experiment_results.py`
- Modify: `src/aggregate_experiment_results.py`

- [ ] **Step 1: Add a failing pure estimate-merge test**

```python
def test_apply_horizon_estimates_matches_source_runs(self):
    rows = [
        {
            "task": "horizon",
            "prompt_condition": "baseline",
            "seed": 1,
            "source_path": str(Path("a.json").resolve()),
        },
        {
            "task": "horizon",
            "prompt_condition": "baseline",
            "seed": 2,
            "source_path": str(Path("b.json").resolve()),
        },
    ]
    estimates = {
        llm_run_id(Path("a.json"), 1): 1.5,
        llm_run_id(Path("b.json"), 2): 2.5,
    }

    apply_horizon_run_estimates(rows, estimates)

    self.assertEqual(rows[0]["random_exploration_effect"], 1.5)
    self.assertEqual(rows[1]["random_exploration_effect"], 2.5)
```

- [ ] **Step 2: Add failing insufficient-run and nonconvergence tests**

Assert:

- one Horizon run yields `random_exploration_insufficient_runs`;
- a condition result with `converged=false` yields
  `random_exploration_not_converged`;
- strict mode raises;
- incomplete mode leaves the metric blank and records the issue.

- [ ] **Step 3: Add a real-model integration test**

Generate three synthetic Horizon JSON files per condition. Each file must
contain 40 first-free-choice records split across both horizons with varying
reward and information differences. Call the existing:

```python
load_llm_choice_observations(paths)
analyze_choice_observations(observations)
```

Assert that all three run rows receive finite
`random_exploration_effect` values. The existing Horizon-model tests remain the
primary parameter-recovery tests; this test verifies data plumbing.

- [ ] **Step 4: Run focused tests and verify failure**

Run:

```powershell
uv run python -m unittest tests.test_aggregate_experiment_results
```

Expected: failures because Horizon estimates are not integrated.

- [ ] **Step 5: Implement condition-wise estimation**

Add:

```python
def estimate_horizon_random_exploration(
    selected_paths: list[Path],
) -> tuple[dict[str, float], list[ValidationIssue]]:
    horizon_paths = []
    for path in selected_paths:
        payload = load_candidate(path)
        if payload and payload.get("task") == "horizon" and payload.get("done"):
            horizon_paths.append(path)

    observations = load_llm_choice_observations(horizon_paths)
    condition_results = analyze_choice_observations(observations)
    estimates: dict[str, float] = {}
    issues: list[ValidationIssue] = []

    for condition, result in sorted(condition_results.items()):
        if result["status"] != "ok":
            issues.append(
                ValidationIssue(
                    code="random_exploration_insufficient_runs",
                    severity="error",
                    message=f"{condition} has too few Horizon runs.",
                    details={"condition": condition, "n_runs": result["n_runs"]},
                )
            )
            continue
        if not result["converged"]:
            issues.append(
                ValidationIssue(
                    code="random_exploration_not_converged",
                    severity="error",
                    message=f"{condition} Horizon fit did not converge.",
                    details={
                        "condition": condition,
                        "optimizer_message": result["optimizer_message"],
                    },
                )
            )
            continue
        for run_estimate in result["run_estimates"]:
            estimates[run_estimate["run_id"]] = float(
                run_estimate["random_exploration_effect"]
            )
    return estimates, issues
```

Workflow:

1. filter selected completed Horizon paths;
2. load first-free-choice observations;
3. call `analyze_choice_observations`;
4. reject `insufficient_runs`;
5. reject nonconverged fits;
6. flatten each condition's `run_estimates` to
   `run_id -> random_exploration_effect`.

- [ ] **Step 6: Implement estimate merge**

```python
def apply_horizon_run_estimates(
    rows: list[dict[str, Any]],
    estimates: dict[str, float],
) -> None:
    for row in rows:
        if row["task"] != "horizon":
            continue
        key = llm_run_id(Path(row["source_path"]), row["seed"])
        if key in estimates:
            row["random_exploration_effect"] = estimates[key]
```

Require the metric for Horizon eligibility after estimation.

- [ ] **Step 7: Run aggregation and Horizon tests**

Run:

```powershell
uv run python -m unittest tests.test_aggregate_experiment_results tests.test_horizon_random_exploration
```

Expected: all tests pass.

- [ ] **Step 8: Commit**

```powershell
git add src/aggregate_experiment_results.py tests/test_aggregate_experiment_results.py
git commit -m "feat: aggregate horizon random exploration"
```

## Task 6: Write Aggregation CSV, Quality Report, and CLI

**Files:**
- Modify: `tests/test_aggregate_experiment_results.py`
- Modify: `src/aggregate_experiment_results.py`

- [ ] **Step 1: Add failing output tests**

```python
def test_write_aggregation_outputs_creates_stable_csv_and_report(self):
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        result = AggregationResult(
            rows=[
                {
                    "run_id": "bart:baseline:1",
                    "task": "bart",
                    "prompt_condition": "baseline",
                    "model": "gpt-test",
                    "seed": 1,
                    "config_name": "experiment_config_stage01",
                    "config_version": "0.4",
                    "prompt_path": "prompts/bart/baseline.md",
                    "prompt_sha256": "a" * 64,
                    "done": True,
                    "n_trials": 40,
                    "parse_success_rate": 1.0,
                    "invalid_response_count": 0,
                    "source_path": str(Path("bart.json").resolve()),
                    "adjusted_average_pumps": 8.0,
                }
            ],
            quality_report={
                "analysis_complete": True,
                "issues": [],
                "valid_run_count": 1,
            },
        )
        write_aggregation_outputs(result, output_dir)

        csv_path = output_dir / "llm_run_metrics.csv"
        report_path = output_dir / "aggregation_quality_report.json"
        self.assertTrue(csv_path.exists())
        self.assertTrue(report_path.exists())
        with csv_path.open(newline="", encoding="utf-8") as handle:
            csv_rows = list(csv.DictReader(handle))
        self.assertEqual(csv_rows[0]["run_id"], "bart:baseline:1")
```

Also assert deterministic row ordering by task order, condition order, then
numeric seed.

- [ ] **Step 2: Run tests and verify failure**

Run:

```powershell
uv run python -m unittest tests.test_aggregate_experiment_results
```

Expected: failure because output writers and CLI-facing orchestration are absent.

- [ ] **Step 3: Implement stable CSV writing**

Write metadata columns first, then sorted metric columns. Use UTF-8 and
`newline=""`. Serialize booleans as `true`/`false`; write missing values as
empty cells.

- [ ] **Step 4: Implement quality-report writing before strict failure**

Add:

```python
def run_aggregation(
    inputs: list[Path],
    *,
    output_dir: Path,
    expected_runs_per_cell: int,
    duplicate_policy: str,
    allow_incomplete: bool,
    config_path: Path,
) -> AggregationResult:
    if expected_runs_per_cell < 1:
        raise ValueError("expected_runs_per_cell must be at least 1.")
    config = load_config(config_path)
    result = aggregate_experiment_results(
        inputs,
        expected_runs_per_cell=expected_runs_per_cell,
        duplicate_policy=duplicate_policy,
        allow_incomplete=allow_incomplete,
        config=config,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    write_aggregation_outputs(result, output_dir)
    errors = [
        issue
        for issue in result.quality_report["issues"]
        if issue["severity"] == "error"
    ]
    if errors and not allow_incomplete:
        raise AggregationValidationError(
            [ValidationIssue(**issue) for issue in errors]
        )
    return result
```

Always create the output directory and write
`aggregation_quality_report.json`. Write `llm_run_metrics.csv` only when valid
rows exist. After writing the report, raise `AggregationValidationError` in
strict mode if error-severity issues exist.

- [ ] **Step 5: Implement CLI**

Arguments:

```text
inputs
--output-dir
--expected-runs-per-cell
--duplicate-policy {error,latest}
--allow-incomplete
--config
```

Validate `expected_runs_per_cell >= 1`.

- [ ] **Step 6: Run aggregation tests**

Run:

```powershell
uv run python -m unittest tests.test_aggregate_experiment_results
```

Expected: all aggregation tests pass.

- [ ] **Step 7: Commit**

```powershell
git add src/aggregate_experiment_results.py tests/test_aggregate_experiment_results.py
git commit -m "feat: add aggregation reports and CLI"
```

## Task 7: Configure the Primary PSI Definition

**Files:**
- Modify: `configs/experiment_config_stage01.json`
- Modify: `tests/test_prompt_sensitivity.py`

- [ ] **Step 1: Add a failing config-policy test**

Create the PSI test file and assert:

```python
config = load_config(Path("configs/experiment_config_stage01.json"))
policy = config["analysis"]["prompt_sensitivity"]

self.assertEqual(
    policy["primary_metrics"]["horizon"],
    [
        "directed_exploration",
        "horizon_effect",
        "random_exploration_effect",
    ],
)
self.assertEqual(
    policy["primary_metrics"]["igt"],
    [
        "advantageous_choice_rate",
        "learning_curve_change",
        "post_loss_switching_rate",
    ],
)
self.assertEqual(
    policy["primary_metrics"]["bart"],
    [
        "adjusted_average_pumps",
        "explosion_rate",
        "post_explosion_adjustment",
    ],
)
self.assertEqual(policy["zero_tolerance"], 1e-12)
self.assertEqual(policy["minimum_partial_metrics"], 2)
```

- [ ] **Step 2: Run the config test and verify failure**

Run:

```powershell
uv run python -m unittest tests.test_prompt_sensitivity
```

Expected: failure because the config lacks these fields.

- [ ] **Step 3: Add the explicit policy**

Extend `analysis.prompt_sensitivity` with:

```json
{
  "primary_metrics": {
    "horizon": [
      "directed_exploration",
      "horizon_effect",
      "random_exploration_effect"
    ],
    "igt": [
      "advantageous_choice_rate",
      "learning_curve_change",
      "post_loss_switching_rate"
    ],
    "bart": [
      "adjusted_average_pumps",
      "explosion_rate",
      "post_explosion_adjustment"
    ]
  },
  "zero_tolerance": 1e-12,
  "minimum_partial_metrics": 2,
  "bounded_metrics": [
    "directed_exploration",
    "horizon_effect",
    "advantageous_choice_rate",
    "post_loss_switching_rate",
    "explosion_rate"
  ],
  "low_variance_absolute_threshold": 1e-6,
  "low_variance_relative_threshold": 1e-6
}
```

Increment config version to `0.4` and update status to:

```text
prompt_matrix_frozen_bart_human_filtered_psi_pipeline
```

- [ ] **Step 4: Run the config test**

Run:

```powershell
uv run python -m unittest tests.test_prompt_sensitivity
```

Expected: config-policy test passes.

- [ ] **Step 5: Commit**

```powershell
git add configs/experiment_config_stage01.json tests/test_prompt_sensitivity.py
git commit -m "config: freeze primary PSI metrics"
```

## Task 8: Implement Descriptive Summaries and Standardised Effects

**Files:**
- Modify: `tests/test_prompt_sensitivity.py`
- Create: `src/compute_prompt_sensitivity.py`

- [ ] **Step 1: Add failing summary-statistic tests**

```python
def test_summarise_metric_uses_sample_standard_deviation(self):
    summary = summarise_values([1.0, 2.0, 3.0])
    self.assertEqual(summary["n"], 3)
    self.assertEqual(summary["mean"], 2.0)
    self.assertEqual(summary["sd"], 1.0)
    self.assertEqual(summary["median"], 2.0)
    self.assertEqual(summary["minimum"], 1.0)
    self.assertEqual(summary["maximum"], 3.0)
```

- [ ] **Step 2: Add failing baseline-SD effect test**

```python
def test_compute_standardised_effect_uses_baseline_sd(self):
    result = compute_standardised_effect(
        baseline_values=[1.0, 2.0, 3.0],
        condition_values=[3.0, 4.0, 5.0],
        metric="adjusted_average_pumps",
        policy=policy,
        allow_incomplete=False,
    )

    self.assertEqual(result["raw_mean_difference"], 2.0)
    self.assertEqual(result["denominator"], 1.0)
    self.assertEqual(result["sd_source"], "baseline")
    self.assertEqual(result["signed_standardised_effect"], 2.0)
    self.assertEqual(result["absolute_standardised_effect"], 2.0)
```

- [ ] **Step 3: Add failing denominator edge-case tests**

Cover:

```python
# baseline constant, condition variable -> pooled fallback
baseline_values = [1.0, 1.0, 1.0]
condition_values = [1.0, 2.0, 3.0]

# both constant and equal -> effect zero
baseline_values = [1.0, 1.0, 1.0]
condition_values = [1.0, 1.0, 1.0]

# both constant and unequal -> strict error
baseline_values = [1.0, 1.0, 1.0]
condition_values = [2.0, 2.0, 2.0]
```

Assert `sd_source` values `pooled_fallback`, `constant_equal`, and the issue
code `zero_variance_undefined_effect`.

- [ ] **Step 4: Add a failing low-variance warning test**

For a bounded metric:

```python
baseline_values = [0.5, 0.5000001, 0.4999999]
condition_values = [0.6, 0.6, 0.6]
```

Assert `low_baseline_variance` is present while `sd_source` remains
`baseline`.

- [ ] **Step 5: Run focused tests and verify failure**

Run:

```powershell
uv run python -m unittest tests.test_prompt_sensitivity
```

Expected: import failure because the PSI module does not exist.

- [ ] **Step 6: Implement numeric parsing and summaries**

Define:

```python
def parse_optional_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    number = float(text)
    return number if math.isfinite(number) else None


def summarise_values(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {
            "n": 0,
            "mean": None,
            "sd": None,
            "median": None,
            "minimum": None,
            "maximum": None,
        }
    return {
        "n": len(values),
        "mean": statistics.mean(values),
        "sd": statistics.stdev(values) if len(values) >= 2 else None,
        "median": statistics.median(values),
        "minimum": min(values),
        "maximum": max(values),
    }


def pooled_sd(baseline_sd: float, condition_sd: float) -> float:
    return math.sqrt((baseline_sd**2 + condition_sd**2) / 2.0)
```

Use `statistics.stdev()` only when `len(values) >= 2`; otherwise return
`sd=None`.

- [ ] **Step 7: Implement standardised effects**

Define a structured `PromptSensitivityValidationError` carrying issue codes.
Implement the exact five variance rules from the approved design.

For relative low variance:

```python
scale = max(abs(baseline_mean), abs(condition_mean), 1.0)
is_low = baseline_sd / scale <= policy["low_variance_relative_threshold"]
```

For configured bounded metrics, use the absolute threshold instead.

- [ ] **Step 8: Run PSI tests**

Run:

```powershell
uv run python -m unittest tests.test_prompt_sensitivity
```

Expected: summary and effect tests pass.

- [ ] **Step 9: Commit**

```powershell
git add src/compute_prompt_sensitivity.py tests/test_prompt_sensitivity.py
git commit -m "feat: compute standardised prompt effects"
```

## Task 9: Implement PSI, Completeness Checks, and Analysis Outputs

**Files:**
- Modify: `tests/test_prompt_sensitivity.py`
- Modify: `src/compute_prompt_sensitivity.py`

- [ ] **Step 1: Add failing complete PSI test**

Use three effects with absolute values `1`, `2`, and `3`:

```python
row = compute_psi_row(
    task="bart",
    condition="risk_emphasis",
    expected_metrics=[
        "adjusted_average_pumps",
        "explosion_rate",
        "post_explosion_adjustment",
    ],
    effect_rows=[
        {"metric": "adjusted_average_pumps", "absolute_standardised_effect": 1.0},
        {"metric": "explosion_rate", "absolute_standardised_effect": 2.0},
        {"metric": "post_explosion_adjustment", "absolute_standardised_effect": 3.0},
    ],
    minimum_partial_metrics=2,
    allow_incomplete=False,
)

self.assertEqual(row["psi"], 2.0)
self.assertEqual(row["valid_metric_count"], 3)
self.assertEqual(row["status"], "complete")
```

- [ ] **Step 2: Add failing partial PSI tests**

Assert:

- strict mode rejects two valid effects out of three;
- incomplete mode averages two effects, marks `status=partial`, and reports the
  excluded metric;
- one valid effect produces no PSI value.

- [ ] **Step 3: Add failing run-table completeness tests**

Create run rows with:

- exactly three paired seeds across four conditions: valid;
- a missing row: strict failure, incomplete warning;
- unpaired seed sets: strict failure;
- missing primary metric cells: strict failure.

- [ ] **Step 4: Add failing deterministic output tests**

Write a shuffled synthetic run table, run the complete analysis, and assert
stable ordering:

```text
task order: horizon, igt, bart
condition order: configured order
metric order: configured primary order, then supplemental alphabetical order
seed order: numeric ascending
```

- [ ] **Step 5: Run tests and verify failure**

Run:

```powershell
uv run python -m unittest tests.test_prompt_sensitivity
```

Expected: PSI, completeness, and output tests fail.

- [ ] **Step 6: Implement CSV loading and validation**

Define:

```python
def load_run_metrics(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def validate_run_table(
    rows: list[dict[str, Any]],
    *,
    config: dict[str, Any],
    expected_runs_per_cell: int,
    allow_incomplete: bool,
) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for task, task_config in config["tasks"].items():
        condition_seeds: dict[str, set[int]] = {}
        for condition in task_config["prompt_conditions"]:
            cell_rows = [
                row
                for row in rows
                if row["task"] == task
                and row["prompt_condition"] == condition
            ]
            seeds = {int(row["seed"]) for row in cell_rows}
            condition_seeds[condition] = seeds
            if len(cell_rows) != expected_runs_per_cell:
                code = (
                    "missing_run"
                    if len(cell_rows) < expected_runs_per_cell
                    else "unexpected_run"
                )
                issues.append(
                    {
                        "code": code,
                        "severity": "error",
                        "message": (
                            f"{task}/{condition} has {len(cell_rows)} runs; "
                            f"expected {expected_runs_per_cell}."
                        ),
                        "details": {
                            "task": task,
                            "condition": condition,
                            "observed": len(cell_rows),
                            "expected": expected_runs_per_cell,
                        },
                    }
                )
        seed_sets = list(condition_seeds.values())
        if seed_sets and any(seed_set != seed_sets[0] for seed_set in seed_sets[1:]):
            issues.append(
                {
                    "code": "unpaired_seed",
                    "severity": "error",
                    "message": f"{task} prompt conditions do not share seed sets.",
                    "details": {
                        condition: sorted(seeds)
                        for condition, seeds in condition_seeds.items()
                    },
                }
            )
    if issues and not allow_incomplete:
        raise PromptSensitivityValidationError(issues)
    return issues
```

Recheck counts and paired seed sets even if aggregation already validated them.

- [ ] **Step 7: Implement summary and effect table construction**

Define:

```python
def build_metric_summaries(
    rows: list[dict[str, Any]],
    *,
    metric_columns: list[str],
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for task, task_config in config["tasks"].items():
        for condition in task_config["prompt_conditions"]:
            cell_rows = [
                row
                for row in rows
                if row["task"] == task
                and row["prompt_condition"] == condition
            ]
            for metric in metric_columns:
                values = [
                    value
                    for row in cell_rows
                    if (value := parse_optional_float(row.get(metric))) is not None
                ]
                if values:
                    summaries.append(
                        {
                            "task": task,
                            "prompt_condition": condition,
                            "metric": metric,
                            **summarise_values(values),
                        }
                    )
    return summaries


def build_prompt_effects(
    rows: list[dict[str, Any]],
    *,
    config: dict[str, Any],
    allow_incomplete: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    analysis = config["analysis"]
    baseline = analysis["baseline_condition"]
    policy = analysis["prompt_sensitivity"]
    effects: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    for task, metrics in policy["primary_metrics"].items():
        task_conditions = config["tasks"][task]["prompt_conditions"]
        for condition in task_conditions:
            if condition == baseline:
                continue
            for metric in metrics:
                baseline_values = [
                    value
                    for row in rows
                    if row["task"] == task
                    and row["prompt_condition"] == baseline
                    and (value := parse_optional_float(row.get(metric))) is not None
                ]
                condition_values = [
                    value
                    for row in rows
                    if row["task"] == task
                    and row["prompt_condition"] == condition
                    and (value := parse_optional_float(row.get(metric))) is not None
                ]
                try:
                    effect = compute_standardised_effect(
                        baseline_values=baseline_values,
                        condition_values=condition_values,
                        metric=metric,
                        policy=policy,
                        allow_incomplete=allow_incomplete,
                    )
                except PromptSensitivityValidationError as exc:
                    issues.extend(exc.issues)
                    if not allow_incomplete:
                        raise
                    continue
                effects.append(
                    {
                        "task": task,
                        "prompt_condition": condition,
                        "metric": metric,
                        **effect,
                    }
                )
    return effects, issues
```

Create effects only for non-baseline conditions.

- [ ] **Step 8: Implement PSI rows**

Define:

```python
def compute_psi_row(
    *,
    task: str,
    condition: str,
    expected_metrics: list[str],
    effect_rows: list[dict[str, Any]],
    minimum_partial_metrics: int,
    allow_incomplete: bool,
) -> dict[str, Any]:
    by_metric = {row["metric"]: row for row in effect_rows}
    valid = [
        by_metric[metric]
        for metric in expected_metrics
        if metric in by_metric
        and by_metric[metric].get("absolute_standardised_effect") is not None
    ]
    missing = [metric for metric in expected_metrics if metric not in by_metric]
    if missing and not allow_incomplete:
        raise PromptSensitivityValidationError(
            [
                {
                    "code": "missing_metric",
                    "severity": "error",
                    "message": f"{task}/{condition} is missing PSI metrics.",
                    "details": {"metrics": missing},
                }
            ]
        )
    psi = None
    if len(valid) >= minimum_partial_metrics:
        psi = statistics.mean(
            float(row["absolute_standardised_effect"]) for row in valid
        )
    return {
        "task": task,
        "prompt_condition": condition,
        "psi": psi,
        "expected_metric_count": len(expected_metrics),
        "valid_metric_count": len(valid),
        "excluded_metrics": "|".join(missing),
        "status": (
            "complete"
            if len(valid) == len(expected_metrics)
            else "partial" if psi is not None else "insufficient"
        ),
    }


def build_psi_rows(
    effect_rows: list[dict[str, Any]],
    *,
    config: dict[str, Any],
    allow_incomplete: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    policy = config["analysis"]["prompt_sensitivity"]
    baseline = config["analysis"]["baseline_condition"]
    rows: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    for task, expected_metrics in policy["primary_metrics"].items():
        for condition in config["tasks"][task]["prompt_conditions"]:
            if condition == baseline:
                continue
            condition_effects = [
                row
                for row in effect_rows
                if row["task"] == task
                and row["prompt_condition"] == condition
            ]
            psi_row = compute_psi_row(
                task=task,
                condition=condition,
                expected_metrics=expected_metrics,
                effect_rows=condition_effects,
                minimum_partial_metrics=policy["minimum_partial_metrics"],
                allow_incomplete=allow_incomplete,
            )
            rows.append(psi_row)
            if psi_row["status"] != "complete":
                issues.append(
                    {
                        "code": "partial_psi",
                        "severity": "warning",
                        "message": f"{task}/{condition} PSI is not complete.",
                        "details": {
                            "status": psi_row["status"],
                            "excluded_metrics": psi_row["excluded_metrics"],
                        },
                    }
                )
    return rows, issues
```

Do not emit a numeric PSI when fewer than
`minimum_partial_metrics` effects are valid.

- [ ] **Step 9: Implement output writing and CLI**

Write:

```text
metric_summary.csv
prompt_effects.csv
prompt_sensitivity.csv
analysis_summary.json
```

CLI arguments:

```text
run_metrics_csv
--output-dir
--expected-runs-per-cell
--allow-incomplete
--config
```

`analysis_summary.json` records:

- baseline condition;
- expected runs per cell;
- strict/incomplete mode;
- analysis completeness;
- source run-table path;
- counts of summary, effect, and PSI rows;
- issue list;
- explicit statement that PSI is project-defined and descriptive.

- [ ] **Step 10: Run PSI tests**

Run:

```powershell
uv run python -m unittest tests.test_prompt_sensitivity
```

Expected: all PSI tests pass.

- [ ] **Step 11: Commit**

```powershell
git add src/compute_prompt_sensitivity.py tests/test_prompt_sensitivity.py
git commit -m "feat: calculate prompt sensitivity index"
```

## Task 10: Document the Runnable Mini-Pilot Analysis Workflow

**Files:**
- Modify: `README.md`
- Modify: `docs/data_schema.md`
- Modify: `docs/next_steps_plan.md`
- Modify: `docs/research_log.md`

- [ ] **Step 1: Update README in the same behavior change**

Document that:

- output filenames now include the canonical task seed;
- running a task subset keeps the same task-specific offset;
- mini-pilot base seeds are repeated across all four conditions;
- the expected scale is 36 runs;
- strict analysis is the default;
- `--allow-incomplete` and `--duplicate-policy latest` must be explicit;
- PSI uses three fixed metrics per task and is descriptive.

Add commands:

```powershell
python -m src.aggregate_experiment_results outputs/mini_pilot `
  --expected-runs-per-cell 3 `
  --output-dir outputs/processed/mini_pilot

python -m src.compute_prompt_sensitivity `
  outputs/processed/mini_pilot/llm_run_metrics.csv `
  --expected-runs-per-cell 3 `
  --output-dir outputs/processed/mini_pilot
```

Add incomplete recovery example:

```powershell
python -m src.aggregate_experiment_results outputs/mini_pilot `
  --expected-runs-per-cell 3 `
  --duplicate-policy latest `
  --allow-incomplete `
  --output-dir outputs/processed/mini_pilot
```

- [ ] **Step 2: Update the data schema**

Document columns and status fields for:

- `llm_run_metrics.csv`;
- `aggregation_quality_report.json`;
- `metric_summary.csv`;
- `prompt_effects.csv`;
- `prompt_sensitivity.csv`;
- `analysis_summary.json`.

Explicitly define:

```text
run_id = task:prompt_condition:seed
learning_curve_change = IGT block 5 net score - block 1 net score
random_exploration_effect = decision_noise_h6 - decision_noise_h1
```

- [ ] **Step 3: Update project status documents**

In `docs/next_steps_plan.md`, mark multi-run aggregation and PSI implementation
complete while leaving the 36 API-run mini pilot pending.

In `docs/research_log.md`, record:

- canonical seed-offset correction;
- new output names;
- quality-control rules;
- variance fallback;
- primary PSI metric set;
- exact verification commands and results from Task 11.

- [ ] **Step 4: Check documentation references**

Run:

```powershell
rg -n "aggregate_experiment_results|compute_prompt_sensitivity|expected-runs-per-cell|allow-incomplete|Prompt Sensitivity Index" README.md docs
```

Expected: README and method documentation expose the current workflow.

- [ ] **Step 5: Commit**

```powershell
git add README.md docs/data_schema.md docs/next_steps_plan.md docs/research_log.md
git commit -m "docs: add multi-run PSI analysis workflow"
```

## Task 11: Verify the Pipeline End to End

**Files:**
- Modify if needed: `tests/test_aggregate_experiment_results.py`
- Modify if needed: `tests/test_prompt_sensitivity.py`
- Modify: `docs/research_log.md`
- Modify: `README.md` only if verification changes the documented test count

- [ ] **Step 1: Run focused tests**

```powershell
uv run python -m unittest `
  tests.test_llm_pilot `
  tests.test_horizon_random_exploration `
  tests.test_aggregate_experiment_results `
  tests.test_prompt_sensitivity
```

Expected: all focused tests pass.

- [ ] **Step 2: Run the complete suite**

```powershell
uv run python -m unittest discover -s tests
```

Expected: zero failures and zero errors. Record the exact test count.

- [ ] **Step 3: Run an end-to-end synthetic 36-run fixture**

Use a temporary directory generated by a test helper or a dedicated
`TemporaryDirectory` invocation. It must contain:

```text
3 tasks x 4 conditions x 3 paired base-seed blocks
```

Run:

```powershell
uv run python -m src.aggregate_experiment_results <fixture-dir> `
  --expected-runs-per-cell 3 `
  --output-dir <fixture-output>

uv run python -m src.compute_prompt_sensitivity `
  <fixture-output>\llm_run_metrics.csv `
  --expected-runs-per-cell 3 `
  --output-dir <fixture-output>
```

Expected files:

```text
llm_run_metrics.csv
aggregation_quality_report.json
metric_summary.csv
prompt_effects.csv
prompt_sensitivity.csv
analysis_summary.json
```

Expected checks:

- 36 run rows;
- no duplicate or missing-run issues;
- 27 prompt-effect rows:
  `3 tasks x 3 manipulated conditions x 3 primary metrics`;
- 9 PSI rows:
  `3 tasks x 3 manipulated conditions`;
- all PSI rows are complete;
- Horizon run rows contain finite `random_exploration_effect`.

- [ ] **Step 4: Verify strict failure and incomplete recovery**

Delete one synthetic run and rerun:

```powershell
uv run python -m src.aggregate_experiment_results <incomplete-fixture> `
  --expected-runs-per-cell 3 `
  --output-dir <strict-output>
```

Expected: nonzero exit with a written quality report containing `missing_run`.

Then run:

```powershell
uv run python -m src.aggregate_experiment_results <incomplete-fixture> `
  --expected-runs-per-cell 3 `
  --allow-incomplete `
  --output-dir <partial-output>
```

Expected: run table and quality report are written with
`analysis_complete=false`.

- [ ] **Step 5: Validate configuration and formatting**

```powershell
uv run python -c "import json; json.load(open('configs/experiment_config_stage01.json', encoding='utf-8')); print('config json ok')"
git diff --check
```

Expected:

```text
config json ok
```

and no `git diff --check` output.

- [ ] **Step 6: Record fresh evidence**

Update `docs/research_log.md` and README's current test count with only the
results observed in Steps 1-5.

- [ ] **Step 7: Rerun final verification after documentation edits**

```powershell
uv run python -m unittest discover -s tests
git diff --check
```

Expected: all tests pass and no whitespace errors.

- [ ] **Step 8: Commit**

```powershell
git add README.md docs/research_log.md
git add src tests configs docs/data_schema.md docs/next_steps_plan.md
git commit -m "feat: complete multi-run aggregation and PSI pipeline"
```
