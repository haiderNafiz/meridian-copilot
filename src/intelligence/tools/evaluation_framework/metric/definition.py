from pydantic import BaseModel, Field

class MetricDefinition(BaseModel):
    name: str = Field(description="Unique metric name (e.g. accuracy)")
    description: str = Field(description="Details on what this metric represents")
    category: str = Field(description="Category (e.g. classification, generation)")
    target_threshold: float = Field(default=0.8, description="Default pass threshold")
    higher_is_better: bool = Field(default=True)
    unit: str = Field(default="ratio")
    aggregation_method: str = Field(default="macro")
