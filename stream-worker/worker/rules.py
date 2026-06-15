import json
import os
from dataclasses import dataclass, field


@dataclass
class AlarmRule:
    metric_name: str
    threshold: float
    severity: str
    title: str
    description: str


DEFAULT_RULES: list[AlarmRule] = [
    AlarmRule(
        metric_name="temperature",
        threshold=76.0,
        severity="warning",
        title="腔体温度偏高",
        description="设备温度超过阈值，请检查冷却与工艺状态。",
    ),
    AlarmRule(
        metric_name="pressure",
        threshold=2.85,
        severity="warning",
        title="压力波动偏高",
        description="设备压力超过阈值，请检查气路与腔体状态。",
    ),
]


def _parse_rules_json(raw: str) -> list[AlarmRule]:
    data = json.loads(raw)
    return [
        AlarmRule(
            metric_name=item["metric_name"],
            threshold=item["threshold"],
            severity=item.get("severity", "warning"),
            title=item.get("title", f"{item['metric_name']} 超限"),
            description=item.get("description", ""),
        )
        for item in data
    ]


@dataclass
class RuleEngine:
    rules: dict[str, AlarmRule] = field(default_factory=dict)

    @classmethod
    def from_env(cls) -> "RuleEngine":
        raw = os.getenv("ALARM_RULES_JSON", "")
        if raw:
            rules = _parse_rules_json(raw)
        else:
            rules = DEFAULT_RULES
        return cls({r.metric_name: r for r in rules})

    def evaluate(self, metric_name: str, value: float) -> AlarmRule | None:
        rule = self.rules.get(metric_name)
        if rule and value >= rule.threshold:
            return rule
        return None

    def clearance_check(self, metric_name: str, value: float) -> bool:
        rule = self.rules.get(metric_name)
        if rule is None:
            return False
        return value < rule.threshold
