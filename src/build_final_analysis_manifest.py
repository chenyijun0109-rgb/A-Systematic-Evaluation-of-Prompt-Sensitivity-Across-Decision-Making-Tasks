from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def build_manifest(root: Path) -> dict[str, Any]:
    failures: list[str] = []
    expected_effects = {
        "gpt-4.1-en": (24, 9),
        "gpt-5.4-en": (24, 9),
        "gpt-5.4-mini-en": (24, 9),
        "gpt-4.1-multilingual": (72, 27),
    }
    files: dict[str, dict[str, Any]] = {}

    def record(path: Path) -> None:
        relative = path.relative_to(root).as_posix()
        entry: dict[str, Any] = {"sha256": sha256(path), "bytes": path.stat().st_size}
        if path.suffix == ".csv":
            entry["rows"] = len(csv_rows(path))
        files[relative] = entry

    for directory, (effect_count, psi_count) in expected_effects.items():
        batch = root / directory
        quality_path = batch / "aggregation_quality_report.json"
        effects_path = batch / "prompt_effects.csv"
        psi_path = batch / "prompt_sensitivity.csv"
        for path in (quality_path, effects_path, psi_path):
            require(path.exists(), f"Missing {path}", failures)
        if not all(path.exists() for path in (quality_path, effects_path, psi_path)):
            continue
        quality = json.loads(quality_path.read_text(encoding="utf-8"))
        effects = csv_rows(effects_path)
        psi = csv_rows(psi_path)
        require(quality["analysis_complete"], f"Incomplete aggregation: {directory}", failures)
        require(len(effects) == effect_count, f"Unexpected effect rows: {directory}", failures)
        require(len(psi) == psi_count, f"Unexpected PSI rows: {directory}", failures)
        require(all(row["raw_interval_status"] == "report" for row in effects), f"Non-report raw interval: {directory}", failures)
        require(all(row["standardised_interval_status"] == "report" for row in effects), f"Non-report standardised interval: {directory}", failures)
        require(all(row["psi_interval_status"] == "report" for row in psi), f"Non-report PSI interval: {directory}", failures)
        for path in (quality_path, effects_path, psi_path, batch / "llm_run_metrics.csv"):
            record(path)

    for directory in ("gpt-4.1-minus-gpt-5.4", "gpt-5.4-mini-minus-gpt-5.4"):
        path = root / directory / "model_prompt_interaction_contrasts.csv"
        rows = csv_rows(path)
        require(len(rows) == 24, f"Unexpected RQ2 rows: {directory}", failures)
        require(all(row["interval_status"] == "report" for row in rows), f"Non-report RQ2 interval: {directory}", failures)
        record(path)

    multilingual = root / "gpt-4.1-multilingual"
    for name, count in (("language_centered_baselines.csv", 24), ("language_centered_prompt_effects.csv", 72)):
        path = multilingual / name
        rows = csv_rows(path)
        require(len(rows) == count, f"Unexpected RQ3 rows: {name}", failures)
        require(all(row["raw_interval_status"] == "report" for row in rows), f"Non-report RQ3 raw interval: {name}", failures)
        require(all(row["standardised_interval_status"] == "report" for row in rows), f"Non-report RQ3 standardised interval: {name}", failures)
        record(path)

    human_dir = root / "human_reference_results"
    for name, count in (("model_human_comparison.csv", 160), ("model_human_distance_changes.csv", 120)):
        path = human_dir / name
        require(len(csv_rows(path)) == count, f"Unexpected RQ4 rows: {name}", failures)
        record(path)
    for name, count in (("human_reference_bootstrap.csv", 7),):
        path = human_dir / name
        require(len(csv_rows(path)) == count, f"Unexpected human bootstrap rows: {name}", failures)
        record(path)
    bootstrap_summary = human_dir / "human_reference_bootstrap_summary.json"
    require(bootstrap_summary.exists(), "Missing human reference bootstrap summary", failures)
    record(bootstrap_summary)

    diagnostics_dir = root / "random_exploration_diagnostics"
    diagnostic_files = sorted(diagnostics_dir.glob("*.json"))
    require(len(diagnostic_files) == 6, "Expected six Random-exploration diagnostic files", failures)
    for path in diagnostic_files:
        data = json.loads(path.read_text(encoding="utf-8"))
        conditions = [item for item in data["conditions"].values() if item["status"] == "ok"]
        sensitivity = [
            fit
            for item in data["diagnostics"].values()
            for fit in item["shrinkage_sensitivity"]
        ]
        require(all(item["converged"] for item in conditions), f"Failed base fit: {path.name}", failures)
        require(all(item["converged"] for item in sensitivity), f"Failed sensitivity fit: {path.name}", failures)
        record(path)

    for path in (
        Path("configs/experiment_config_stage01.json"),
        Path("configs/formal_experiment_freeze.json"),
        Path("configs/multilingual_experiment_freeze_v01.json"),
    ):
        files[path.as_posix()] = {"sha256": sha256(path), "bytes": path.stat().st_size}

    return {
        "manifest_version": "final_analysis_v03",
        "analysis_ready": not failures,
        "failures": failures,
        "validated_claim_scope": ["RQ1", "RQ2", "RQ3", "descriptive_RQ4"],
        "files": dict(sorted(files.items())),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate and hash the final analysis package.")
    parser.add_argument("--root", type=Path, default=Path("outputs/processed/final_analysis_v03"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    manifest = build_manifest(args.root)
    output = args.output or args.root / "analysis_manifest.json"
    output.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"analysis_ready": manifest["analysis_ready"], "failures": manifest["failures"], "output": str(output)}, indent=2))
    if not manifest["analysis_ready"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
