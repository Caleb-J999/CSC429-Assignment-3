from dataclasses import dataclass
from typing import List, Set, Dict, Any


@dataclass
class Rule:
    antecedents: List[str]
    consequent: str
    priority: int = 0
    name: str = ""


class ForwardChainingEngine:
    def __init__(self, rules: List[Rule]):
        self.rules = rules
        self.facts: Set[str] = set()
        self.trace: List[Dict[str, Any]] = []

    def assert_facts(self, initial: List[str]) -> None:
        """Store initial facts into the working memory."""
        self.facts.update(initial)

    def can_fire(self, rule: Rule) -> bool:
        """Return True if all conditions hold and the result is new."""
        return (
            all(fact in self.facts for fact in rule.antecedents)
            and rule.consequent not in self.facts
        )

    def run(self) -> None:
        """Apply rules until no additional facts can be derived."""
        while True:
            applicable_rules = [
                rule for rule in self.rules if self.can_fire(rule)
            ]

            if not applicable_rules:
                break

            selected_rule = max(
                applicable_rules,
                key=lambda rule: rule.priority
            )

            self.facts.add(selected_rule.consequent)

            self.trace.append({
                "rule": selected_rule.name,
                "antecedents": list(selected_rule.antecedents),
                "consequent": selected_rule.consequent
            })

    def conclusions(self) -> Dict[str, List[str]]:
        """Separate recommendations, specifications, and other facts."""
        results = {
            "recommendations": [],
            "specs": [],
            "other": []
        }

        for fact in sorted(self.facts):
            if fact.startswith("recommend:"):
                results["recommendations"].append(fact.split(":", 1)[1])
            elif fact.startswith("spec:"):
                results["specs"].append(fact.split(":", 1)[1])
            else:
                results["other"].append(fact)

        return results