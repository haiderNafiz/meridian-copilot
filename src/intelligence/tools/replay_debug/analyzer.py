import json
from typing import Any, Dict, Optional
from .schema import ReplayRecord, ReplayExecutionResult, ReplayDiff

class DifferenceAnalyzer:
    @staticmethod
    def analyze(original: ReplayRecord, replayed: ReplayExecutionResult) -> ReplayDiff:
        orig_payload = original.output_payload
        repl_payload = replayed.output_payload
        
        outputs_match = (orig_payload == repl_payload)
        
        output_diff = {}
        if not outputs_match:
            output_diff = {
                "original": orig_payload,
                "replayed": repl_payload
            }
            
        orig_cost = original.cost.get("estimated_cost", 0.0) if original.cost else 0.0
        repl_cost = replayed.cost.get("estimated_cost", 0.0) if replayed.cost else 0.0
        cost_delta = round(repl_cost - orig_cost, 4)
        
        orig_dur = original.resource.get("duration_ms", 0.0) if original.resource else 0.0
        repl_dur = replayed.resource.get("duration_ms", 0.0) if replayed.resource else 0.0
        duration_delta = round(repl_dur - orig_dur, 2)
        
        orig_conf = 0.0
        if isinstance(orig_payload, dict):
            orig_conf = orig_payload.get("confidence", 0.0)
            
        repl_conf = 0.0
        if isinstance(repl_payload, dict):
            repl_conf = repl_payload.get("confidence", 0.0)
            
        confidence_delta = round(repl_conf - orig_conf, 4)
        
        reasoning_diff = None
        if isinstance(orig_payload, dict) and isinstance(repl_payload, dict):
            orig_trace = orig_payload.get("explanation") or orig_payload.get("reasoning")
            repl_trace = repl_payload.get("explanation") or repl_payload.get("reasoning")
            if orig_trace != repl_trace:
                reasoning_diff = f"Original: {orig_trace} | Replayed: {repl_trace}"
                
        return ReplayDiff(
            replay_id=original.replay_id,
            outputs_match=outputs_match,
            output_diff=output_diff,
            cost_delta=cost_delta,
            duration_delta_ms=duration_delta,
            confidence_delta=confidence_delta,
            reasoning_diff=reasoning_diff
        )
