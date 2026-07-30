from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class DeploymentEnv(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class ReleaseChannel(str, Enum):
    ALPHA = "alpha"
    BETA = "beta"
    STABLE = "stable"

class ValidationStatus(str, Enum):
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"

class SystemLifecycleState(str, Enum):
    INITIALIZING = "initializing"
    VALIDATING = "validating"
    BOOTSTRAPPING = "bootstrapping"
    READY = "ready"
    DEGRADED = "degraded"
    SHUTTING_DOWN = "shutting_down"
    STOPPED = "stopped"
    FAILED = "failed"

class DeploymentEventType(str, Enum):
    BOOTSTRAP_STARTED = "BOOTSTRAP_STARTED"
    PROFILE_LOADED = "PROFILE_LOADED"
    DEPENDENCIES_VALIDATED = "DEPENDENCIES_VALIDATED"
    PLUGIN_REGISTERED = "PLUGIN_REGISTERED"
    BOOTSTRAP_COMPLETED = "BOOTSTRAP_COMPLETED"
    BOOTSTRAP_FAILED = "BOOTSTRAP_FAILED"
    ROLLBACK_STARTED = "ROLLBACK_STARTED"
    ROLLBACK_COMPLETED = "ROLLBACK_COMPLETED"
    VALIDATION_FAILED = "VALIDATION_FAILED"

class FeatureFlag(BaseModel):
    key: str
    enabled: bool
    rules: Dict[str, Any] = Field(default_factory=dict)

class ConfigurationProfile(BaseModel):
    profile_id: str
    environment: DeploymentEnv
    release_channel: ReleaseChannel
    version: str
    feature_flags: List[FeatureFlag] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)

class DependencyDefinition(BaseModel):
    dependency_id: str
    dependency_type: str
    required_version: str
    optional: bool = False

class PluginDefinition(BaseModel):
    plugin_name: str
    version: str
    entry_point: str
    dependencies: List[DependencyDefinition] = Field(default_factory=list)
    capabilities: List[str] = Field(default_factory=list)

class DeploymentManifest(BaseModel):
    manifest_id: str
    profile_id: str
    platform_version: str
    created_at: str
    created_by: str
    checksum: str
    required_capabilities: List[str] = Field(default_factory=list)
    minimum_python_version: str = "3.10"
    minimum_node_version: str = "18.0"
    deployment_notes: Optional[str] = None
    schema_version: str = "1.0.0"
    plugins: List[PluginDefinition] = Field(default_factory=list)
    backup_before_deploy: bool = True

class CapabilityMetadata(BaseModel):
    capability_name: str
    provider_class: str
    registered_at: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ValidationItem(BaseModel):
    name: str
    status: ValidationStatus
    message: Optional[str] = None
    duration_ms: float

class ValidationResult(BaseModel):
    overall_status: ValidationStatus
    total_checks: int
    passed: int
    warnings: int
    failed: int
    duration_ms: float
    items: List[ValidationItem] = Field(default_factory=list)
    timestamp: str

class PlatformManifest(BaseModel):
    platform_name: str = "Meridian Revenue Intelligence"
    platform_version: str
    build_number: str
    git_commit: str
    build_timestamp: str
    python_version: str
    node_version: str
    platform_capabilities: List[str] = Field(default_factory=list)
    installed_plugins: List[PluginDefinition] = Field(default_factory=list)
    configuration_profile: Optional[ConfigurationProfile] = None
    deployment_history: List[Dict[str, Any]] = Field(default_factory=list)

class DiagnosticsReport(BaseModel):
    system_state: SystemLifecycleState
    uptime_seconds: float
    validation_results: ValidationResult
    active_capabilities: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    platform_manifest: Optional[PlatformManifest] = None

class DeploymentResponse(BaseModel):
    status: str
    message: Optional[str] = None
    diagnostics: Optional[DiagnosticsReport] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
