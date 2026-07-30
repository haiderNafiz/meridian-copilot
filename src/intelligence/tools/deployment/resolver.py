import re
from typing import Dict, List
from .schema import DependencyDefinition

class CompatibilityMatrix:
    def __init__(self):
        self.module_versions: Dict[str, str] = {
            "knowledge_platform": "2.1.0",
            "monitoring": "1.5.2",
            "memory": "3.0.1",
            "intent_rules": "1.0.0",
            "evaluation_framework": "1.0.0",
            "replay_debug": "1.0.0",
            "human_feedback": "1.0.0"
        }

class VersionResolver:
    def __init__(self, matrix: CompatibilityMatrix):
        self.matrix = matrix

    def _parse_version(self, version_str: str) -> tuple:
        parts = []
        for x in re.split(r'[^0-9]', version_str.strip()):
            if x.isdigit():
                parts.append(int(x))
        while len(parts) < 3:
            parts.append(0)
        return tuple(parts[:3])

    def compare_versions(self, version_a: str, operator: str, version_b: str) -> bool:
        v_a = self._parse_version(version_a)
        v_b = self._parse_version(version_b)
        if operator == ">=":
            return v_a >= v_b
        elif operator == "<=":
            return v_a <= v_b
        elif operator == ">":
            return v_a > v_b
        elif operator == "<":
            return v_a < v_b
        elif operator == "==":
            return v_a == v_b
        return False

    def resolve_dependencies(self, dependencies: List[DependencyDefinition]) -> bool:
        for dep in dependencies:
            target = dep.dependency_id
            if target not in self.matrix.module_versions:
                if dep.optional:
                    continue
                return False
            
            actual = self.matrix.module_versions[target]
            match = re.match(r"^([>=<!~]+)\s*([0-9a-zA-Z.-]+)$", dep.required_version.strip())
            if not match:
                if actual != dep.required_version.strip():
                    if dep.optional:
                        continue
                    return False
            else:
                op, req_v = match.groups()
                if not self.compare_versions(actual, op, req_v):
                    if dep.optional:
                        continue
                    return False
        return True
