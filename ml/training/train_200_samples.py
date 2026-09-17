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
    Executes the 200-sample dataset training & evaluation pipeline:
    - Loads 200 sample O&G safety reports (100 SIF_PRECURSOR / 100 NON_SIF_PRECURSOR).
    - Checks duplicates, missing values, and data leakage.
    - Performs 80% Train (160) / 20% Test (40) stratified split (random_state=42).
    - Trains TF-IDF + Logistic Regression model on 160 training samples.
    - Evaluates on 40 untouched test samples.
    - Saves model artifacts & evaluation metrics.
    - Registers model as CANDIDATE / ACTIVE in ModelRegistry.
    """
    dataset_path = os.path.join(base_dir, "data/sample/sif_200_dataset.csv")
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found at {dataset_path}")

    # 1. Load 200 sample dataset
    df_raw, meta = DatasetLoader.load_from_file(dataset_path)
    logger.info(f"Loaded 200-sample dataset: {len(df_raw)} records.")

    # Data Quality & Leakage Checks
    duplicate_count = df_raw["description"].duplicated().sum()
    missing_values_count = df_raw.isnull().sum().sum()
    logger.info(f"Data Quality Check: Duplicates={duplicate_count}, Missing Values={missing_values_count}")

    # 2. Clean dataset
    df_clean, clean_stats = DatasetCleaner.clean_dataset(df_raw)

    # 3. Validate dataset
    validation = DatasetValidator.validate_dataset(df_clean)
    if not validation["is_valid"]:
        raise ValueError(f"Dataset validation failed: {validation['errors']}")

    # 4. Stratified Split: 80% Train (160) / 20% Test (40)
    train_df, _, test_df = DatasetSplitter.split_dataset(df_clean, test_size=0.2, random_state=42)
    logger.info(f"Train/Test Split: Train = {len(train_df)} reports (80%), Test = {len(test_df)} reports (20%)")

    # Data Leakage Verification
    train_descs = set(train_df["description"].str.strip().str.lower())
    test_descs = set(test_df["description"].str.strip().str.lower())
    leakage_count = len(train_descs.intersection(test_descs))
    if leakage_count > 0:
        raise ValueError(f"Data leakage detected! {leakage_count} test descriptions found in training set.")
    logger.info("Data Leakage Check: NONE (0 overlapping test descriptions in training set).")

    # 5. Train Baseline ML Model (TF-IDF + Logistic Regression) on 160 Training Samples
    baseline_model = BaselineMLModel(classifier_type="logistic")
    train_info = baseline_model.train(train_df["description"], train_df["sif_potential"])

    # Save trained model to both ai_model/model and backend/ai_model/model
    model_dir = os.path.join(base_dir, "ai_model/model")
    backend_model_dir = os.path.join(base_dir, "backend/ai_model/model")
    model_path, vec_path = baseline_model.save(model_dir)
    baseline_model.save(backend_model_dir)

    # 6. Evaluate Model on 40 Untouched Test Samples using AIAdapter & RiskService
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
        actual_label = "SIF_PRECURSOR" if actual_sif == 1 else "NON_SIF_PRECURSOR"

        # Execute AI/NLP Analysis & Risk Evaluation
        res = adapter.analyze(text)
        risk = risk_service.calculate_risk(res)

        pred_sif_bool = res.sif_precursor
        pred_sif_int = 1 if pred_sif_bool else 0
        pred_label = "SIF_PRECURSOR" if pred_sif_bool else "NON_SIF_PRECURSOR"
        y_pred_sif.append(pred_sif_int)

        pred_risk_level = risk.level.value  # LOW, MEDIUM, HIGH, CRITICAL
        is_correct = (pred_sif_int == actual_sif)

        predictions_list.append({
            "test_index": idx + 1,
            "report_id": rep_id,
            "description": text,
            "actual_sif": actual_sif,
            "actual_label": actual_label,
            "predicted_sif": pred_sif_int,
            "predicted_label": pred_label,
            "correct": is_correct,
            "actual_risk": actual_risk,
            "predicted_risk": pred_risk_level,
            "context_type": res.context_type,
            "raw_prediction": int(res.raw_prediction) if isinstance(res.raw_prediction, (bool, np.bool_)) else res.raw_prediction,
            "confidence": res.confidence,
            "hazard_category": res.hazard_category,
            "unsafe_act": res.unsafe_act or "None",
            "adjustment_reason": res.context_adjustment_reason or "N/A"
        })

    # 7. Calculate Evaluation Metrics & Confusion Matrix
    metrics = ModelEvaluator.evaluate_predictions(y_true_sif, y_pred_sif)

    # Calculate specific SIF_PRECURSOR class metrics
    cm = metrics["confusion_matrix"]  # [[TN, FP], [FN, TP]]
    tn, fp, fn, tp = cm[0][0], cm[0][1], cm[1][0], cm[1][1]

    sif_precision = round(tp / (tp + fp), 4) if (tp + fp) > 0 else 0.0
    sif_recall = round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0.0
    sif_f1 = round(2 * sif_precision * sif_recall / (sif_precision + sif_recall), 4) if (sif_precision + sif_recall) > 0 else 0.0

    # Save test predictions to CSV
    results_dir = os.path.join(base_dir, "data/results")
    os.makedirs(results_dir, exist_ok=True)
    results_csv_path = os.path.join(results_dir, "test_predictions_200.csv")
    pd.DataFrame(predictions_list).to_csv(results_csv_path, index=False)
    logger.info(f"Saved 40 test set predictions to {results_csv_path}")

    # 8. Register Candidate/Active Model in ModelRegistry
    version_id = f"MOD-200SAMPLES-{int(datetime.now().timestamp())}"
    registry = ModelRegistry()
    registry.register_model_version({
        "model_id": version_id,
        "model_name": "TF-IDF + Logistic Regression — 200 Sample Baseline",
        "model_type": "BASELINE_ML",
        "version": "2.0.0",
        "dataset_version": "sif_200_dataset.csv",
        "training_date": datetime.now().isoformat(),
        "metrics": metrics,
        "sif_precursor_metrics": {
            "precision": sif_precision,
            "recall": sif_recall,
            "f1": sif_f1
        },
        "status": "CANDIDATE",
        "artifact_path": os.path.relpath(model_path, base_dir).replace("\\", "/"),
        "description": f"Trained on {len(train_df)} samples (80%), tested on {len(test_df)} samples (20%)."
    })

    # Activate model after validation and evaluation
    registry.activate_model(version_id)


    # 9. Format & Output Complete Technical Summary
    print("\n" + "=" * 80)
    print("      SIH26165 AI/NLP ENGINE — 200 SAMPLE DATASET EVALUATION REPORT      ")
    print("=" * 80)
    print(f"Dataset Path        : data/sample/sif_200_dataset.csv")
    print(f"Total Dataset Size  : {len(df_clean)} Reports (100 SIF_PRECURSOR / 100 NON_SIF_PRECURSOR)")
    print(f"Training Set (80%)  : {len(train_df)} Reports")
    print(f"Test Set (20%)      : {len(test_df)} Reports")
    print(f"Duplicates / Missing: Duplicates={duplicate_count}, Missing={missing_values_count}")
    print(f"Data Leakage        : NONE (0 overlapping test descriptions in training set)")
    print(f"Registered Model ID : {version_id} (Status: CANDIDATE -> ACTIVE)")
    print("-" * 80)
    print("MODEL EVALUATION METRICS ON 40 UNTOUCHED TEST SAMPLES:")
    print(f"  * Accuracy         : {metrics['accuracy'] * 100:.2f}%")
    print(f"  * Overall Precision: {metrics['precision'] * 100:.2f}%")
    print(f"  * Overall Recall   : {metrics['recall'] * 100:.2f}%")
    print(f"  * Overall F1-Score : {metrics['f1'] * 100:.2f}%")
    print(f"  * Macro F1-Score   : {metrics['macro_f1'] * 100:.2f}%")
    print("-" * 80)
    print("CONFUSION MATRIX ON 40 TEST SAMPLES:")
    print(f"  * True Negatives  (TN) : {tn}")
    print(f"  * False Positives (FP) : {fp}")
    print(f"  * False Negatives (FN) : {fn}")
    print(f"  * True Positives  (TP) : {tp}")
    print("-" * 80)
    print("SIF_PRECURSOR CLASS SPECIFIC METRICS:")
    print(f"  * SIF Precision    : {sif_precision * 100:.2f}%")
    print(f"  * SIF Recall       : {sif_recall * 100:.2f}%")
    print(f"  * SIF F1-Score     : {sif_f1 * 100:.2f}%")
    print("-" * 80)
    print("DETAILED 40 TEST SET PREDICTIONS:\n")

    for p in predictions_list:
        match_str = "CORRECT" if p["correct"] else "INCORRECT (MISCLASSIFIED)"
        tag = "[SIF PRECURSOR]" if p["predicted_sif"] else "[NON SIF PRECURSOR]"
        print(f"[{p['test_index']:02d}/40] ID: {p['report_id']} | Actual: {p['actual_label']} | Pred: {p['predicted_label']} {tag} | Result: {match_str}")
        print(f"     Description: \"{p['description']}\"")
        print(f"     Context Type: {p['context_type']} | Raw ML SIF: {p['raw_prediction']} | Conf: {p['confidence']}")
        print(f"     Danger Level: Actual={p['actual_risk']} ==> Pred={p['predicted_risk']}")
        print(f"     Reason: {p['adjustment_reason']}")
        print("     " + "-" * 75)

    print("=" * 80)
    print("PIPELINE EXECUTION COMPLETE")
    print("=" * 80 + "\n")

    return {
        "status": "SUCCESS",
        "model_id": version_id,
        "metrics": metrics,
        "sif_metrics": {
            "precision": sif_precision,
            "recall": sif_recall,
            "f1": sif_f1
        },
        "confusion_matrix": {"TN": tn, "FP": fp, "FN": fn, "TP": tp},
        "test_predictions": predictions_list,
        "train_count": len(train_df),
        "test_count": len(test_df),
        "leakage": "NONE",
        "duplicates": duplicate_count,
        "missing_values": missing_values_count
    }


if __name__ == "__main__":
    execute_200_sample_pipeline()
