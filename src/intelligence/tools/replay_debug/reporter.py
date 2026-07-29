import os
import json
from typing import Optional
from .schema import ReplayRecord, ReplayExecutionResult, ReplayDiff

class DebugReporter:
    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            self.base_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../../../../../reports/debug")
            )
        else:
            self.base_dir = os.path.abspath(base_dir)
            
        os.makedirs(self.base_dir, exist_ok=True)

    def generate_report(self, original: ReplayRecord, replayed: ReplayExecutionResult, diff: ReplayDiff, format: str = "json") -> str:
        report_id = f"debug_{original.replay_id}_{original.run_id}"
        
        if format.lower() == "markdown":
            filepath = os.path.join(self.base_dir, f"{report_id}.md")
            content = self._render_markdown(original, replayed, diff)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            return filepath
        else:
            filepath = os.path.join(self.base_dir, f"{report_id}.json")
            data = {
                "report_id": report_id,
                "original": original.model_dump(),
                "replayed": replayed.model_dump(),
                "diff": diff.model_dump()
            }
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return filepath

    def _render_markdown(self, original: ReplayRecord, replayed: ReplayExecutionResult, diff: ReplayDiff) -> str:
        status_emoji = "✅" if diff.outputs_match else "❌ WARNING: OUTPUT MISMATCH"
        
        orig_dur = original.resource.get("duration_ms", 0.0) if original.resource else 0.0
        repl_dur = replayed.resource.get("duration_ms", 0.0) if replayed.resource else 0.0
        
        orig_cost = original.cost.get("estimated_cost", 0.0) if original.cost else 0.0
        repl_cost = replayed.cost.get("estimated_cost", 0.0) if replayed.cost else 0.0
        
        orig_conf = original.output_payload.get("confidence", 0.0) if isinstance(original.output_payload, dict) else 0.0
        repl_conf = replayed.output_payload.get("confidence", 0.0) if isinstance(replayed.output_payload, dict) else 0.0
        
        return f"""# Replay Debug Report: {original.replay_id}

- **Target Component**: `{original.target_id}`
- **Original Run ID**: `{original.run_id}`
- **Version Tested**: `{original.version}`
- **Replay Status**: {status_emoji}

---

## 1. Execution Differences

| Metric | Original | Replayed | Delta |
| :--- | :--- | :--- | :--- |
| **Duration (ms)** | {orig_dur} | {repl_dur} | {diff.duration_delta_ms} |
| **Cost ($)** | {orig_cost} | {repl_cost} | {diff.cost_delta} |
| **Confidence** | {orig_conf} | {repl_conf} | {diff.confidence_delta} |

---

## 2. Output Payloads Comparison

### Original Output
```json
{json.dumps(original.output_payload, indent=2)}
```

### Replayed Output
```json
{json.dumps(replayed.output_payload, indent=2)}
```

### Structural Diff Details
```json
{json.dumps(diff.output_diff, indent=2)}
```

---

## 3. Reasoning & Explanations Traces
- **Reasoning Diff**: `{diff.reasoning_diff or 'No changes in explanation traces detected.'}`
"""
