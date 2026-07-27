from typing import List, Dict, Any

class RecommendationBuilder:
    def build_recommendations(
        self,
        risks: List[str],
        blockers: List[str],
        missing: List[str]
    ) -> List[str]:
        """Rank and prioritize recommended next actions based on assessment items."""
        actions = []
        
        # 1. Resolve blockers first (High priority / Urgent)
        for blocker in blockers:
            actions.append(f"CRITICAL: Resolve blocker - {blocker}")
            
        # 2. Resolve missing information (Medium priority)
        for item in missing:
            actions.append(f"REQUIRED: Obtain missing information - {item}")
            
        # 3. Mitigate risks (Low priority)
        for risk in risks:
            actions.append(f"ADVISORY: Verify and mitigate risk - {risk}")
            
        if not actions:
            actions.append("STANDARD: Complete regular vetting steps.")
            
        return actions
