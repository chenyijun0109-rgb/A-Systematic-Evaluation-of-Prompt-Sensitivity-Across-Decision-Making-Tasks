import json
import tempfile
import unittest
from pathlib import Path

from src.generate_prompt_variants import (
    build_generation_prompt,
    generate_prompt_variants,
)


class FakeGeneratorClient:
    def __init__(self):
        self.calls = []

    def create_response(
        self,
        *,
        prompt,
        model,
        max_output_tokens,
        temperature=None,
        top_p=None,
    ):
        self.calls.append(
            {
                "prompt": prompt,
                "model": model,
                "max_output_tokens": max_output_tokens,
                "temperature": temperature,
                "top_p": top_p,
            }
        )
        return {
            "raw_response": {
                "id": f"resp_{len(self.calls)}",
                "model": "gpt-4o-2024-11-20",
                "output_text": "generated variants",
            },
            "output_text": "generated variants",
        }


class PromptVariantGenerationTests(unittest.TestCase):
    def test_build_generation_prompt_fills_all_meta_prompt_inputs(self):
        prompt = build_generation_prompt("horizon")

        self.assertNotIn("[TASK_IDENTIFIER]", prompt)
        self.assertNotIn("[PASTE_CANONICAL_TASK_SPECIFICATION]", prompt)
        self.assertNotIn("[PASTE_BASELINE_PROMPT_VERBATIM]", prompt)
        self.assertNotIn("[CONDITION_NAME]", prompt)
        self.assertNotIn("[DEFINE_INFORMATION_TO_MAKE_MORE_SALIENT]", prompt)
        self.assertIn("uncertainty_emphasis", prompt)
        self.assertIn("40 separate games", prompt)
        self.assertIn("{observation}", prompt)

    def test_generate_prompt_variants_uses_generator_model_and_saves_audit_record(self):
        client = FakeGeneratorClient()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            summaries = generate_prompt_variants(
                client=client,
                model="gpt-4o-2024-11-20",
                output_dir=output_dir,
                task_names=("igt",),
                generated_at="2026-06-14T12:00:00+00:00",
            )

            self.assertEqual(len(client.calls), 1)
            call = client.calls[0]
            self.assertEqual(call["model"], "gpt-4o-2024-11-20")
            self.assertEqual(call["max_output_tokens"], 6000)
            self.assertEqual(call["temperature"], 0.0)
            self.assertEqual(call["top_p"], 1.0)

            task_dir = output_dir / "igt"
            self.assertTrue((task_dir / "request.md").is_file())
            self.assertTrue((task_dir / "raw_response.json").is_file())
            self.assertTrue((task_dir / "raw_output.md").is_file())
            record = json.loads((task_dir / "generation_record.json").read_text(encoding="utf-8"))
            self.assertEqual(record["requested_model"], "gpt-4o-2024-11-20")
            self.assertEqual(record["response_model"], "gpt-4o-2024-11-20")
            self.assertEqual(record["reasoning_effort"], "not sent")
            self.assertEqual(record["text_verbosity"], "not sent")
            self.assertEqual(record["temperature"], 0.0)
            self.assertEqual(record["top_p"], 1.0)
            self.assertFalse(record["installed_as_final_prompts"])
            self.assertEqual(summaries["igt"]["response_id"], "resp_1")


if __name__ == "__main__":
    unittest.main()
