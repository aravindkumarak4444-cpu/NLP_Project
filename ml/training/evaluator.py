import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

logger = logging.getLogger("sif_ml")


class ModelEvaluator:
    """
    Evaluator for classification metrics (Accuracy, Precision, Recall, F1, Macro F1, Weighted F1, Confusion Matrix).
    """

    @staticmethod
    def evaluate_predictions(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
        """
        Calculates classification evaluation metrics.
        Returns metrics dictionary.
        """
        if len(y_true) == 0 or len(y_pred) == 0:
            return {
                "insufficient_data": True,
                "message": "Insufficient labeled data for reliable evaluation.",
                "accuracy": 0.0,
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "macro_f1": 0.0,
                "weighted_f1": 0.0,
                "confusion_matrix": [[0, 0], [0, 0]],
            }

        acc = float(accuracy_score(y_true, y_pred))
        prec = float(precision_score(y_true, y_pred, zero_division=0))
        rec = float(recall_score(y_true, y_pred, zero_division=0))
        f1 = float(f1_score(y_true, y_pred, zero_division=0))
        macro_f1 = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
        weighted_f1 = float(f1_score(y_true, y_pred, average="weighted", zero_division=0))

        cm = confusion_matrix(y_true, y_pred).tolist()

        metrics = {
            "insufficient_data": False,
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "macro_f1": round(macro_f1, 4),
            "weighted_f1": round(weighted_f1, 4),
            "confusion_matrix": cm,
            "sample_count": int(len(y_true)),
        }

        logger.info(f"Evaluated predictions on {len(y_true)} samples: Accuracy={acc:.4f}, Recall={rec:.4f}, F1={f1:.4f}")
        return metrics
