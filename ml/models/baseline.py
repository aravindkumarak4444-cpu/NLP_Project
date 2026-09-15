import os
import logging
import joblib
import pandas as pd
from typing import Dict, Any, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from ml.data.preprocessing import TextPreprocessor

logger = logging.getLogger("sif_ml")


class BaselineMLModel:
    """
    TF-IDF Vectorizer + Logistic Regression / Linear SVM Classifier for SIF Precursor Detection.
    """

    def __init__(self, classifier_type: str = "logistic"):
        self.classifier_type = classifier_type.lower()
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=1,
            max_features=5000,
            lowercase=True
        )
        if self.classifier_type == "svm":
            self.model = SVC(probability=True, kernel="linear", random_state=42)
        else:
            self.model = LogisticRegression(C=1.0, max_iter=1000, random_state=42)

        self.is_trained = False

    def train(self, X_train: pd.Series, y_train: pd.Series) -> Dict[str, Any]:
        """
        Fits TF-IDF vectorizer and classifier on text data.
        Returns training metadata.
        """
        logger.info(f"Training BaselineMLModel ({self.classifier_type}) on {len(X_train)} samples...")
        X_clean = [TextPreprocessor.clean_text(t) for t in X_train]

        X_vec = self.vectorizer.fit_transform(X_clean)
        self.model.fit(X_vec, y_train)
        self.is_trained = True

        return {
            "model_type": f"TF-IDF + {self.classifier_type.upper()}",
            "vocabulary_size": len(self.vectorizer.vocabulary_),
            "training_sample_count": len(X_train),
        }

    def predict(self, text: str) -> Dict[str, Any]:
        """
        Predicts SIF precursor flag and probability confidence for input report text.
        """
        if not self.is_trained:
            raise RuntimeError("Model has not been trained yet.")

        clean_t = TextPreprocessor.clean_text(text)
        vec = self.vectorizer.transform([clean_t])

        pred_class = int(self.model.predict(vec)[0])

        probs = self.model.predict_proba(vec)[0] if hasattr(self.model, "predict_proba") else [0.5, 0.5]
        confidence = float(probs[pred_class])

        # Extract hazard category and evidence phrases using preprocessor
        extracted = TextPreprocessor.extract_negations_and_hazards(text)
        cats = extracted.get("matched_categories", [])
        primary_cat = cats[0] if cats else ("CONFINED_SPACE" if pred_class == 1 else "GENERAL_SAFETY")

        evidence = [f"Found category '{primary_cat}'"]
        if extracted.get("has_negation"):
            evidence.append(f"Detected safety negations: {', '.join(extracted['detected_negations'])}")

        return {
            "sif_precursor": bool(pred_class == 1),
            "confidence": round(confidence, 2),
            "hazard_category": primary_cat,
            "evidence": evidence,
            "model_source": "BASELINE_ML",
        }

    def save(self, model_dir: str) -> Tuple[str, str]:
        """
        Saves sif_classifier.pkl and tfidf_vectorizer.pkl into specified directory.
        """
        os.makedirs(model_dir, exist_ok=True)
        model_path = os.path.join(model_dir, "sif_classifier.pkl")
        vectorizer_path = os.path.join(model_dir, "tfidf_vectorizer.pkl")

        joblib.dump(self.model, model_path)
        joblib.dump(self.vectorizer, vectorizer_path)
        logger.info(f"Saved baseline model artifacts to {model_dir}")
        return model_path, vectorizer_path

    @classmethod
    def load(cls, model_path: str, vectorizer_path: str) -> "BaselineMLModel":
        """
        Loads baseline model instance from pickled artifact files.
        """
        instance = cls()
        instance.model = joblib.load(model_path)
        instance.vectorizer = joblib.load(vectorizer_path)
        instance.is_trained = True
        logger.info(f"Loaded BaselineMLModel from {model_path}")
        return instance
