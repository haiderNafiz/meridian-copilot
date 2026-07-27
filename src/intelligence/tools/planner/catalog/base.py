from typing import Dict, Optional, List
from pydantic import BaseModel, Field
from src.intelligence.tools.agent_orchestrator.schema import ExecutionNode

class WorkflowTemplate(BaseModel):
    name: str = Field(description="Unique catalog workflow identifier")
    description: str = Field(description="High-level target purpose summary")
    nodes: List[ExecutionNode] = Field(description="Static sequenced execution nodes blueprints")

class WorkflowCatalog:
    def __init__(self):
        self._templates: Dict[str, WorkflowTemplate] = {}
        self._initialize_catalog()

    def register_template(self, template: WorkflowTemplate) -> None:
        self._templates[template.name] = template

    def get_template(self, name: str) -> Optional[WorkflowTemplate]:
        return self._templates.get(name)

    def get_all_workflows(self) -> List[str]:
        return list(self._templates.keys())

    def _initialize_catalog(self) -> None:
        # 1. CandidateAssessmentWorkflow (Standard sequential pipeline)
        self.register_template(WorkflowTemplate(
            name="CandidateAssessmentWorkflow",
            description="Complete deterministic pipeline from raw intake to compiled context builder.",
            nodes=[
                ExecutionNode(tool_name="intent_classifier", arguments_mapping={"query_text": "initial_query"}),
                ExecutionNode(tool_name="candidate_profiler", arguments_mapping={"raw_text": "initial_query"}),
                ExecutionNode(tool_name="deterministic_enricher", arguments_mapping={
                    "email": "email",
                    "location": "location",
                    "technology_keywords": "technology_keywords",
                    "candidate_profile": "candidate_profiler"
                }),
                ExecutionNode(tool_name="knowledge_service", arguments_mapping={"query_text": "initial_query"}),
                ExecutionNode(tool_name="qualification_scorer", arguments_mapping={
                    "candidate_profile": "candidate_profiler",
                    "candidate_enrichment": "deterministic_enricher",
                    "retrieved_context": "knowledge_service"
                }),
                ExecutionNode(tool_name="summarizer", arguments_mapping={
                    "candidate_profile": "candidate_profiler",
                    "candidate_enrichment": "deterministic_enricher",
                    "retrieved_context": "knowledge_service",
                    "qualification_scores": "qualification_scorer"
                }),
                ExecutionNode(tool_name="context_builder", arguments_mapping={
                    "context_id": "context_id",
                    "session_id": "session_id",
                    "raw_text": "initial_query",
                    "candidate_profile": "candidate_profiler",
                    "candidate_enrichment": "deterministic_enricher",
                    "retrieved_context": "knowledge_service",
                    "qualification_scores": "qualification_scorer",
                    "recruiter_summary": "summarizer"
                }),
                ExecutionNode(tool_name="save_memory", arguments_mapping={
                    "snapshot": "context_builder.payload",
                    "session_id": "session_id"
                })
            ]
        ))
        
        # 2. RecruiterWorkflow (Lookup-only fast track)
        self.register_template(WorkflowTemplate(
            name="RecruiterWorkflow",
            description="Bypasses profiling, running knowledge checks and qualification matches.",
            nodes=[
                ExecutionNode(tool_name="knowledge_service", arguments_mapping={"query_text": "initial_query"}),
                ExecutionNode(tool_name="qualification_scorer", arguments_mapping={
                    "candidate_profile": "candidate_profiler",
                    "candidate_enrichment": "deterministic_enricher",
                    "retrieved_context": "knowledge_service"
                })
            ]
        ))
        
        # 3. ConversationWorkflow (Memory retrieve only)
        self.register_template(WorkflowTemplate(
            name="ConversationWorkflow",
            description="Historical search and memory context loader.",
            nodes=[
                ExecutionNode(tool_name="retrieve_memory", arguments_mapping={
                    "session_id": "session_id"
                })
            ]
        ))
