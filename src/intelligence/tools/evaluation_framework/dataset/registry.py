import os
import json
from typing import List, Dict, Any, Optional
from ..schema import EvaluationDataset, EvaluationItem, DatasetType

class DatasetRegistry:
    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            # Default to workspace relative 'datasets'
            self.base_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../../../../../datasets")
            )
        else:
            self.base_dir = os.path.abspath(base_dir)

    def resolve_path(self, domain: str, dataset_type: str, filename: str) -> str:
        """Resolve absolute path to a specific dataset file."""
        return os.path.join(self.base_dir, domain, dataset_type, filename)

    def load_dataset_file(self, file_path: str) -> EvaluationDataset:
        """Load and parse dataset schema from JSON or JSONL file path."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Dataset file not found at: {file_path}")
            
        if file_path.endswith(".jsonl"):
            items = []
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        items.append(json.loads(line))
            
            # Map parameters to create dataset object
            dataset_id = os.path.basename(file_path).replace(".jsonl", "")
            return EvaluationDataset(
                dataset_id=dataset_id,
                version="1.0.0",
                dataset_type=DatasetType.CURATED,
                items=[EvaluationItem.model_validate(x) for x in items]
            )
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
            return EvaluationDataset.model_validate(raw_data)

    def get_dataset(self, domain: str, dataset_type: str, version: str) -> EvaluationDataset:
        """Lookup dataset matching criteria inside the directory layout."""
        filename = f"{version}.json"
        path = self.resolve_path(domain, dataset_type, filename)
        if not os.path.exists(path):
            # Try JSONL fallback
            path = self.resolve_path(domain, dataset_type, f"{version}.jsonl")
            
        return self.load_dataset_file(path)

    def list_datasets(self) -> List[Dict[str, Any]]:
        """Scan registry directory structure and report available datasets."""
        results = []
        if not os.path.exists(self.base_dir):
            return results
            
        for domain in os.listdir(self.base_dir):
            domain_path = os.path.join(self.base_dir, domain)
            if not os.path.isdir(domain_path):
                continue
                
            for type_name in os.listdir(domain_path):
                type_path = os.path.join(domain_path, type_name)
                if not os.path.isdir(type_path):
                    continue
                    
                for file_name in os.listdir(type_path):
                    if file_name.endswith(".json") or file_name.endswith(".jsonl"):
                        version = file_name.rsplit(".", 1)[0]
                        results.append({
                            "domain": domain,
                            "dataset_type": type_name,
                            "version": version,
                            "path": os.path.join(type_path, file_name)
                        })
        return results
