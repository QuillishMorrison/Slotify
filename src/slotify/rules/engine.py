from __future__ import annotations

from dataclasses import dataclass, field

from slotify.domain import Event, ScheduleState
from slotify.rules.base import Rule, RuleContext


@dataclass(slots=True)
class RuleEngine:
    rules: list[Rule] = field(default_factory=list)

    def add_rule(self, rule: Rule) -> None:
        self.rules.append(rule)

    def validate(self, schedule: ScheduleState, event: Event, context: RuleContext) -> None:
        for rule in self.rules:
            rule.validate(schedule, event, context)
