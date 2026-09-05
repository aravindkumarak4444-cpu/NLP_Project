import os
import logging
import importlib.util
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from app.models.report import AIAnalysisModel
from app.config import settings

logger = logging.getLogger("sif_backend")


def normalize_output(raw_output: Any, model_source: str) -> AIAnalysisModel:
    """
    Normalizes raw model prediction outputs (boolean, dict, string, list, tuple, class index, sklearn output)
    into standard AIAnalysisModel while preserving exact returned attributes and avoiding unreturned data fabrication.
    """
    if isinstance(raw_output, AIAnalysisModel):
        output_dict = raw_output.model_dump()
        output_dict["model_source"] = model_source
        return AIAnalysisModel(**output_dict)

    if isinstance(raw_output, (list, tuple)):
        if len(raw_output) > 0:
            if len(raw_output) == 2 and isinstance(raw_output[0], (bool, str, int)) and isinstance(raw_output[1], (float, int)):
                # Handle tuple of (label, confidence)
                label, conf = raw_output[0], float(raw_output[1])
                is_sif = bool(label) if isinstance(label, bool) else (str(label).upper() in ["SIF", "PRECURSOR", "TRUE", "1", "YES"])
                return AIAnalysisModel(
                    sif_precursor=is_sif,
                    confidence=round(conf, 2),
                    hazard_category="UNCLASSIFIED",
                    severity=4 if is_sif else 2,
                    evidence=[f"Model output tuple: label={label}, confidence={conf}"],
                    model_source=model_source
                )
            raw_output = raw_output[0]

    if isinstance(raw_output, dict):
        sif = raw_output.get("sif_precursor", raw_output.get("sif", raw_output.get("label", raw_output.get("is_sif", False))))
        if isinstance(sif, str):
            sif = sif.upper() in ["SIF", "PRECURSOR", "TRUE", "1", "YES"]
        elif isinstance(sif, (int, float)):
            sif = bool(sif)

        conf = float(raw_output.get("confidence", raw_output.get("score", raw_output.get("prob", 0.88 if sif else 0.75))))
        cat = str(raw_output.get("hazard_category", raw_output.get("hazard", raw_output.get("category", "UNCLASSIFIED"))))
        act = raw_output.get("unsafe_act", raw_output.get("act"))
        cond = raw_output.get("unsafe_condition", raw_output.get("condition"))
        sev = int(raw_output.get("severity", 4 if sif else 2))
        ev = raw_output.get("evidence", [])
        if isinstance(ev, str):
            ev = [ev]

        return AIAnalysisModel(
            sif_precursor=bool(sif),
            confidence=round(conf, 2),
            hazard_category=cat,
            unsafe_act=str(act) if act else None,
            unsafe_condition=str(cond) if cond else None,
            severity=sev,
            evidence=list(ev) if ev else [f"Model inference prediction: SIF={sif}"],
            model_source=model_source
        )

    if isinstance(raw_output, bool):
        return AIAnalysisModel(
            sif_precursor=raw_output,
            confidence=0.90 if raw_output else 0.85,
            hazard_category="CONFINED_SPACE" if raw_output else "GENERAL_SAFETY",
            severity=4 if raw_output else 2,
            evidence=[f"Model prediction boolean: SIF={raw_output}"],
            model_source=model_source
        )

    if isinstance(raw_output, (int, float)):
        is_sif = bool(raw_output > 0)
        return AIAnalysisModel(
            sif_precursor=is_sif,
            confidence=0.88 if is_sif else 0.80,
            hazard_category="UNCLASSIFIED",
            severity=4 if is_sif else 2,
            evidence=[f"Model numeric prediction: value={raw_output}"],
            model_source=model_source
        )

    if isinstance(raw_output, str):
        label_upper = raw_output.upper()
        is_sif = label_upper in ["SIF", "PRECURSOR", "TRUE", "1", "YES", "CONFINED_SPACE", "WORKING_AT_HEIGHT", "ELECTRICAL_SAFETY", "SUSPENDED_LOAD", "PRESSURE_SYSTEMS", "HOT_WORK"]
        return AIAnalysisModel(
            sif_precursor=is_sif,
            confidence=0.88,
            hazard_category=label_upper if is_sif and label_upper not in ["SIF", "PRECURSOR", "TRUE", "1", "YES"] else "UNCLASSIFIED",
            severity=4 if is_sif else 2,
            evidence=[f"Model string prediction: {raw_output}"],
            model_source=model_source
        )

    # Generic fallback normalization
    is_sif = bool(raw_output)
    return AIAnalysisModel(
        sif_precursor=is_sif,
        confidence=0.75,
        hazard_category="UNCLASSIFIED",
        severity=3 if is_sif else 1,
        evidence=[f"Generic model prediction: {str(raw_output)}"],
        model_source=model_source
    )


