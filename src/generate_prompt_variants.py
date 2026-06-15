from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

from src.llm_client import OpenAIResponsesClient, get_env_value


DEFAULT_MODEL = "gpt-4o-2024-11-20"
DEFAULT_MAX_OUTPUT_TOKENS = 6000
DEFAULT_TEMPERATURE = 0.0
DEFAULT_TOP_P = 1.0
META_PROMPT_PATH = Path("prompts/generation/meta_prompt_v2.md")
ALL_TASKS = ("horizon", "igt", "bart")

TASK_GENERATION_SPECS = {
    "horizon": {
        "identifier": "two_option_reward_task",
        "baseline_path": Path("prompts/bandit/baseline.md"),
        "condition_name": "uncertainty_emphasis",
        "permitted_emphasis": (
            "the fact that A and B have initially unknown reward patterns and "
            "that the observed rewards provide incomplete information about them"
        ),
        "canonical_specification": (
            "The frozen baseline is the complete participant-facing specification. "
            "It describes 40 games, four forced choices followed by one or six "
            "free choices, reward feedback, and the exact response format. Do not "
            "introduce internal condition labels, true reward means or distribution "
            "parameters, exploration terminology, behavioural metrics, or a "
            "recommended choice strategy."
        ),
    },
    "igt": {
        "identifier": "four_deck_reward_task",
        "baseline_path": Path("prompts/igt/baseline.md"),
        "condition_name": "reward_loss_emphasis",
        "permitted_emphasis": (
            "the rewards, losses, net outcomes, and cumulative consequences "
            "already described in the frozen baseline"
        ),
        "canonical_specification": (
            "The frozen baseline is the complete participant-facing specification. "
            "It describes 100 choices, a starting score of 2000, four decks with "
            "initially unknown reward and loss patterns, outcome feedback, and the "
            "exact response format. Do not identify advantageous decks, reveal the "
            "payoff schedule, introduce behavioural metrics, or recommend a deck."
        ),
    },
    "bart": {
        "identifier": "balloon_earnings_task",
        "baseline_path": Path("prompts/bart/baseline.md"),
        "condition_name": "risk_emphasis",
        "permitted_emphasis": (
            "the existing trade-off that pumping can increase temporary earnings "
            "or cause an explosion that loses those temporary earnings"
        ),
        "canonical_specification": (
            "The frozen baseline is the complete participant-facing specification. "
            "It describes 40 balloons, a 0.05 increase after each successful pump, "
            "explosion loss, cashing out, feedback, and the exact response format. "
            "Do not reveal explosion probabilities or thresholds, introduce risk "
            "metrics, or recommend a pumping or cash-out strategy."
        ),
    },
}


class PromptGeneratorClient(Protocol):
    def create_response(
        self,
        *,
        prompt: str,
        model: str,
        max_output_tokens: int,
        temperature: float | None = None,
        top_p: float | None = None,
    ) -> dict[str, Any]:
        ...


def build_generation_prompt(
    task: str,
    *,
    meta_prompt_path: Path = META_PROMPT_PATH,
) -> str:
    task_key = task.lower()
    if task_key not in TASK_GENERATION_SPECS:
        raise ValueError(f"Unknown task {task!r}. Valid tasks are {ALL_TASKS}.")

    spec = TASK_GENERATION_SPECS[task_key]
    meta_prompt = meta_prompt_path.read_text(encoding="utf-8")
    baseline = spec["baseline_path"].read_text(encoding="utf-8")
    replacements = {
        "[TASK_IDENTIFIER]": spec["identifier"],
        "[PASTE_CANONICAL_TASK_SPECIFICATION]": spec["canonical_specification"],
        "[PASTE_BASELINE_PROMPT_VERBATIM]": baseline,
        "[CONDITION_NAME]": spec["condition_name"],
        "[DEFINE_INFORMATION_TO_MAKE_MORE_SALIENT]": spec["permitted_emphasis"],
    }
    for placeholder, value in replacements.items():
        meta_prompt = meta_prompt.replace(placeholder, value)
    return meta_prompt


