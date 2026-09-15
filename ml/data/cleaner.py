import re
import logging
import pandas as pd
from typing import Tuple, Dict, Any

logger = logging.getLogger("sif_ml")


class DatasetCleaner:
    """
    Data cleaning and normalization utility for safety report datasets.
    """

    @staticmethod
    def clean_dataset(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Cleans dataset DataFrame by:
        1. Normalizing column names to lowercase.
        2. Mapping label column ('sif_precursor', 'label', 'is_sif' -> 'sif_potential').
        3. Removing rows with missing description or label.
        4. Removing duplicate report descriptions.
        5. Cleaning whitespace in text fields.

        Returns (cleaned_df, cleaning_stats).
        """
        initial_count = len(df)
        df_clean = df.copy()

        # 1. Normalize column names
        df_clean.columns = [str(c).strip().lower() for c in df_clean.columns]

        # 2. Standardize description column name
        desc_col = None
        for candidate in ["description", "report_text", "text", "report_description"]:
            if candidate in df_clean.columns:
                desc_col = candidate
                break

        if not desc_col:
            raise ValueError("Dataset missing required text column. Expected one of: ['description', 'report_text', 'text']")

        if desc_col != "description":
            df_clean = df_clean.rename(columns={desc_col: "description"})

        # 3. Standardize label column name
        label_col = None
        for candidate in ["sif_potential", "sif_precursor", "is_sif", "sif", "label"]:
            if candidate in df_clean.columns:
                label_col = candidate
                break

        if not label_col:
            raise ValueError("Dataset missing required label column. Expected one of: ['sif_potential', 'sif_precursor', 'is_sif', 'label']")

        if label_col != "sif_potential":
            df_clean = df_clean.rename(columns={label_col: "sif_potential"})

        # 4. Convert label values to binary int (0 or 1)
        def parse_binary_label(val):
            if pd.isna(val):
                return None
            if isinstance(val, (int, float)):
                return 1 if val > 0 else 0
            val_str = str(val).strip().upper()
            if val_str in ["1", "TRUE", "SIF", "PRECURSOR", "YES"]:
                return 1
            if val_str in ["0", "FALSE", "NON-SIF", "NORMAL", "NO"]:
                return 0
            return None

        df_clean["sif_potential"] = df_clean["sif_potential"].apply(parse_binary_label)

        # 5. Drop rows with null description or null label
        null_desc_count = df_clean["description"].isna().sum()
        null_label_count = df_clean["sif_potential"].isna().sum()
        df_clean = df_clean.dropna(subset=["description", "sif_potential"])

        # 6. Clean text strings (strip whitespace, normalize spaces)
        df_clean["description"] = df_clean["description"].astype(str).apply(
            lambda s: re.sub(r"\s+", " ", s.strip())
        )

        # Drop descriptions under 5 characters
        df_clean = df_clean[df_clean["description"].str.len() >= 5]

        # 7. Remove duplicate text rows
        duplicates_count = df_clean.duplicated(subset=["description"]).sum()
        df_clean = df_clean.drop_duplicates(subset=["description"], keep="first")

        final_count = len(df_clean)

        stats = {
            "initial_rows": initial_count,
            "final_rows": final_count,
            "removed_rows": initial_count - final_count,
            "null_descriptions_removed": int(null_desc_count),
            "null_labels_removed": int(null_label_count),
            "duplicates_removed": int(duplicates_count),
            "sif_positive_count": int((df_clean["sif_potential"] == 1).sum()),
            "sif_negative_count": int((df_clean["sif_potential"] == 0).sum()),
        }

        logger.info(f"Cleaned dataset: {initial_count} -> {final_count} rows. Stats: {stats}")
        return df_clean, stats
