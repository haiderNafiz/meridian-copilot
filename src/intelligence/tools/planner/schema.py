from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from src.intelligence.platform.contracts import BaseRequest, BaseResponse
from src.intelligence.tools.agent_orchestrator.schema import ExecutionPlan, ToolMetadata
from src.intelligence.tools.context_builder.schema import ContextSnapshot

class PlannerRequest(BaseRequest):
    query_text: str = Field(description="Raw user instruction prompting execution mapping")
    session_id: Optional[str] = Field(default=None, description="Conversational session code")
    context_id: Optional[str] = Field(default=None, description="Preceding context snapshot tracking ID")
    force_workflow: Optional[str] = Field(default=None, description="Enforced workflow template name bypass")
    email: Optional[str] = Field(default=None, description="Optional raw candidate email override")
    location: Optional[str] = Field(default=None, description="Optional raw candidate location override")
    technology_keywords: Optional[List[str]] = Field(default_factory=list, description="Optional raw technologies list")

class PlannerContext(BaseModel):
    current_context: Optional[ContextSnapshot] = Field(default=None, description="Current parsed context snapshot")
    retrieved_memories: List[ContextSnapshot] = Field(default_factory=list, description="Relevant memories resolved via MemoryService")
    available_tools: List[ToolMetadata] = Field(default_factory=list, description="Active tools fetched from AgentOrchestrator registry")

class PlannerConstraints(BaseModel):
    required_tools: List[str] = Field(default_factory=list, description="Explicit tools required by selected workflow")
    available_tools: List[str] = Field(default_factory=list, description="List of registered/enabled system tools")
    disabled_tools: List[str] = Field(default_factory=list, description="Explicit blacklist of disabled tools")
    context_requirements: List[str] = Field(default_factory=list, description="Mandatory keys needed inside current_context or request")
    memory_availability: bool = Field(default=True, description="Flag checking memory service availability status")

class PlannerDecision(BaseModel):
    selected_workflow: str = Field(description="Name of the catalog template selected")
    reasoning: str = Field(description="Concise rationale behind catalog mapping selection")
    confidence: float = Field(ge=0.0, le=1.0, description="Selection certainty score")
    assumptions: List[str] = Field(default_factory=list, description="Unverified conditions assumed during planning")
    missing_information: List[str] = Field(default_factory=list, description="Details needed but currently unavailable")

class PlannerEvaluationMetrics(BaseModel):
    planning_latency_ms: float = Field(description="Time elapsed during plan resolve phase")
    workflow_selection_confidence: float = Field(description="Confidence rating of workflow classification")
    constraint_violations: List[str] = Field(default_factory=list, description="Any warnings caught by ConstraintResolver")
    workflow_complexity: int = Field(description="Total nodes count inside target plan")
    estimated_execution_cost: float = Field(default=0.0, description="Estimated token multiplier cost projection")
    estimated_execution_depth: int = Field(description="Estimated dependency execution tree depth")

class PlannerResult(BaseResponse):
    execution_plan: Optional[ExecutionPlan] = Field(default=None, description="Compatible execution plan object")
    planning_trace: str = Field(description="Trace transaction code mapping request flow")
    planner_reasoning_summary: str = Field(description="Auditable summary detailing why this plan was generated")
    confidence: float = Field(description="Plan resolve confidence score")
    assumptions: List[str] = Field(default_factory=list, description="Assumptions noted by planner strategy")
    missing_information: List[str] = Field(default_factory=list, description="Unresolved details needed for completion")
    selected_workflow: str = Field(description="Target catalog template name")
    metrics: PlannerEvaluationMetrics = Field(description="Telemetry and scheduling performance metadata")

class PlanningFailure(BaseModel):
    status: str = Field(default="failure", description="Outcome status code")
    error_code: str = Field(description="Designated error class identifier")
    message: str = Field(description="Descriptive explanation of the failure")
    trace_id: str = Field(description="Unique tracking reference code")
    missing_details: List[str] = Field(default_factory=list, description="Unresolved required fields or missing tools")
