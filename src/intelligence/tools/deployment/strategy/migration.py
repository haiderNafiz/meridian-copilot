from .base import ConfigMigrationStrategy
from ..schema import ConfigurationProfile

class DefaultConfigMigrationStrategy(ConfigMigrationStrategy):
    def migrate(self, profile: ConfigurationProfile) -> ConfigurationProfile:
        profile.version = "v3.0.0"
        return profile