def generate_prompt_variants(
    *,
    client: PromptGeneratorClient,
    model: str,
    output_dir: Path,
    task_names: tuple[str, ...] = ALL_TASKS,
    max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
    temperature: float = DEFAULT_TEMPERATURE,
    top_p: float = DEFAULT_TOP_P,
    generated_at: str | None = None,
) -> dict[str, dict[str, Any]]:
    timestamp = generated_at or datetime.now(timezone.utc).isoformat()
    output_dir.mkdir(parents=True, exist_ok=True)
    summaries: dict[str, dict[str, Any]] = {}

    for task in task_names:
        task_key = task.lower()
        prompt = build_generation_prompt(task_key)
        spec = TASK_GENERATION_SPECS[task_key]
        baseline_path = spec["baseline_path"]
        baseline_hash = _sha256(baseline_path)
        task_dir = output_dir / task_key
        task_dir.mkdir(parents=True, exist_ok=True)
        (task_dir / "request.md").write_text(prompt, encoding="utf-8")

        response = client.create_response(
            prompt=prompt,
            model=model,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            top_p=top_p,
        )
        raw_response = response["raw_response"]
        output_text = response["output_text"]
        (task_dir / "raw_response.json").write_text(
            json.dumps(raw_response, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        (task_dir / "raw_output.md").write_text(output_text, encoding="utf-8")

        record = {
            "task": task_key,
            "generated_at": timestamp,
            "provider": "OpenAI Responses API via university-provided access",
            "requested_model": model,
            "response_model": raw_response.get("model", "not exposed by provider"),
            "response_id": raw_response.get("id", "not exposed by provider"),
            "reasoning_effort": "not sent",
            "text_verbosity": "not sent",
            "temperature": temperature,
            "top_p": top_p,
            "max_output_tokens": max_output_tokens,
            "seed": "not supported",
            "meta_prompt_path": str(META_PROMPT_PATH),
            "baseline_path": str(baseline_path),
            "baseline_sha256": baseline_hash,
            "task_specific_condition": spec["condition_name"],
            "candidate_sets_requested": 1,
            "raw_request_path": str(task_dir / "request.md"),
            "raw_response_path": str(task_dir / "raw_response.json"),
            "raw_output_path": str(task_dir / "raw_output.md"),
            "installed_as_final_prompts": False,
            "manual_review_status": "pending",
        }
        (task_dir / "generation_record.json").write_text(
            json.dumps(record, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        summaries[task_key] = {
            "task": task_key,
            "requested_model": model,
            "response_model": record["response_model"],
            "response_id": record["response_id"],
            "output_dir": str(task_dir),
            "manual_review_status": "pending",
        }

    return summaries


def parse_task_names(value: str) -> tuple[str, ...]:
    if value.strip().lower() == "all":
        return ALL_TASKS
    tasks = tuple(part.strip().lower() for part in value.split(",") if part.strip())
    invalid = [task for task in tasks if task not in ALL_TASKS]
    if invalid:
        raise ValueError(f"Unknown task names: {invalid}. Valid tasks are {ALL_TASKS}.")
    if not tasks:
        raise ValueError("At least one task name is required.")
    return tasks


def default_output_dir(model: str) -> Path:
    date = datetime.now(timezone.utc).date().isoformat()
    safe_model = re.sub(r"[^A-Za-z0-9._-]+", "_", model)
    return Path("prompts/generation/records") / f"{date}_{safe_model}"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate nine prompt variants for manual review without installing them."
    )
    parser.add_argument(
        "--model",
        default=get_env_value("PROMPT_GENERATOR_MODEL") or DEFAULT_MODEL,
    )
    parser.add_argument("--tasks", default="all", help="Comma-separated task names or 'all'.")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--max-output-tokens", type=int, default=DEFAULT_MAX_OUTPUT_TOKENS)
    parser.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE)
    parser.add_argument("--top-p", type=float, default=DEFAULT_TOP_P)
    args = parser.parse_args()

    api_key = get_env_value("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is missing. Set it in PowerShell or a local .env file.")

    output_dir = args.output_dir or default_output_dir(args.model)
    client = OpenAIResponsesClient(api_key=api_key)
    summaries = generate_prompt_variants(
        client=client,
        model=args.model,
        output_dir=output_dir,
        task_names=parse_task_names(args.tasks),
        max_output_tokens=args.max_output_tokens,
        temperature=args.temperature,
        top_p=args.top_p,
    )
    print(json.dumps(summaries, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
