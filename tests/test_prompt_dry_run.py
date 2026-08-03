import json
import hashlib
import tempfile
import unittest
from pathlib import Path

from src.prompt_loader import (
    extract_response_format,
    load_config,
    load_prompt_template,
    render_prompt,
)
from src.run_prompt_dry_run import (
    run_baseline_prompt_dry_run,
    run_prompt_matrix_dry_run,
    run_multilingual_prompt_matrix_dry_run,
)


class PromptDryRunTests(unittest.TestCase):
    ROLE_SENTENCE = "Take the role of a human participant completing this task.\n\n"
    MULTILINGUAL_ROLE_SENTENCES = {
        "zh-CN": "请以一名正在完成此任务的人类参与者的身份作答。\n\n",
        "es": "Asume el papel de un participante humano que está completando esta tarea.\n\n",
    }

    def test_load_prompt_template_reads_baseline_prompt_from_config(self):
        template = load_prompt_template("igt", "baseline")

        self.assertIn("{observation}", template)
        self.assertIn("CHOICE: A", template)
        self.assertIn("CHOICE: D", template)

    def test_experimental_prompts_do_not_include_classic_task_names(self):
        task_names = {
            "horizon": "Horizon Task",
            "igt": "Iowa Gambling Task",
            "bart": "Balloon Analogue Risk Task",
        }
        config = load_config()

        for task, task_name in task_names.items():
            for condition in config["tasks"][task]["prompt_conditions"]:
                with self.subTest(task=task, condition=condition):
                    template = load_prompt_template(task, condition)
                    self.assertNotIn(task_name, template)

    def test_canonical_baselines_have_shared_objective_and_one_placeholder(self):
        objective = "finish the full task with as much total reward as possible"

        for task in ("horizon", "igt", "bart"):
            with self.subTest(task=task):
                template = load_prompt_template(task, "baseline")
                self.assertEqual(template.count("{observation}"), 1)
                self.assertIn(objective, template)

    def test_canonical_baselines_include_approved_participant_facing_parameters(self):
        required_text = {
            "horizon": (
                "40 separate games",
                "four forced choices",
                "one or six free choices",
            ),
            "igt": (
                "100 choices",
                "starts at 2000",
                "different pattern of rewards and losses",
            ),
            "bart": (
                "40 balloons",
                "successful pump adds 0.05",
                "temporary earnings for that balloon are lost",
            ),
        }

        for task, required_phrases in required_text.items():
            template = load_prompt_template(task, "baseline")
            for phrase in required_phrases:
                with self.subTest(task=task, phrase=phrase):
                    self.assertIn(phrase, template)

    def test_experimental_prompts_do_not_reveal_hidden_task_information(self):
        forbidden_text = {
            "horizon": (
                "directed exploration",
                "random exploration",
                "decision noise",
                "horizon_1",
                "horizon_6",
                "equal_information",
                "unequal_information",
            ),
            "igt": (
                "advantageous",
                "disadvantageous",
                "C and D are",
                "payoff schedule",
            ),
            "bart": (
                "explosion probability",
                "certain explosion",
                "pump 32",
                "1/(33",
                "cash-out threshold",
            ),
        }
        config = load_config()

        for task, forbidden_phrases in forbidden_text.items():
            for condition in config["tasks"][task]["prompt_conditions"]:
                template = load_prompt_template(task, condition).casefold()
                for phrase in forbidden_phrases:
                    with self.subTest(task=task, condition=condition, phrase=phrase):
                        self.assertNotIn(phrase.casefold(), template)

    def test_task_named_baseline_paths_are_preserved_for_later_comparison(self):
        config = load_config()

        self.assertEqual(
            config["tasks"]["horizon"]["prompt_paths"]["task_named_baseline"],
            "prompts/bandit/baseline_task_named.md",
        )
        self.assertEqual(
            config["tasks"]["igt"]["prompt_paths"]["task_named_baseline"],
            "prompts/igt/baseline_task_named.md",
        )
        self.assertEqual(
            config["tasks"]["bart"]["prompt_paths"]["task_named_baseline"],
            "prompts/bart/baseline_task_named.md",
        )

    def test_reviewed_prompt_conditions_are_available(self):
        expected_conditions = {
            "horizon": ("baseline", "detailed", "role_human", "uncertainty_emphasis"),
            "igt": ("baseline", "detailed", "role_human", "reward_loss_emphasis"),
            "bart": ("baseline", "detailed", "role_human", "risk_emphasis"),
        }

        for task, conditions in expected_conditions.items():
            for condition in conditions:
                with self.subTest(task=task, condition=condition):
                    template = load_prompt_template(task, condition)
                    self.assertEqual(template.count("{observation}"), 1)

    def test_multilingual_baselines_and_variants_are_configured(self):
        config = load_config()

        self.assertEqual(config["prompt_languages"], ["en", "zh-CN", "es"])
        self.assertEqual(config["default_prompt_language"], "en")
        for language in ("zh-CN", "es"):
            for task, task_config in config["tasks"].items():
                expected = set(task_config["prompt_conditions"])
                configured = set(task_config["multilingual_prompt_paths"][language])
                self.assertEqual(configured, expected)
                for condition in expected:
                    with self.subTest(language=language, task=task, condition=condition):
                        template = load_prompt_template(
                            task,
                            condition,
                            language=language,
                        )
                        self.assertEqual(template.count("{observation}"), 1)
                        for output in task_config["response_format"]["valid_outputs"]:
                            self.assertIn(output, template)

    def test_multilingual_role_prompts_only_add_authorised_sentence(self):
        for language, sentence in self.MULTILINGUAL_ROLE_SENTENCES.items():
            for task in ("horizon", "igt", "bart"):
                with self.subTest(language=language, task=task):
                    baseline = load_prompt_template(
                        task,
                        "baseline",
                        language=language,
                    )
                    role = load_prompt_template(
                        task,
                        "role_human",
                        language=language,
                    )
                    self.assertEqual(role.replace(sentence, "", 1), baseline)

    def test_unknown_prompt_language_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Prompt language"):
            load_prompt_template("igt", "baseline", language="fr")

    def test_multilingual_prompt_matrix_dry_run_checks_twelve_prompts(self):
        for language in ("zh-CN", "es"):
            with self.subTest(language=language), tempfile.TemporaryDirectory() as tmpdir:
                result = run_prompt_matrix_dry_run(
                    seed=123,
                    language=language,
                    output_path=Path(tmpdir) / "matrix.json",
                )
                self.assertEqual(len(result), 12)
                self.assertTrue(
                    all(row["prompt_language"] == language for row in result.values())
                )
                self.assertTrue(
                    all(row["all_config_valid_outputs_parse"] for row in result.values())
                )

    def test_all_languages_dry_run_checks_thirty_six_prompts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = run_multilingual_prompt_matrix_dry_run(
                seed=123,
                output_path=Path(tmpdir) / "all_languages.json",
            )

        self.assertEqual(len(result), 36)
        self.assertEqual(
            {row["prompt_language"] for row in result.values()},
            {"en", "zh-CN", "es"},
        )

    def test_multilingual_freeze_hashes_match_all_thirty_six_prompts(self):
        manifest = json.loads(
            Path("configs/multilingual_experiment_freeze_v01.json").read_text(
                encoding="utf-8"
            )
        )
        config = load_config()
        observed = 0
        for language, tasks in manifest["prompt_sha256"].items():
            for task, conditions in tasks.items():
                for condition, expected_hash in conditions.items():
                    path = (
                        Path(config["tasks"][task]["prompt_paths"][condition])
                        if language == "en"
                        else Path(
                            config["tasks"][task]["multilingual_prompt_paths"][
                                language
                            ][condition]
                        )
                    )
                    actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
                    self.assertEqual(actual_hash, expected_hash)
                    observed += 1
        self.assertEqual(observed, 36)

    def test_reviewed_variants_preserve_semantic_boundaries(self):
        for condition in ("detailed", "role_human", "uncertainty_emphasis"):
            template = load_prompt_template("horizon", condition)
            self.assertNotIn("are different", template)

        for condition in ("detailed", "role_human", "reward_loss_emphasis"):
            template = load_prompt_template("igt", condition)
            self.assertNotIn("unique", template)
            self.assertNotIn("distinct", template)
            self.assertNotIn("reward minus the loss", template)

        for condition in ("detailed", "role_human", "risk_emphasis"):
            template = load_prompt_template("bart", condition)
            normalised = " ".join(template.split())
            self.assertIn(
                "Explosion outcomes are not known to you in advance and may differ "
                "between balloons.",
                normalised,
            )
            self.assertNotIn("likelihood of a balloon exploding", template)
            self.assertNotIn("chance of a balloon exploding", template)

    def test_each_variant_isolates_its_intended_manipulation(self):
        for task in ("horizon", "igt", "bart"):
            role_prompt = load_prompt_template(task, "role_human")
            self.assertIn(self.ROLE_SENTENCE.strip(), role_prompt)
            self.assertNotIn("typical human", role_prompt.casefold())

        horizon_emphasis = " ".join(
            load_prompt_template("horizon", "uncertainty_emphasis").split()
        )
        self.assertIn("incomplete information", horizon_emphasis)
        self.assertIn(
            "pay particular attention to the reward, any loss",
            load_prompt_template("igt", "reward_loss_emphasis"),
        )
        self.assertIn(
            "Pumping therefore involves a",
            load_prompt_template("bart", "risk_emphasis"),
        )

    def test_all_experimental_prompts_preserve_exact_neutral_objective(self):
        objective = "Your aim is to finish the full task with as much total reward as possible."
        config = load_config()

        for task, task_config in config["tasks"].items():
            for condition in task_config["prompt_conditions"]:
                with self.subTest(task=task, condition=condition):
                    normalised = " ".join(load_prompt_template(task, condition).split())
                    self.assertIn(objective, normalised)

    def test_role_prompts_differ_from_baseline_only_by_human_role_sentence(self):
        for task in ("horizon", "igt", "bart"):
            with self.subTest(task=task):
                baseline = load_prompt_template(task, "baseline")
                role_prompt = load_prompt_template(task, "role_human")
                self.assertEqual(
                    role_prompt.replace(self.ROLE_SENTENCE, "", 1),
                    baseline,
                )

    def test_task_specific_prompts_change_only_the_authorised_paragraph(self):
        paragraph_pairs = {
            "horizon": (
                "Within a game, A and B may have different reward patterns that are not known\n"
                "to you in advance. After every choice, you are shown the reward from the\n"
                "selected option. You may use the observed rewards and the number of choices\n"
                "remaining in the current game when making later choices.",
                "Within a game, A and B may have different reward patterns that are not known\n"
                "to you in advance. Each observed reward provides only partial information\n"
                "about those patterns. After every choice, you are shown the reward from the\n"
                "selected option. You may use this incomplete information and the number of\n"
                "choices remaining in the current game when making later choices.",
                "uncertainty_emphasis",
            ),
            "igt": (
                "On each trial, choose one of four decks: A, B, C, or D. Each deck may have a\n"
                "different pattern of rewards and losses that is not known to you in advance.\n"
                "After every choice, you are shown the reward, any loss, the net outcome, and\n"
                "your updated cumulative score. You may use the feedback and the displayed\n"
                "history when making later choices.",
                "On each trial, choose one of four decks: A, B, C, or D. Each deck may have a\n"
                "different pattern of rewards and losses that is not known to you in advance.\n"
                "After every choice, pay particular attention to the reward, any loss, the net\n"
                "outcome, and your updated cumulative score. You may use the feedback and the\n"
                "displayed history when making later choices.",
                "reward_loss_emphasis",
            ),
            "bart": (
                "Every successful pump adds 0.05 to the temporary earnings for the current\n"
                "balloon, and you may then choose again. A pump can also cause the balloon to\n"
                "explode. If it explodes, the temporary earnings for that balloon are lost and\n"
                "the task moves to the next balloon.",
                "Every successful pump adds 0.05 to the temporary earnings for the current\n"
                "balloon, and you may then choose again. Pumping therefore involves a\n"
                "trade-off: it can increase the temporary earnings, but it can also cause the\n"
                "balloon to explode. If it explodes, the temporary earnings for that balloon\n"
                "are lost and the task moves to the next balloon.",
                "risk_emphasis",
            ),
        }

        for task, (baseline_paragraph, emphasis_paragraph, condition) in paragraph_pairs.items():
            with self.subTest(task=task, condition=condition):
                baseline = load_prompt_template(task, "baseline")
                emphasis = load_prompt_template(task, condition)
                self.assertEqual(
                    emphasis.replace(emphasis_paragraph, baseline_paragraph, 1),
                    baseline,
                )

    def test_all_configured_prompt_files_exist_and_use_same_observation_placeholder(self):
        config = load_config()

        for task, task_config in config["tasks"].items():
            valid_outputs = task_config["response_format"]["valid_outputs"]
            for condition, prompt_path in task_config["prompt_paths"].items():
                with self.subTest(task=task, condition=condition):
                    path = Path(prompt_path)
                    self.assertTrue(path.exists(), f"Missing prompt file: {prompt_path}")
                    template = path.read_text(encoding="utf-8")
                    self.assertIn("{observation}", template)
                    for output in valid_outputs:
                        self.assertIn(output, template)

    def test_render_prompt_replaces_observation_placeholder(self):
        rendered = render_prompt("State:\n{observation}", "Trial 1\nAvailable decks: A, B, C, D")

        self.assertIn("Trial 1", rendered)
        self.assertIn("Available decks: A, B, C, D", rendered)
        self.assertNotIn("{observation}", rendered)

    def test_extract_response_format_matches_parser_inputs(self):
        horizon = extract_response_format("horizon")
        igt = extract_response_format("igt")
        bart = extract_response_format("bart")

        self.assertEqual(horizon.prefix, "CHOICE")
        self.assertEqual(horizon.valid_actions, ("A", "B"))
        self.assertEqual(igt.prefix, "CHOICE")
        self.assertEqual(igt.valid_actions, ("A", "B", "C", "D"))
        self.assertEqual(bart.prefix, "ACTION")
        self.assertEqual(bart.valid_actions, ("PUMP", "CASH_OUT"))

    def test_run_baseline_prompt_dry_run_writes_validation_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "baseline_prompt_dry_run.json"
            result = run_baseline_prompt_dry_run(seed=123, output_path=output_path)

            self.assertEqual(set(result), {"horizon", "igt", "bart"})
            self.assertTrue(output_path.exists())
            data = json.loads(output_path.read_text(encoding="utf-8"))
            for task, task_result in data.items():
                with self.subTest(task=task):
                    self.assertTrue(task_result["placeholder_replaced"])
                    self.assertTrue(task_result["all_config_valid_outputs_parse"])
                    self.assertIn("observation", task_result)
                    self.assertIn("rendered_prompt", task_result)
                    self.assertNotIn("{observation}", task_result["rendered_prompt"])

    def test_run_prompt_matrix_dry_run_checks_all_twelve_experimental_prompts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "prompt_matrix_dry_run.json"
            result = run_prompt_matrix_dry_run(seed=123, output_path=output_path)

            self.assertEqual(len(result), 12)
            self.assertTrue(output_path.exists())
            for key, prompt_result in result.items():
                with self.subTest(prompt=key):
                    self.assertTrue(prompt_result["placeholder_replaced"])
                    self.assertTrue(prompt_result["all_config_valid_outputs_parse"])
                    self.assertNotIn("{observation}", prompt_result["rendered_prompt"])


if __name__ == "__main__":
    unittest.main()
