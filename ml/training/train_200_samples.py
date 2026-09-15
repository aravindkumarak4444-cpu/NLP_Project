import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any, List
import pandas as pd
import numpy as np

# Ensure project root is in sys.path
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

# Add backend directory to sys.path
backend_dir = os.path.join(base_dir, "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from ml.data.loader import DatasetLoader
from ml.data.cleaner import DatasetCleaner
from ml.data.validator import DatasetValidator
from ml.data.splitter import DatasetSplitter
from ml.models.baseline import BaselineMLModel
from ml.training.evaluator import ModelEvaluator
from ml.registry.model_registry import ModelRegistry
from app.integrations.ai_adapter import AIAdapter
from app.services.risk_service import RiskService

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s")
logger = logging.getLogger("sif_ml_200_samples")


def execute_200_sample_pipeline():
    """
    Executes the 200-sample dataset training & evaluation pipeline (80% train / 20% test).
    Classifies danger levels (LOW, MEDIUM, HIGH/CRITICAL) and prints detailed predictions.
    """
    dataset_path = os.path.join(base_dir, "data/sample/sif_200_dataset.csv")
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found at {dataset_path}")

    # 1. Load 200 sample dataset
    df_raw, meta = DatasetLoader.load_from_file(dataset_path)
    logger.info(f"Loaded 200-sample dataset: {len(df_raw)} records.")

    # 2. Clean dataset
    df_clean, clean_stats = DatasetCleaner.clean_dataset(df_raw)

    # 3. Validate dataset
    validation = DatasetValidator.validate_dataset(df_clean)
    if not validation["is_valid"]:
        raise ValueError(f"Dataset validation failed: {validation['errors']}")

    # 4. Split dataset into 80% Train (160) and 20% Test (40)
    train_df, _, test_df = DatasetSplitter.split_dataset(df_clean, test_size=0.2, random_state=42)
    logger.info(f"Train/Test Split Complete: Train = {len(train_df)} reports (80%), Test = {len(test_df)} reports (20%)")

    # 5. Train Baseline ML Model on 160 Training Samples
    baseline_model = BaselineMLModel(classifier_type="logistic")
    train_info = baseline_model.train(train_df["description"], train_df["sif_potential"])

    # Save trained baseline model to ai_model/model directory
    model_dir = os.path.join(base_dir, "ai_model/model")
    model_path, vec_path = baseline_model.save(model_dir)

    # 6. Evaluate Model on 40 Test Samples using AIAdapter and RiskService
    adapter = AIAdapter()
    risk_service = RiskService()

    predictions_list = []
    y_true_sif = test_df["sif_potential"].values.tolist()
    y_pred_sif = []

    for idx, row in test_df.reset_index(drop=True).iterrows():
        rep_id = row["report_id"]
        text = row["description"]
        actual_risk = row.get("risk_level", "UNKNOWN")
        actual_sif = int(row["sif_potential"])

        # Execute AI/NLP Analysis & Risk Evaluation
        res = adapter.analyze(text)
        risk = risk_service.calculate_risk(res)

        pred_sif_bool = res.sif_precursor
        pred_sif_int = 1 if pred_sif_bool else 0
        y_pred_sif.append(pred_sif_int)

        pred_risk_level = risk.level.value  # LOW, MEDIUM, HIGH, CRITICAL

        predictions_list.append({
            "test_index": idx + 1,
            "report_id": rep_id,
            "description": text,
            "actual_sif": actual_sif,
            "predicted_sif": pred_sif_bool,
            "actual_risk": actual_risk,
            "predicted_risk": pred_risk_level,
            "context_type": res.context_type,
            "raw_prediction": res.raw_prediction,
            "confidence": res.confidence,
            "hazard_category": res.hazard_category,
            "unsafe_act": res.unsafe_act or "None",
            "adjustment_reason": res.context_adjustment_reason or "N/A"
        })

    # 7. Calculate Evaluation Metrics
    metrics = ModelEvaluator.evaluate_predictions(y_true_sif, y_pred_sif)

    # Risk level classification statistics on test set
    risk_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for p in predictions_list:
        lvl = p["predicted_risk"]
        risk_counts[lvl] = risk_counts.get(lvl, 0) + 1

    # 8. Register in ModelRegistry
    version_id = f"MOD-200SAMPLES-{int(datetime.now().timestamp())}"
    registry = ModelRegistry()
    registry.register_model_version({
        "model_id": version_id,
        "model_name": "TF-IDF + Logistic Regression (200 Samples 80/20 Split)",
        "model_type": "BASELINE_ML",
        "version": "2.0.0",
        "dataset_version": "sif_200_dataset.csv",
        "training_date": datetime.now().isoformat(),
        "metrics": metrics,
        "status": "ACTIVE",
        "artifact_path": os.path.relpath(model_path, base_dir).replace("\\", "/"),
        "description": f"Trained on {len(train_df)} samples (80%), tested on {len(test_df)} samples (20%)."
    })

    # 9. Format and Print Structured Performance & Prediction Summary
    print("\n" + "=" * 80)
    print("      SIH26165 AI/NLP ENGINE — 200 SAMPLE DATASET (80/20 SPLIT) REPORT      ")
    print("=" * 80)
    print(f"Total Dataset Size : 200 Reports")
    print(f"Training Set (80%) : {len(train_df)} Reports")
    print(f"Test Set (20%)     : {len(test_df)} Reports")
    print(f"Active Model ID    : {version_id}")
    print("-" * 80)
    print("MODEL EVALUATION METRICS ON 40 TEST SAMPLES:")
    print(f"  * Accuracy        : {metrics['accuracy'] * 100:.2f}%")
    print(f"  * Precision       : {metrics['precision'] * 100:.2f}%")
    print(f"  * Recall          : {metrics['recall'] * 100:.2f}%")
    print(f"  * F1-Score        : {metrics['f1'] * 100:.2f}%")
    print(f"  * Macro F1-Score  : {metrics['macro_f1'] * 100:.2f}%")
    print(f"  * Confusion Matrix: TP={metrics['confusion_matrix'][1][1]}, FP={metrics['confusion_matrix'][0][1]}, TN={metrics['confusion_matrix'][0][0]}, FN={metrics['confusion_matrix'][1][0]}")
    print("-" * 80)
    print("PREDICTED DANGER RISK LEVEL BREAKDOWN (40 TEST SAMPLES):")
    print(f"  * LOW Danger (Safe/Prevented/Minor) : {risk_counts['LOW']} reports")
    print(f"  * MEDIUM Danger (Unsafe Condition)  : {risk_counts['MEDIUM']} reports")
    print(f"  * HIGH Danger (Precursor / Hazard)  : {risk_counts['HIGH']} reports")
    print(f"  * CRITICAL Danger (Severe Precursor): {risk_counts['CRITICAL']} reports")
    print("-" * 80)
    print("DETAILED TEST SET PREDICTIONS (40 TEST SAMPLES):\n")

    for p in predictions_list:
        status_symbol = "[DANGER - SIF PRECURSOR]" if p["predicted_sif"] else "[SAFE / LOW RISK]"
        print(f"[{p['test_index']:02d}/40] Report ID: {p['report_id']} | Actual SIF: {p['actual_sif']} | Predicted SIF: {p['predicted_sif']} {status_symbol}")
        print(f"     Description: \"{p['description']}\"")
        print(f"     Context Type: {p['context_type']} | Raw ML SIF: {p['raw_prediction']} | Conf: {p['confidence']}")
        print(f"     Danger Classification: Actual={p['actual_risk']} ==> PREDICTED DANGER={p['predicted_risk']}")
        print(f"     Unsafe Act: {p['unsafe_act']} | Hazard Category: {p['hazard_category']}")
        print(f"     Reason: {p['adjustment_reason']}")
        print("     " + "-" * 75)

    print("=" * 80)
    print("PIPELINE EXECUTION COMPLETE & MODEL SUCCESSFULLY REGISTERED")
    print("=" * 80 + "\n")

    return {
        "status": "SUCCESS",
        "model_id": version_id,
        "metrics": metrics,
        "test_predictions": predictions_list,
        "train_count": len(train_df),
        "test_count": len(test_df)
    }


if __name__ == "__main__":
    execute_200_sample_pipeline()
