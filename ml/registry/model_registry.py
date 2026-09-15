import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger("sif_ml")

REGISTRY_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "registry.json"))


class ModelRegistry:
    """
    Model Registry for Version Management, Model Comparisons, and Active Status Tracking.
    """

    def __init__(self, registry_file: Optional[str] = None):
        self.file_path = registry_file or REGISTRY_FILE_PATH
        self._ensure_registry_file()

    def _ensure_registry_file(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            initial_registry = {
                "active_model_id": "MOD-BASELINE-V1",
                "models": [
                    {
                        "model_id": "MOD-BASELINE-V1",
                        "model_name": "TF-IDF + Logistic Regression Baseline",
                        "model_type": "BASELINE_ML",
                        "version": "1.0.0",
                        "dataset_version": "SAMPLE-V1",
                        "training_date": datetime.now().isoformat(),
                        "metrics": {
                            "accuracy": 0.92,
                            "precision": 0.90,
                            "recall": 0.95,
                            "f1": 0.92,
                            "macro_f1": 0.92,
                            "weighted_f1": 0.92,
                        },
                        "status": "ACTIVE",
                        "artifact_path": "ai_model/model/sif_classifier.pkl",
                        "description": "Baseline TF-IDF Logistic Regression Model"
                    }
                ]
            }
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(initial_registry, f, indent=2)

    def load_registry(self) -> Dict[str, Any]:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading registry file '{self.file_path}': {str(e)}")
            return {"active_model_id": "MOD-BASELINE-V1", "models": []}

    def save_registry(self, data: Dict[str, Any]):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def register_model_version(self, model_info: Dict[str, Any]) -> Dict[str, Any]:
        registry = self.load_registry()

        model_id = model_info.get("model_id", f"MOD-{int(datetime.now().timestamp())}")
        model_entry = {
            "model_id": model_id,
            "model_name": model_info.get("model_name", "SIF Classifier"),
            "model_type": model_info.get("model_type", "BASELINE_ML"),
            "version": model_info.get("version", "1.0.0"),
            "dataset_version": model_info.get("dataset_version", "1.0.0"),
            "training_date": model_info.get("training_date", datetime.now().isoformat()),
            "metrics": model_info.get("metrics", {}),
            "status": model_info.get("status", "INACTIVE"),
            "artifact_path": model_info.get("artifact_path", ""),
            "description": model_info.get("description", "")
        }

        # Check if model_id exists and update
        existing = [m for m in registry["models"] if m["model_id"] == model_id]
        if existing:
            registry["models"] = [m if m["model_id"] != model_id else model_entry for m in registry["models"]]
        else:
            registry["models"].append(model_entry)

        if model_entry["status"] == "ACTIVE":
            registry["active_model_id"] = model_id
            for m in registry["models"]:
                if m["model_id"] != model_id:
                    m["status"] = "INACTIVE"

        self.save_registry(registry)
        logger.info(f"Registered model version '{model_id}' (Status: {model_entry['status']})")
        return model_entry

    def activate_model(self, model_id: str) -> bool:
        registry = self.load_registry()
        found = False
        for m in registry["models"]:
            if m["model_id"] == model_id:
                m["status"] = "ACTIVE"
                registry["active_model_id"] = model_id
                found = True
            else:
                m["status"] = "INACTIVE"

        if found:
            self.save_registry(registry)
            logger.info(f"Activated model ID '{model_id}'")
            return True
        return False

    def get_active_model_info(self) -> Optional[Dict[str, Any]]:
        registry = self.load_registry()
        active_id = registry.get("active_model_id")
        for m in registry["models"]:
            if m["model_id"] == active_id:
                return m
        return registry["models"][0] if registry["models"] else None

    def list_models(self) -> List[Dict[str, Any]]:
        return self.load_registry().get("models", [])
