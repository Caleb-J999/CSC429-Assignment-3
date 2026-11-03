from pathlib import Path

from kb_loader import load_rules
from engine import ForwardChainingEngine


KB_PATH = Path(__file__).resolve().parent / "kb" / "laptop_rules.json"


def ask_yes_no(question):
    """Keep asking until the user enters a valid yes/no answer."""
    while True:
        answer = input(question + " (y/n): ").strip().lower()

        if answer in ("y", "yes"):
            return True

        if answer in ("n", "no"):
            return False

        print("Please enter y or n.")


def ask_choice(question, choices):
    """Ask the user until they choose an allowed value."""
    while True:
        answer = input(
            question + " (" + "/".join(choices) + "): "
        ).strip().lower()

        if answer in choices:
            return answer

        print("Please choose: " + ", ".join(choices))


def collect_initial_facts():
    facts = []

    budget = ask_choice(
        "What is your budget?",
        ("low", "medium", "high")
    )
    facts.append("budget_" + budget)

    questions = [
        ("Is portability important?", "portable"),
        ("Do you need long battery life?", "long_battery"),
        ("Will you use the laptop for gaming?", "gaming"),
        ("Will you use it for creative work?", "creative_work"),
        ("Is it only for office or basic productivity work?", "office_only"),
        ("Do you need AI acceleration?", "needs_ai_accel"),
        ("Do you want a large screen?", "large_screen"),
        ("Do you travel often?", "travel_often")
    ]

    for question, fact in questions:
        if ask_yes_no(question):
            facts.append(fact)

    operating_system = ask_choice(
        "Which operating system do you prefer?",
        ("windows", "macos", "linux")
    )
    facts.append("pref_os_" + operating_system)

    return facts


def main():
    print("Laptop Advisor")
    print("Answer the questions to receive rule-based advice.\n")

    rules = load_rules(KB_PATH)

    engine = ForwardChainingEngine(rules)
    initial_facts = collect_initial_facts()

    engine.assert_facts(initial_facts)
    engine.run()

    results = engine.conclusions()

    print("\nRecommendations:")
    if results["recommendations"]:
        for recommendation in results["recommendations"]:
            print("- " + recommendation)
    else:
        print("- No laptop category matched the current rules.")

    print("\nSuggested specifications:")
    if results["specs"]:
        for specification in results["specs"]:
            print("- " + specification)
    else:
        print("- No additional specifications were derived.")

    print("\nExplanation / fired rules:")
    if engine.trace:
        for step in engine.trace:
            conditions = " AND ".join(step["antecedents"])
            print(
                f"- {step['rule']}: "
                f"{conditions} -> {step['consequent']}"
            )
    else:
        print("- No rules fired.")


if __name__ == "__main__":
    main()