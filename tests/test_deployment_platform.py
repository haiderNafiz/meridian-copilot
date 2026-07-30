import pytest
from src.intelligence.tools.deployment.schema import (
    DeploymentManifest, ConfigurationProfile, DeploymentEnv, ReleaseChannel,
    ValidationResult, ValidationStatus, PlatformManifest, SystemLifecycleState
)

def test_deployment_manifest_schemas():
    profile = ConfigurationProfile(
        profile_id="prod_profile",
        environment=DeploymentEnv.PRODUCTION,
        release_channel=ReleaseChannel.STABLE,
        version="v2.1"
    )
    assert profile.profile_id == "prod_profile"

    manifest = DeploymentManifest(
        manifest_id="dep_001",
        profile_id="prod_profile",
        platform_version="1.0.0",
        created_at="2026-07-30",
        created_by="engineer_x",
        checksum="sha256_xyz"
    )
    assert manifest.manifest_id == "dep_001"
    assert manifest.minimum_python_version == "3.10"

def test_version_resolver():
    from src.intelligence.tools.deployment.resolver import VersionResolver, CompatibilityMatrix
    from src.intelligence.tools.deployment.schema import DependencyDefinition

    matrix = CompatibilityMatrix()
    resolver = VersionResolver(matrix)

    dep_ok = DependencyDefinition(
        dependency_id="knowledge_platform",
        dependency_type="module",
        required_version=">=2.0"
    )
    dep_fail = DependencyDefinition(
        dependency_id="memory",
        dependency_type="module",
        required_version=">=4.0"
    )
    dep_optional = DependencyDefinition(
        dependency_id="unknown_plugin",
        dependency_type="plugin",
        required_version=">=1.0",
        optional=True
    )

    assert resolver.resolve_dependencies([dep_ok]) is True
    assert resolver.resolve_dependencies([dep_fail]) is False
    assert resolver.resolve_dependencies([dep_optional]) is True

def test_validation_and_rollback_strategies():
    from src.intelligence.tools.deployment.strategy.validation import StartupValidator, DependencyValidator
    from src.intelligence.tools.deployment.strategy.migration import DefaultConfigMigrationStrategy
    from src.intelligence.tools.deployment.strategy.rollback import DefaultRollbackStrategy
    from src.intelligence.tools.deployment.schema import ConfigurationProfile, DeploymentEnv, ReleaseChannel
    
    startup = StartupValidator()
    res = startup.validate()
    assert res.overall_status == ValidationStatus.PASSED
    assert res.total_checks == 1
    
    migrator = DefaultConfigMigrationStrategy()
    profile = ConfigurationProfile(profile_id="p1", environment=DeploymentEnv.DEVELOPMENT, release_channel=ReleaseChannel.ALPHA, version="v1.0")
    migrated = migrator.migrate(profile)
    assert migrated.version == "v3.0.0"
    
    rollback = DefaultRollbackStrategy()
    assert rollback.execute_rollback() is True
    assert rollback.rollback_executed is True

def test_registries_and_storage_provider():
    import tempfile
    from src.intelligence.tools.deployment.registry import CapabilityRegistry, PluginRegistry, ValidationRegistry
    from src.intelligence.tools.deployment.provider.file import LocalFilesystemDeploymentStorageProvider
    from src.intelligence.tools.deployment.schema import CapabilityMetadata, PluginDefinition
    from src.intelligence.tools.deployment.strategy.validation import StartupValidator
    
    cap_reg = CapabilityRegistry()
    cap_reg.register("nlp_retrieval", CapabilityMetadata(capability_name="nlp_retrieval", provider_class="NlpProvider", registered_at="2026"))
    assert "nlp_retrieval" in cap_reg.list_capabilities()
    
    val_reg = ValidationRegistry()
    startup = StartupValidator()
    val_reg.register(startup)
    assert val_reg.get_validator("StartupValidator") is not None
    
    with tempfile.TemporaryDirectory() as tmpdir:
        provider = LocalFilesystemDeploymentStorageProvider(base_dir=tmpdir)
        profile = ConfigurationProfile(profile_id="p2", environment=DeploymentEnv.DEVELOPMENT, release_channel=ReleaseChannel.ALPHA, version="v1.0")
        provider.save_profile(profile)
        
        loaded = provider.load_profile("p2")
        assert loaded is not None
        assert loaded.version == "v1.0"

