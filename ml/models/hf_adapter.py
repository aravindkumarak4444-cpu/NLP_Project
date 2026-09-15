import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("sif_ml")

class HuggingFaceAdapter:
    """
    Real Hugging Face Transformers Adapter for SIF Precursor Detection.
    Attempts to load Hugging Face pipeline/model specified by HF_MODEL_NAME.
    Gracefully handles missing packages, network failures, or download errors.
    """

    def __init__(self, model_name_or_path: Optional[str] = None):
        self.model_name = model_name_or_path or os.getenv("HF_MODEL_NAME", "distilbert-base-uncased-finetuned-sst-2-english")
        self.pipeline = None
        self.load_error: Optional[str] = None
        self._initialize_pipeline()

    def _initialize_pipeline(self):
        try:
            from transformers import pipeline
            logger.info(f"Attempting to load Hugging Face pipeline for '{self.model_name}'...")
            self.pipeline = pipeline("text-classification", model=self.model_name, return_all_scores=True)
            logger.info(f"Hugging Face Transformer pipeline '{self.model_name}' initialized successfully.")
        except Exception as e:
            self.load_error = f"Hugging Face Transformer load warning: {str(e)}"
            logger.warning(self.load_error)

    def is_available(self) -> bool:
        return self.pipeline is not None and self.load_error is None

    def predict(self, text: str) -> Dict[str, Any]:
        """
        Executes Hugging Face Transformer model inference on input text.
        """
        if not self.is_available():
            raise RuntimeError(self.load_error or "Hugging Face Transformer pipeline is not available.")

        try:
            raw_scores = self.pipeline(text[0:512])[0]
            # Map score output
            top_pred = max(raw_scores, key=lambda x: x["score"])
            label_upper = str(top_pred["label"]).upper()
            score = float(top_pred["score"])

            is_sif = label_upper in ["NEGATIVE", "LABEL_1", "SIF", "PRECURSOR", "RISK", "DANGER"]

            return {
                "sif_precursor": is_sif,
                "confidence": round(score, 2),
                "hazard_category": "UNCLASSIFIED_TRANSFORMER",
                "evidence": [f"HuggingFace {self.model_name} prediction: label={top_pred['label']}, score={score:.2f}"],
                "model_source": "HUGGINGFACE",
                "hf_model_name": self.model_name,
            }
        except Exception as e:
            logger.error(f"Error during Hugging Face inference: {str(e)}", exc_info=True)
            raise RuntimeError(f"Hugging Face inference error: {str(e)}")

    def get_info(self) -> Dict[str, Any]:
        return {
            "mode": "HUGGINGFACE",
            "model_name": self.model_name,
            "model_loaded": self.is_available(),
            "reason": self.load_error if not self.is_available() else None,
        }
