from pydantic import BaseModel, Field

class RetryPolicy(BaseModel):
    max_retries: int = Field(default=0, ge=0, description="Maximum execution attempts to retry on tool failures")
    initial_delay: float = Field(default=0.0, ge=0.0, description="Base retry delay interval in seconds")
    backoff: float = Field(default=1.0, ge=1.0, description="Exponential multiplier backoff factor")
