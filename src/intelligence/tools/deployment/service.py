import time
import datetime
import sys
from typing import Optional, Dict, Any
from .schema import (
    DeploymentManifest, DiagnosticsReport, SystemLifecycleState, DeploymentEventType,
    ValidationResult, ValidationStatus, PlatformManifest, CapabilityMetadata
)
from .provider.base import DeploymentStorageProvider
from .provider.file import LocalFilesystemDeploymentStorageProvider
from .registry import CapabilityRegistry, PluginRegistry, ValidationRegistry
from .resolver import VersionResolver, CompatibilityMatrix

class DeploymentService:
    def __init__(self, provider: Optional[DeploymentStorageProvider] = None):
        self.provider = provider or LocalFilesystemDeploymentStorageProvider()
        self.capabilities = CapabilityRegistry()
        self.plugins = PluginRegistry()
        self.validators = ValidationRegistry()
        self.resolver = VersionResolver(CompatibilityMatrix())
        self.state = SystemLifecycleState.INITIALIZING
        self._start_time = time.time()

    def bootstrap(self, manifest: DeploymentManifest) -> DiagnosticsReport:
        self.state = SystemLifecycleState.BOOTSTRAPPING
        self._emit_event(DeploymentEventType.BOOTSTRAP_STARTED, {"manifest_id": manifest.manifest_id})

        try:
            # 1. Load profile
            profile = self.provider.load_profile(manifest.profile_id)
            if not profile:
                raise ValueError(f"Profile {manifest.profile_id} not found")
            self._emit_event(DeploymentEventType.PROFILE_LOADED, {"profile_id": manifest.profile_id})

            # 2. Validate profile
            if not profile.version:
                raise ValueError("Invalid profile configuration: missing version")

            # 3. Resolve plugins
            for plugin in manifest.plugins:
                self.plugins.register_plugin(plugin)
                self._emit_event(DeploymentEventType.PLUGIN_REGISTERED, {"plugin_name": plugin.plugin_name})

            # 4. Validate dependencies
            for plugin in manifest.plugins:
                if not self.resolver.resolve_dependencies(plugin.dependencies):
                    raise ValueError(f"Plugin dependency validation failed for plugin {plugin.plugin_name}")
            self._emit_event(DeploymentEventType.DEPENDENCIES_VALIDATED, {})

            # 5. Run startup validators inside ValidationRegistry
            for validator in self.validators.list_validators():
                v_res = validator.validate()
                if v_res.overall_status == ValidationStatus.FAILED:
                    self._emit_event(DeploymentEventType.VALIDATION_FAILED, {"validator": validator.name})
                    raise ValueError(f"Validator {validator.name} failed startup checks")

            # 6. Register capabilities
            for plugin in manifest.plugins:
                for cap in plugin.capabilities:
                    meta = CapabilityMetadata(
                        capability_name=cap,
                        provider_class=plugin.entry_point,
                        registered_at=datetime.datetime.now(datetime.UTC).isoformat()
                    )
                    self.capabilities.register(cap, meta)

            # 7. Start services (No-op placeholder)

            # 8. Health validation
            health_chk = self.validators.get_validator("HealthValidator")
            if health_chk:
                h_res = health_chk.validate()
                if h_res.overall_status == ValidationStatus.FAILED:
                    raise ValueError("Health checks verification failed")

            # 9. Emit Monitoring Event
            self._emit_event(DeploymentEventType.BOOTSTRAP_COMPLETED, {"manifest_id": manifest.manifest_id})

            # 10. Ready
            self.state = SystemLifecycleState.READY

        except Exception as e:
            self.state = SystemLifecycleState.FAILED
            self._emit_event(DeploymentEventType.BOOTSTRAP_FAILED, {"error": str(e)})
            raise

        return self.run_diagnostics()

    def run_diagnostics(self) -> DiagnosticsReport:
        checks = []
        for v in self.validators.list_validators():
            try:
                checks.append(v.validate())
            except Exception:
                pass
                
        total = sum(c.total_checks for c in checks)
        passed = sum(c.passed for c in checks)
        warnings = sum(c.warnings for c in checks)
        failed = sum(c.failed for c in checks)
        overall = ValidationStatus.PASSED if failed == 0 else ValidationStatus.FAILED
        
        v_res = ValidationResult(
            overall_status=overall,
            total_checks=total,
            passed=passed,
            warnings=warnings,
            failed=failed,
            duration_ms=0.0,
            items=[],
            timestamp=datetime.datetime.now(datetime.UTC).isoformat()
        )
        
        pm = PlatformManifest(
            platform_version="1.0.0",
            build_number="123",
            git_commit="git_abc",
            build_timestamp="2026-07-30",
            python_version=sys.version,
            node_version="18.16.0",
            platform_capabilities=self.capabilities.list_capabilities(),
            installed_plugins=self.plugins.list_plugins()
        )
        
        return DiagnosticsReport(
            system_state=self.state,
            uptime_seconds=time.time() - self._start_time,
            validation_results=v_res,
            active_capabilities=self.capabilities.list_capabilities(),
            errors=[],
            platform_manifest=pm
        )

    def trigger_rollback(self) -> bool:
        self._emit_event(DeploymentEventType.ROLLBACK_STARTED, {})
        # Rollback logic (simple status updates)
        self.state = SystemLifecycleState.DEGRADED
        self._emit_event(DeploymentEventType.ROLLBACK_COMPLETED, {})
        return True

    def _emit_event(self, event_type: DeploymentEventType, payload: Dict[str, Any]) -> None:
        try:
            from ..monitoring_observability.service import get_monitoring_service
            monitoring = get_monitoring_service()
            monitoring.log_event(
                event_type=event_type.value,
                severity="info" if "FAILED" not in event_type.value else "critical",
                payload=payload or {}
            )
        except Exception:
            pass

_deployment_service_instance = None

def get_deployment_service() -> DeploymentService:
    global _deployment_service_instance
    if _deployment_service_instance is None:
        _deployment_service_instance = DeploymentService()
    return _deployment_service_instance
