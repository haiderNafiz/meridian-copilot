from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from src.intelligence.platform.contracts import BaseRequest, BaseResponse
from src.intelligence.tools.context_builder.schema import ContextSnapshot

class OrchestrationRequest(BaseRequest):
    query_text: str = Field(description="Raw user message prompting orchestration action")
    session_id: Optional[str] = Field(default=None, description="Conversational session code")
    context_id: Optional[str] = Field(default=None, description="Initial or preceding Context ID (if any)")
    force_tools: List[str] = Field(default_factory=list, description="Explicit tools list to enforce bypassing intent classification")
    email: Optional[str] = Field(default=None, description="Optional raw candidate email")
    location: Optional[str] = Field(default=None, description="Optional raw candidate location")
    technology_keywords: Optional[List[str]] = Field(default_factory=list, description="Optional raw technologies list")

class OrchestrationResult(BaseResponse):
    context_snapshot: Optional[ContextSnapshot] = Field(default=None, description="The final compiled ContextSnapshot")
    execution_trace_id: str = Field(description="Unique tracing transaction ID for this flow execution")
    completed_steps: List[str] = Field(default_factory=list, description="List of successfully executed tool names")
    failed_steps: List[str] = Field(default_factory=list, description="List of failed tool names")

class ToolMetadata(BaseModel):
    name: str = Field(description="Unique system name identifying the tool")
    version: str = Field(default="1.0.0", description="SemVer designation of target tool")
    enabled: bool = Field(default=True, description="Flag indicating if tool is available for selection")
    dependencies: List[str] = Field(default_factory=list, description="List of tool names required before execution")

class ExecutionNode(BaseModel):
    tool_name: str = Field(description="Name of the tool to execute")
    arguments_mapping: Dict[str, str] = Field(
        default_factory=dict, 
        description="Mappings routing context fields into tool input arguments (e.g. {'raw_text': 'inputs.raw_text'})"
    )

class ExecutionPlan(BaseModel):
    plan_id: str = Field(description="Unique code identifying plan instance")
    nodes: List[ExecutionNode] = Field(description="Ordered list of deterministic execution steps")

class ExecutionContext(BaseModel):
    trace_id: str = Field(description="Trace ID tracking execution path")
    session_id: Optional[str] = Field(default=None, description="Conversational session identifier")
    outputs: Dict[str, Any] = Field(default_factory=dict, description="Stores outputs returned by each executed tool")
    created_at: datetime = Field(default_factory=datetime.utcnow)
