import unittest
from pathlib import Path

from engine import ForwardChainingEngine, Rule
from kb_loader import load_rules


KB_PATH = (
    Path(__file__).resolve().parents[1]
    / "kb"
    / "laptop_rules.json"
)


class TestForwardChainingEngine(unittest.TestCase):
    def setUp(self):
        self.rules = load_rules(KB_PATH)

    def infer(self, facts):
        engine = ForwardChainingEngine(self.rules)
        engine.assert_facts(facts)
        engine.run()
        return engine

    def test_each_laptop_rule(self):
        cases = [
            (
                ["budget_high", "portable", "long_battery"],
                "recommend:premium_ultrabook"
            ),
            (
                ["budget_low", "office_only", "portable"],
                "recommend:budget_ultrabook"
            ),
            (
                ["gaming", "budget_medium"],
                "recommend:midrange_gaming_laptop"
            ),
            (
                ["gaming", "budget_high"],
                "recommend:high_end_gaming_laptop"
            ),
            (
                ["creative_work", "portable"],
                "spec:ram_16_plus"
            ),
            (
                ["creative_work", "large_screen"],
                "spec:display_15_plus_color_accurate"
            ),
            (
                ["travel_often", "long_battery"],
                "spec:battery_60wh_plus"
            ),
            (
                ["pref_os_macos"],
                "spec:macos_required"
            ),
            (
                ["needs_ai_accel"],
                "spec:gpu_with_tensor_cores"
            ),
            (
                ["pref_os_linux", "office_only"],
                "spec:linux_friendly_hw"
            )
        ]

        for facts, expected in cases:
            with self.subTest(expected=expected):
                engine = self.infer(facts)
                self.assertIn(expected, engine.facts)
                self.assertEqual(len(engine.trace), 1)

    def test_missing_condition_prevents_firing(self):
        engine = self.infer(["budget_high", "portable"])

        self.assertNotIn(
            "recommend:premium_ultrabook",
            engine.facts
        )
        self.assertEqual(engine.trace, [])

    def test_multiple_rules_can_fire(self):
        engine = self.infer([
            "creative_work",
            "portable",
            "large_screen"
        ])

        self.assertEqual(
            set(engine.conclusions()["specs"]),
            {"ram_16_plus", "display_15_plus_color_accurate"}
        )

    def test_forward_chaining_requires_another_pass(self):
        # Put the dependent rule first to verify repeated reasoning.
        rules = [
            Rule(["intermediate"], "recommend:result", name="Second"),
            Rule(["start"], "intermediate", name="First")
        ]

        engine = ForwardChainingEngine(rules)
        engine.assert_facts(["start"])
        engine.run()

        self.assertIn("recommend:result", engine.facts)
        self.assertEqual(
            [step["rule"] for step in engine.trace],
            ["First", "Second"]
        )

    def test_running_again_does_not_repeat_rules(self):
        engine = self.infer(["gaming", "budget_medium"])
        original_trace_length = len(engine.trace)

        engine.run()

        self.assertEqual(len(engine.trace), original_trace_length)

    def test_no_matching_rules(self):
        engine = self.infer(["budget_low", "pref_os_windows"])

        self.assertEqual(engine.conclusions()["recommendations"], [])
        self.assertEqual(engine.conclusions()["specs"], [])
        self.assertEqual(engine.trace, [])


if __name__ == "__main__":
    unittest.main()