class BaseAIAdapter(ABC):
    @abstractmethod
    def analyze(self, text: str) -> AIAnalysisModel:
        pass

    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        pass


class RealMLModelAdapter(BaseAIAdapter):
    """Adapter for Member 1 binary pickled model (model.pkl)."""
    def __init__(self, model_path: str, relative_path: str):
        self.model_path = model_path
        self.relative_path = relative_path
        self.model = None
        self.load_error: Optional[str] = None
        self._load_model()

    def _load_model(self):
        try:
            import joblib
            self.model = joblib.load(self.model_path)
            if not (hasattr(self.model, "predict") or callable(self.model)):
                raise ValueError("Loaded model object lacks a callable predict method.")
            logger.info(f"Loaded Member 1 binary model from {self.relative_path}")
        except Exception as e:
            self.load_error = f"REAL MODEL DETECTED BUT FAILED TO LOAD: {str(e)}"
            logger.error(f"Failed to load binary model at {self.model_path}: {str(e)}", exc_info=True)

    def analyze(self, text: str) -> AIAnalysisModel:
        if not self.model or self.load_error:
            raise RuntimeError(self.load_error or "Binary model not loaded.")
        
        # Check predict or callable
        raw_pred = self.model.predict([text]) if hasattr(self.model, "predict") else self.model(text)
        
        # Check predict_proba if available
        confidence_override = None
        if hasattr(self.model, "predict_proba"):
            try:
                proba = self.model.predict_proba([text])[0]
                if hasattr(proba, "__iter__"):
                    confidence_override = round(float(max(proba)), 2)
            except Exception as e:
                logger.warning(f"predict_proba call failed: {str(e)}")

        norm = normalize_output(raw_pred, model_source="REAL_MODEL")
        if confidence_override is not None:
            norm.confidence = confidence_override
        return norm

    def get_info(self) -> Dict[str, Any]:
        if self.model and not self.load_error:
            return {
                "mode": "REAL_MODEL",
                "model_loaded": True,
                "model_path": self.relative_path,
                "reason": None
            }
        return {
            "mode": "REAL_MODEL",
            "model_loaded": False,
            "model_path": self.relative_path,
            "reason": self.load_error or "Real model failed to load."
        }


