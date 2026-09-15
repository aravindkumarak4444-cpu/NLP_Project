import logging
import pandas as pd
from typing import Tuple, Dict, Any
from sklearn.model_selection import train_test_split

logger = logging.getLogger("sif_ml")


class DatasetSplitter:
    """
    Stratified Dataset Train/Validation/Test Splitter.
    """

    @staticmethod
    def split_dataset(
        df: pd.DataFrame,
        test_size: float = 0.2,
        val_size: float = 0.0,
        random_state: int = 42
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Splits dataset into train_df, val_df (optional), and test_df using stratified sampling based on 'sif_potential'.
        Returns (train_df, val_df, test_df).
        """
        if df.empty or len(df) < 4:
            logger.warning("Dataset too small for train/test split. Returning dataset as train_df.")
            return df, pd.DataFrame(), pd.DataFrame()

        y = df["sif_potential"]

        # Stratified train/test split
        try:
            train_df, test_df = train_test_split(
                df,
                test_size=test_size,
                stratify=y,
                random_state=random_state
            )
        except Exception as e:
            logger.warning(f"Stratified split failed ({str(e)}). Falling back to unstratified split.")
            train_df, test_df = train_test_split(
                df,
                test_size=test_size,
                random_state=random_state
            )

        val_df = pd.DataFrame()
        if val_size > 0.0 and len(train_df) >= 4:
            try:
                train_df, val_df = train_test_split(
                    train_df,
                    test_size=val_size / (1.0 - test_size),
                    stratify=train_df["sif_potential"],
                    random_state=random_state
                )
            except Exception:
                train_df, val_df = train_test_split(
                    train_df,
                    test_size=val_size / (1.0 - test_size),
                    random_state=random_state
                )

        logger.info(f"Split dataset: Train={len(train_df)}, Val={len(val_df)}, Test={len(test_df)}")
        return train_df, val_df, test_df
