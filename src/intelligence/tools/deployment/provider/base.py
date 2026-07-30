from abc import ABC, abstractmethod
from typing import Optional
from ..schema import ConfigurationProfile, DeploymentManifest

class DeploymentStorageProvider(ABC):
    @abstractmethod
    def save_profile(self, profile: ConfigurationProfile) -> None: pass
    
    @abstractmethod
    def load_profile(self, profile_id: str) -> Optional[ConfigurationProfile]: pass

    @abstractmethod
    def save_manifest(self, manifest: DeploymentManifest) -> None: pass

    @abstractmethod
    def load_manifest(self, manifest_id: str) -> Optional[DeploymentManifest]: pass
