import os
import json
import logging
from typing import List, Dict, Any, Tuple, Optional
import pandas as pd

logger = logging.getLogger("sif_ml")

REQUIRED_COLUMNS = ["description", "sif_potential"]


class DatasetLoader:
    """
    Data ingestion loader for CSV, JSON, and XLSX safety report datasets.
    """

    @staticmethod
    def load_from_file(file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Loads dataset from file path, validating file extension and reading content into pandas DataFrame.
        Returns (DataFrame, metadata_dict).
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Dataset file not found at '{file_path}'")

        ext = os.path.splitext(file_path)[1].lower()
        metadata = {
            "file_name": os.path.basename(file_path),
            "file_size_bytes": os.path.getsize(file_path),
            "format": ext.replace(".", "").upper(),
        }

        try:
            if ext == ".csv":
                df = pd.read_csv(file_path)
            elif ext == ".json":
                df = pd.read_json(file_path)
            elif ext in [".xlsx", ".xls"]:
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported dataset format '{ext}'. Supported formats: .csv, .json, .xlsx")

            logger.info(f"Loaded dataset '{metadata['file_name']}' with {len(df)} rows.")
            return df, metadata
        except Exception as e:
            logger.error(f"Error reading dataset file '{file_path}': {str(e)}", exc_info=True)
            raise RuntimeError(f"Failed to parse dataset file: {str(e)}")

    @staticmethod
    def load_sample_dataset() -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Loads sample reports dataset from data/sample/sample_reports.csv if available.
        """
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        sample_path = os.path.join(base_dir, "data/sample/sample_reports.csv")

        if os.path.exists(sample_path):
            df, meta = DatasetLoader.load_from_file(sample_path)
            meta["is_demo"] = True
            meta["label_notice"] = "DEMO SAMPLE DATASET"
            return df, meta

        # Fallback inline sample dataset if file not found
        demo_records = [
            {"report_id": "DEMO-001", "description": "Worker entered confined space vessel without gas testing prior to entry.", "sif_potential": 1, "department": "Operations", "location": "Plant Area A"},
            {"report_id": "DEMO-002", "description": "Tripped on an extension cord in the office hallway, no injury incurred.", "sif_potential": 0, "department": "Administration", "location": "Main Office"},
            {"report_id": "DEMO-003", "description": "Technician working on elevated scaffold at 8 meters without fall arrest harness.", "sif_potential": 1, "department": "Maintenance", "location": "Rig 12"},
            {"report_id": "DEMO-004", "description": "Hot work welding performed near flammable crude storage without hot work permit or fire watch.", "sif_potential": 1, "department": "Drilling", "location": "Refinery Tank 4"},
            {"report_id": "DEMO-005", "description": "Spilled coffee on breakroom counter during lunch hour.", "sif_potential": 0, "department": "Services", "location": "Cafeteria"},
            {"report_id": "DEMO-006", "description": "Live high-voltage conductor exposed in electrical substation without LOTO lockout tagout.", "sif_potential": 1, "department": "Electrical", "location": "Substation 2"},
            {"report_id": "DEMO-007", "description": "Crane sling snapped during heavy pipe lift, suspended load swung overhead.", "sif_potential": 1, "department": "Logistics", "location": "Pipe Yard"},
            {"report_id": "DEMO-008", "description": "Minor paper cut while printing safety documentation.", "sif_potential": 0, "department": "HSE", "location": "Office"},
        ]
        df = pd.DataFrame(demo_records)
        return df, {
            "file_name": "sample_reports_fallback.json",
            "file_size_bytes": len(json.dumps(demo_records)),
            "format": "INLINE_DEMO",
            "is_demo": True,
            "label_notice": "DEMO SAMPLE DATASET ONLY"
        }
