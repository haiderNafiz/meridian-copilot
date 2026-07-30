import os
import json
from typing import Optional
from .base import DeploymentStorageProvider
from ..schema import ConfigurationProfile, DeploymentManifest

class LocalFilesystemDeploymentStorageProvider(DeploymentStorageProvider):
    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            self.base_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../../../../../deployment_platform")
            )
        else:
            self.base_dir = os.path.abspath(base_dir)

        os.makedirs(self.base_dir, exist_ok=True)
        self.profiles_file = os.path.join(self.base_dir, "profiles.jsonl")
        self.manifests_file = os.path.join(self.base_dir, "manifests.jsonl")

    def save_profile(self, profile: ConfigurationProfile) -> None:
        self._append_jsonl(self.profiles_file, profile.model_dump())

    def load_profile(self, profile_id: str) -> Optional[ConfigurationProfile]:
        data = self._read_jsonl(self.profiles_file)
        for item in reversed(data):
            if item.get("profile_id") == profile_id:
                return ConfigurationProfile.model_validate(item)
        return None

    def save_manifest(self, manifest: DeploymentManifest) -> None:
        self._append_jsonl(self.manifests_file, manifest.model_dump())

    def load_manifest(self, manifest_id: str) -> Optional[DeploymentManifest]:
        data = self._read_jsonl(self.manifests_file)
        for item in reversed(data):
            if item.get("manifest_id") == manifest_id:
                return DeploymentManifest.model_validate(item)
        return None

    def _append_jsonl(self, filepath: str, data: dict) -> None:
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")

    def _read_jsonl(self, filepath: str) -> list:
        if not os.path.exists(filepath):
            return []
        items = []
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line_str = line.strip()
                if line_str:
                    try:
                        items.append(json.loads(line_str))
                    except Exception:
                        pass
        return items
