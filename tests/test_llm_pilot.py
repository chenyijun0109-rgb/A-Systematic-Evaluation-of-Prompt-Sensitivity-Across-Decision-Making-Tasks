import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.llm_client import OpenAIResponsesClient, load_dotenv
from src.prompt_loader import load_config
from src.run_llm_pilot import parse_task_names, run_baseline_llm_pilot, run_llm_pilot


class FakePilotClient:
    def create_response(self, *, prompt: str, model: str, max_output_tokens: int) -> dict:
        del model, max_output_tokens
        if "ACTION: CASH_OUT" in prompt:
            text = "ACTION: CASH_OUT"
        elif "Forced choice: choose A." in prompt:
            text = "CHOICE: A"
        elif "Forced choice: choose B." in prompt:
            text = "CHOICE: B"
        else:
            text = "CHOICE: A"
        return {
            "raw_response": {"output_text": text},
            "output_text": text,
        }


class InvalidPilotClient:
    def create_response(self, *, prompt: str, model: str, max_output_tokens: int) -> dict:
        del prompt, model, max_output_tokens
        return {
            "raw_response": {"output_text": "A"},
            "output_text": "A",
        }


class LLMPilotTests(unittest.TestCase):
    def test_load_dotenv_reads_simple_key_value_pairs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            env_path = Path(tmpdir) / ".env"
            env_path.write_text(
                "OPENAI_API_KEY=test-key\nOPENAI_MODEL=gpt-test\n",
                encoding="utf-8",
            )

            values = load_dotenv(env_path)

            self.assertEqual(values["OPENAI_API_KEY"], "test-key")
            self.assertEqual(values["OPENAI_MODEL"], "gpt-test")

    def test_openai_client_requires_api_key(self):
        with self.assertRaises(ValueError):
            OpenAIResponsesClient(api_key="")

    def test_openai_client_retries_transient_timeout(self):
        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, traceback):
                return False

            def read(self):
                return json.dumps({"output_text": "CHOICE: A"}).encode("utf-8")

        calls = {"count": 0}

        def fake_urlopen(request, timeout):
            del request, timeout
            calls["count"] += 1
            if calls["count"] == 1:
                raise TimeoutError("temporary read timeout")
            return FakeResponse()

        client = OpenAIResponsesClient(api_key="test-key", max_retries=1, retry_sleep_seconds=0)

        with patch("src.llm_client.request.urlopen", side_effect=fake_urlopen):
            result = client.create_response(
                prompt="Choose.",
                model="gpt-test",
                max_output_tokens=16,
            )

        self.assertEqual(result["output_text"], "CHOICE: A")
        self.assertEqual(calls["count"], 2)

    def test_openai_client_sends_gpt5_reasoning_and_verbosity_parameters(self):
        captured = {}

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, traceback):
                return False

            def read(self):
                return json.dumps({"output_text": "generated"}).encode("utf-8")

        def fake_urlopen(http_request, timeout):
            del timeout
            captured.update(json.loads(http_request.data.decode("utf-8")))
            return FakeResponse()

        client = OpenAIResponsesClient(api_key="test-key")
        with patch("src.llm_client.request.urlopen", side_effect=fake_urlopen):
            client.create_response(
                prompt="Generate.",
                model="gpt-5.5",
                max_output_tokens=6000,
                reasoning_effort="low",
                text_verbosity="low",
            )

        self.assertEqual(captured["model"], "gpt-5.5")
        self.assertEqual(captured["reasoning"], {"effort": "low"})
        self.assertEqual(captured["text"], {"verbosity": "low"})
        self.assertNotIn("temperature", captured)
        self.assertNotIn("top_p", captured)

    def test_openai_client_sends_sampling_parameters(self):
        captured = {}

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, traceback):
                return False

            def read(self):
                return json.dumps({"output_text": "generated"}).encode("utf-8")

        def fake_urlopen(http_request, timeout):
            del timeout
            captured.update(json.loads(http_request.data.decode("utf-8")))
            return FakeResponse()

        client = OpenAIResponsesClient(api_key="test-key")
        with patch("src.llm_client.request.urlopen", side_effect=fake_urlopen):
            client.create_response(
                prompt="Generate.",
                model="gpt-4o-2024-11-20",
                max_output_tokens=6000,
                temperature=0.0,
                top_p=1.0,
            )

        self.assertEqual(captured["model"], "gpt-4o-2024-11-20")
        self.assertEqual(captured["temperature"], 0.0)
        self.assertEqual(captured["top_p"], 1.0)
        self.assertNotIn("reasoning", captured)
        self.assertNotIn("text", captured)

    def test_parse_task_names(self):
        self.assertEqual(parse_task_names("igt,bart"), ("igt", "bart"))
        self.assertEqual(parse_task_names("all"), ("horizon", "igt", "bart"))

    def test_run_baseline_llm_pilot_writes_outputs_with_fake_client(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            result = run_baseline_llm_pilot(
                client=FakePilotClient(),
                model="gpt-test",
                seed=123,
                output_dir=output_dir,
                task_names=("igt", "bart"),
            )

            self.assertEqual(set(result), {"igt", "bart"})
            for task in result:
                with self.subTest(task=task):
                    self.assertTrue(result[task]["done"])
                    self.assertGreater(result[task]["n_trials"], 0)
                    self.assertEqual(result[task]["invalid_response_count"], 0)

                    expected_seed = 124 if task == "igt" else 125
                    path = output_dir / f"{task}_baseline_seed-{expected_seed}.json"
                    self.assertTrue(path.exists())
                    data = json.loads(path.read_text(encoding="utf-8"))
                    self.assertEqual(data["task"], task)
                    self.assertEqual(data["seed"], expected_seed)
                    self.assertEqual(data["config_name"], "experiment_config_stage01")
                    self.assertEqual(
                        data["config_version"],
                        str(
                            load_config(
                                Path("configs/experiment_config_stage01.json")
                            )["version"]
                        ),
                    )
                    self.assertEqual(
                        data["prompt_path"],
                        f"prompts/{task}/baseline.md",
                    )
                    self.assertRegex(data["prompt_sha256"], r"^[0-9a-f]{64}$")
                    self.assertIn("raw_llm_outputs", data)
                    self.assertIn("trial_records", data)
                    self.assertIn("run_metrics", data)

    def test_run_baseline_llm_pilot_writes_failed_debug_output(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)

            with self.assertRaises(RuntimeError):
                run_baseline_llm_pilot(
                    client=InvalidPilotClient(),
                    model="gpt-test",
                    seed=123,
                    output_dir=output_dir,
                    task_names=("igt",),
                )

            path = output_dir / "igt_baseline_seed-124_failed.json"
            self.assertTrue(path.exists())
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["task"], "igt")
            self.assertFalse(data["done"])
            self.assertEqual(data["failure_reason"], "missing_required_prefix")
            self.assertGreater(len(data["raw_llm_outputs"]), 0)
            self.assertGreater(len(data["invalid_responses"]), 0)

    def test_run_llm_pilot_accepts_reviewed_generated_condition(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)

            result = run_llm_pilot(
                client=FakePilotClient(),
                model="gpt-test",
                seed=123,
                output_dir=output_dir,
                prompt_condition="detailed",
                task_names=("igt",),
            )

            self.assertTrue(result["igt"]["done"])
            self.assertTrue((output_dir / "igt_detailed_seed-124.json").exists())

    def test_single_task_uses_canonical_task_seed_offset(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)

            result = run_llm_pilot(
                client=FakePilotClient(),
                model="gpt-test",
                seed=100,
                output_dir=output_dir,
                prompt_condition="risk_emphasis",
                task_names=("bart",),
            )

            self.assertEqual(result["bart"]["seed"], 102)
            self.assertTrue(
                (output_dir / "bart_risk_emphasis_seed-102.json").exists()
            )


if __name__ == "__main__":
    unittest.main()
