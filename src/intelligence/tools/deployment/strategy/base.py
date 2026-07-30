from abc import ABC, abstractmethod
from ..schema import ValidationResult, ConfigurationProfile

class ValidationStrategy(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def validate(self) -> ValidationResult:
        """Run validation rules against targets."""
        pass

class ConfigMigrationStrategy(ABC):
    @abstractmethod
    def migrate(self, profile: ConfigurationProfile) -> ConfigurationProfile:
        """Upgrade configuration profile structure to the current version."""
        pass

class RollbackStrategy(ABC):
    @abstractmethod
    def execute_rollback(self) -> bool:
        """Roll back system configurations to the last successful release."""
        pass