def test_deployment_service_facade():
    import tempfile
    from src.intelligence.tools.deployment.service import DeploymentService
    from src.intelligence.tools.deployment.provider.file import LocalFilesystemDeploymentStorageProvider
    from src.intelligence.tools.deployment.schema import DeploymentManifest, PluginDefinition, DependencyDefinition
    from src.intelligence.tools.deployment.strategy.validation import StartupValidator, HealthValidator
    
    with tempfile.TemporaryDirectory() as tmpdir:
        provider = LocalFilesystemDeploymentStorageProvider(base_dir=tmpdir)
        
        profile = ConfigurationProfile(profile_id="prof_abc", environment=DeploymentEnv.STAGING, release_channel=ReleaseChannel.BETA, version="v1.0.0")
        provider.save_profile(profile)
        
        service = DeploymentService(provider=provider)
        
        service.validators.register(StartupValidator())
        service.validators.register(HealthValidator())
        
        manifest = DeploymentManifest(
            manifest_id="man_abc",
            profile_id="prof_abc",
            platform_version="1.0.0",
            created_at="2026-07-30",
            created_by="engineer_y",
            checksum="sha_abc",
            plugins=[
                PluginDefinition(
                    plugin_name="nlp_plugin",
                    version="1.0.0",
                    entry_point="NlpPluginClass",
                    dependencies=[
                        DependencyDefinition(dependency_id="knowledge_platform", dependency_type="module", required_version=">=2.0")
                    ],
                    capabilities=["nlp_retrieval"]
                )
            ]
        )
        
        report = service.bootstrap(manifest)
        assert report.system_state == SystemLifecycleState.READY
        assert "nlp_retrieval" in report.active_capabilities
        assert report.platform_manifest.platform_version == "1.0.0"
        
        assert service.trigger_rollback() is True
        assert service.state == SystemLifecycleState.DEGRADED

@pytest.mark.anyio
async def test_mcp_deployment_tools():
    import json
    import tempfile
    from src.intelligence.mcp.server import deployment_bootstrap, deployment_diagnostics, deployment_rollback, deployment_capabilities
    from src.intelligence.tools.deployment.service import get_deployment_service
    from src.intelligence.tools.deployment.provider.file import LocalFilesystemDeploymentStorageProvider
    from src.intelligence.tools.deployment.schema import ConfigurationProfile, DeploymentEnv, ReleaseChannel, PluginDefinition, DependencyDefinition
    
    with tempfile.TemporaryDirectory() as tmpdir:
        provider = LocalFilesystemDeploymentStorageProvider(base_dir=tmpdir)
        
        import src.intelligence.tools.deployment.service as dep_service_module
        service = dep_service_module.DeploymentService(provider=provider)
        dep_service_module._deployment_service_instance = service
        
        profile = ConfigurationProfile(profile_id="prof_mcp", environment=DeploymentEnv.DEVELOPMENT, release_channel=ReleaseChannel.ALPHA, version="v1.0")
        provider.save_profile(profile)
        
        manifest = {
            "manifest_id": "man_mcp",
            "profile_id": "prof_mcp",
            "platform_version": "1.0.0",
            "created_at": "2026-07-30",
            "created_by": "engineer_z",
            "checksum": "sha_xyz",
            "plugins": [
                {
                    "plugin_name": "test_plug",
                    "version": "1.0.0",
                    "entry_point": "TestClass",
                    "dependencies": [
                        {"dependency_id": "knowledge_platform", "dependency_type": "module", "required_version": ">=2.0"}
                    ],
                    "capabilities": ["test_cap"]
                }
            ]
        }
        
        res_boot = await deployment_bootstrap(manifest=manifest)
        data_boot = json.loads(res_boot)
        assert data_boot["status"] == "success"
        
        res_diag = await deployment_diagnostics()
        data_diag = json.loads(res_diag)
        assert data_diag["status"] == "success"
        assert "test_cap" in data_diag["diagnostics"]["active_capabilities"]