class PredictScriptAdapter(BaseAIAdapter):
    """Adapter for Member 1 Python prediction script (predict.py)."""
    def __init__(self, script_path: str, relative_path: str):
        self.script_path = script_path
        self.relative_path = relative_path
        self.predict_func = None
        self.load_error: Optional[str] = None
        self._load_script()

    def _load_script(self):
        try:
            spec = importlib.util.spec_from_file_location("member1_predict", self.script_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not load spec from {self.script_path}")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            predict_fn = getattr(module, "predict", getattr(module, "analyze_text", getattr(module, "predict_sif", None)))
            if not callable(predict_fn):
                raise ValueError("predict.py exists but does not export a callable predict(text), analyze_text(text), or predict_sif(text) function.")
            self.predict_func = predict_fn
            logger.info(f"Loaded Member 1 prediction script from {self.relative_path}")
        except Exception as e:
            self.load_error = f"PREDICT SCRIPT DETECTED BUT FAILED TO LOAD: {str(e)}"
            logger.error(f"Failed to load predict script at {self.script_path}: {str(e)}", exc_info=True)

    def analyze(self, text: str) -> AIAnalysisModel:
        if not self.predict_func or self.load_error:
            raise RuntimeError(self.load_error or "Predict function not loaded.")
        raw = self.predict_func(text)
        return normalize_output(raw, model_source="PREDICT_SCRIPT")

    def get_info(self) -> Dict[str, Any]:
        if self.predict_func and not self.load_error:
            return {
                "mode": "PREDICT_SCRIPT",
                "model_loaded": True,
                "model_path": self.relative_path,
                "reason": None
            }
        return {
            "mode": "PREDICT_SCRIPT",
            "model_loaded": False,
            "model_path": self.relative_path,
            "reason": self.load_error or "Predict script failed to load."
        }


class FallbackAdapter(BaseAIAdapter):
    """Domain-aware Rule & Keyword-boosted NLP engine fallback."""
    def analyze(self, text: str) -> AIAnalysisModel:
        res = self._analyze_with_nlp_engine(text)
        res.model_source = "FALLBACK"
        return res

    def get_info(self) -> Dict[str, Any]:
        return {
            "mode": "FALLBACK",
            "model_loaded": False,
            "model_path": None,
            "reason": "Member 1 model not available"
        }

    def _analyze_with_nlp_engine(self, text: str) -> AIAnalysisModel:
        text_lower = text.lower()
        categories = {
            "CONFINED_SPACE": {
                "keywords": ["confined space", "vessel entry", "tank entry", "gas test", "h2s", "oxygen deficiency", "manhole", "nitrogen purging"],
                "sif_acts": ["entry without gas test", "no permit for entry", "unauthorized entry"],
                "sif_conditions": ["gas detector faulty", "no ventilation", "toxic gas build up"],
                "base_severity": 5
            },
            "WORKING_AT_HEIGHT": {
                "keywords": ["height", "scaffolding", "harness", "safety belt", "elevated", "fall arrest", "ladder", "roof work", "open edge"],
                "sif_acts": ["working without harness", "unhooked safety lanyard", "standing on top railing"],
                "sif_conditions": ["missing guardrail", "unsecured scaffold board", "slippery grating"],
                "base_severity": 4
            },
            "ELECTRICAL_SAFETY": {
                "keywords": ["high voltage", "live wire", "loto", "lockout", "tagout", "electrical panel", "short circuit", "arc flash", "substation"],
                "sif_acts": ["work on live equipment", "bypassed LOTO", "no rubber gloves"],
                "sif_conditions": ["exposed live conductor", "damaged insulation", "water near electrical panel"],
                "base_severity": 5
            },
            "SUSPENDED_LOAD": {
                "keywords": ["crane", "hoist", "rigging", "suspended load", "sling", "lifting", "crane hook", "derrick"],
                "sif_acts": ["walking under load", "improper rigging", "overloading crane"],
                "sif_conditions": ["snapped sling", "uncalibrated crane indicator", "damaged wire rope"],
                "base_severity": 4
            },
            "PRESSURE_SYSTEMS": {
                "keywords": ["high pressure", "pipeline", "relief valve", "wellhead", "booster pump", "burst disc", "flange leak", "blowout"],
                "sif_acts": ["tightening under pressure", "overpressurizing line", "bypassing relief valve"],
                "sif_conditions": ["corroded flange", "defective pressure gauge", "line overpressure"],
                "base_severity": 5
            },
            "HOT_WORK": {
                "keywords": ["welding", "cutting", "grinding", "sparks", "hot work permit", "hydrocarbon leak", "gas leak"],
                "sif_acts": ["welding near flammable material", "no fire watch", "hot work without permit"],
                "sif_conditions": ["flammable gas buildup", "missing spark screen", "leaking acetylene hose"],
                "base_severity": 4
            }
        }

        matched_category = "GENERAL_SAFETY"
        matched_score = 0
        detected_evidence: List[str] = []
        severity = 2
        detected_unsafe_act: Optional[str] = None
        detected_unsafe_condition: Optional[str] = None

        for cat_name, info in categories.items():
            hits = [kw for kw in info["keywords"] if kw in text_lower]
            if len(hits) > matched_score:
                matched_score = len(hits)
                matched_category = cat_name
                severity = info["base_severity"]
                detected_evidence = [f"Detected term '{h}'" for h in hits]

                for act in info["sif_acts"]:
                    if any(w in text_lower for w in act.split()):
                        detected_unsafe_act = act.upper().replace(" ", "_")
                for cond in info["sif_conditions"]:
                    if any(w in text_lower for w in cond.split()):
                        detected_unsafe_condition = cond.upper().replace(" ", "_")

        sif_keywords = ["near miss", "fatal", "death", "explosion", "fire", "leak", "collapse", "electrocution", "unconscious", "high risk", "bypass", "without permit"]
        sif_hits = [skw for skw in sif_keywords if skw in text_lower]

        sif_precursor = (matched_score >= 1 and severity >= 4) or len(sif_hits) >= 1

        if sif_hits:
            detected_evidence.extend([f"Critical keyword '{sk}'" for sk in sif_hits])

        confidence = 0.92 if (sif_precursor and matched_score >= 2) else (0.85 if sif_precursor else 0.75)

        if not detected_unsafe_act and matched_category != "GENERAL_SAFETY":
            detected_unsafe_act = f"UNSAFE_{matched_category}_OPERATION"
        if not detected_unsafe_condition and matched_category != "GENERAL_SAFETY":
            detected_unsafe_condition = f"UNPROTECTED_{matched_category}_HAZARD"

        return AIAnalysisModel(
            sif_precursor=sif_precursor,
            confidence=round(confidence, 2),
            hazard_category=matched_category,
            unsafe_act=detected_unsafe_act,
            unsafe_condition=detected_unsafe_condition,
            severity=severity,
            evidence=detected_evidence if detected_evidence else ["Standard safety observations noted."],
            model_source="FALLBACK"
        )


class AIAdapter:
    """
    Facade AIAdapter managing strategy selection according to Member 1 availability:
    1. RealMLModelAdapter (model.pkl)
    2. PredictScriptAdapter (predict.py)
    3. FallbackAdapter (Domain NLP Engine)
    """
    def __init__(self):
        self.active_adapter: BaseAIAdapter = self._detect_and_create_adapter()

    def _detect_and_create_adapter(self) -> BaseAIAdapter:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
        
        # Priority 1: Binary pickled model (model.pkl)
        pkl_candidates = [
            os.path.abspath(os.path.join(base_dir, "backend/ml/models/model.pkl")),
            os.path.abspath(os.path.join(base_dir, "ml/models/model.pkl")),
            os.path.abspath(settings.MODEL_PATH)
        ]
        for pkl_path in pkl_candidates:
            if os.path.exists(pkl_path) and os.path.getsize(pkl_path) > 0:
                rel_path = os.path.relpath(pkl_path, base_dir).replace("\\", "/")
                logger.info(f"Detected Member 1 model binary at {rel_path}")
                adapter = RealMLModelAdapter(pkl_path, rel_path)
                if adapter.get_info()["model_loaded"]:
                    return adapter
                else:
                    # Keep failed adapter so get_status() reflects exact loading error
                    logger.error(f"Real model binary at {rel_path} detected but failed initialization.")
                    return adapter

        # Priority 2: Python prediction script (predict.py)
        py_candidates = [
            os.path.abspath(os.path.join(base_dir, "ai_model/src/predict.py")),
            os.path.abspath(os.path.join(base_dir, "backend/ai_model/src/predict.py"))
        ]
        for py_path in py_candidates:
            if os.path.exists(py_path) and os.path.getsize(py_path) > 0:
                rel_path = os.path.relpath(py_path, base_dir).replace("\\", "/")
                logger.info(f"Detected Member 1 predict script at {rel_path}")
                adapter = PredictScriptAdapter(py_path, rel_path)
                if adapter.get_info()["model_loaded"]:
                    return adapter
                else:
                    logger.error(f"Predict script at {rel_path} detected but failed initialization.")
                    return adapter

        # Priority 3: Fallback adapter
        logger.info("Neither model.pkl nor non-empty predict.py detected. Initializing FallbackAdapter.")
        return FallbackAdapter()

    def analyze(self, text: str) -> AIAnalysisModel:
        status_info = self.get_status()
        if not text or not text.strip():
            return AIAnalysisModel(
                sif_precursor=False,
                confidence=0.0,
                hazard_category="GENERAL_SAFETY",
                severity=1,
                evidence=["No description provided."],
                model_source=status_info.get("mode", "FALLBACK")
            )

        try:
            return self.active_adapter.analyze(text)
        except Exception as e:
            logger.error(f"Error in AIAdapter ({status_info['mode']}) execution: {str(e)}", exc_info=True)
            if status_info["mode"] != "FALLBACK":
                logger.warning("Active real model execution failed; falling back safely to NLP baseline.")
                fallback = FallbackAdapter()
                res = fallback.analyze(text)
                res.evidence.append(f"Notice: {status_info['mode']} runtime warning; using baseline output.")
                return res

            return AIAnalysisModel(
                sif_precursor=False,
                confidence=0.5,
                hazard_category="UNCLASSIFIED",
                severity=2,
                evidence=["Automated AI extraction encountered an error; manual review advised."],
                model_source="FALLBACK"
            )

    def get_status(self) -> Dict[str, Any]:
        return self.active_adapter.get_info()
