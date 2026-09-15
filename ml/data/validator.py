import logging
import pandas as pd
from typing import Dict, Any, List

logger = logging.getLogger("sif_ml")


class DatasetValidator:
    """
    Validation checks for dataset integrity prior to model training.
    """

    @staticmethod
    def validate_dataset(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validates DataFrame structure, row count, label representation, and text quality.
        Returns a validation report dict.
        """
        errors: List[str] = []
        warnings: List[str] = []

        if df.empty:
            errors.append("Dataset is empty.")
            return {"is_valid": False, "errors": errors, "warnings": warnings}

        if "description" not in df.columns:
            errors.append("Missing required 'description' column.")
        if "sif_potential" not in df.columns:
            errors.append("Missing required 'sif_potential' label column.")

        if errors:
            return {"is_valid": False, "errors": errors, "warnings": warnings}

        row_count = len(df)
        if row_count < 5:
            warnings.append(f"Small dataset size ({row_count} rows). Model training may overfit.")

        unique_labels = df["sif_potential"].unique()
        if len(unique_labels) < 2:
            errors.append(f"Dataset contains only 1 class label ({unique_labels}). Must contain both SIF (1) and Non-SIF (0) examples.")

        sif_pos = (df["sif_potential"] == 1).sum()
        sif_neg = (df["sif_potential"] == 0).sum()

        if sif_pos == 0:
            errors.append("Dataset has zero SIF precursor positive examples (1).")
        if sif_neg == 0:
            errors.append("Dataset has zero SIF precursor negative examples (0).")

        imbalance_ratio = round(max(sif_pos, sif_neg) / max(1, min(sif_pos, sif_neg)), 2)
        if imbalance_ratio > 5.0:
            warnings.append(f"Class imbalance detected (Ratio {imbalance_ratio}:1). Consider using class weighting or resampling.")

        avg_desc_len = round(df["description"].str.len().mean(), 1)

        is_valid = len(errors) == 0

        validation_result = {
            "is_valid": is_valid,
            "row_count": row_count,
            "sif_positive_count": int(sif_pos),
            "sif_negative_count": int(sif_neg),
            "class_imbalance_ratio": imbalance_ratio,
            "avg_description_length": avg_desc_len,
            "errors": errors,
            "warnings": warnings,
        }

        logger.info(f"Dataset validation complete: is_valid={is_valid}, errors={len(errors)}, warnings={len(warnings)}")
        return validation_result
