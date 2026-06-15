import unittest

from src.parser import parse_response


class ParseResponseTests(unittest.TestCase):
    def test_parses_valid_choice_response(self):
        result = parse_response("CHOICE: A", prefix="CHOICE", valid_actions={"A", "B"})

        self.assertTrue(result.parse_success)
        self.assertEqual(result.parsed_action, "A")
        self.assertEqual(result.normalized_response, "CHOICE: A")
        self.assertIsNone(result.invalid_reason)

    def test_parses_valid_action_response_with_surrounding_whitespace(self):
        result = parse_response(
            "  ACTION: cash_out  ",
            prefix="ACTION",
            valid_actions={"PUMP", "CASH_OUT"},
        )

        self.assertTrue(result.parse_success)
        self.assertEqual(result.parsed_action, "CASH_OUT")
        self.assertEqual(result.normalized_response, "ACTION: CASH_OUT")

    def test_parses_valid_response_inside_markdown_code_fence(self):
        result = parse_response(
            "```text\nACTION: PUMP\n```",
            prefix="ACTION",
            valid_actions={"PUMP", "CASH_OUT"},
        )

        self.assertTrue(result.parse_success)
        self.assertEqual(result.parsed_action, "PUMP")
        self.assertEqual(result.normalized_response, "ACTION: PUMP")

    def test_rejects_empty_response(self):
        result = parse_response("", prefix="CHOICE", valid_actions={"A", "B"})

        self.assertFalse(result.parse_success)
        self.assertEqual(result.invalid_reason, "empty_response")

    def test_rejects_invalid_option(self):
        result = parse_response("CHOICE: C", prefix="CHOICE", valid_actions={"A", "B"})

        self.assertFalse(result.parse_success)
        self.assertEqual(result.invalid_reason, "invalid_option")
        self.assertEqual(result.parsed_action, "C")

    def test_rejects_missing_required_prefix(self):
        result = parse_response("A", prefix="CHOICE", valid_actions={"A", "B"})

        self.assertFalse(result.parse_success)
        self.assertEqual(result.invalid_reason, "missing_required_prefix")

    def test_rejects_multiple_actions(self):
        result = parse_response(
            "CHOICE: A\nCHOICE: B",
            prefix="CHOICE",
            valid_actions={"A", "B"},
        )

        self.assertFalse(result.parse_success)
        self.assertEqual(result.invalid_reason, "multiple_actions")


if __name__ == "__main__":
    unittest.main()
