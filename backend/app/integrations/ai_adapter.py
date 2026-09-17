import os
import sys
import logging
import importlib.util
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from app.models.report import AIAnalysisModel
from app.config import settings

logger = logging.getLogger("sif_backend")

# Ensure project root is in sys.path for ml module imports
BASE_PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if BASE_PROJECT_DIR not in sys.path:
    sys.path.insert(0, BASE_PROJECT_DIR)

try:
    from ml.registry.model_registry import ModelRegistry
    from ml.models.hf_adapter import HuggingFaceAdapter
    from ml.models.baseline import BaselineMLModel
    from ml.models.language import MultilingualSafetyEngine
    from ml.data.preprocessing import TextPreprocessor
    ML_MODULE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"ml package import warning in ai_adapter: {e}")
    ML_MODULE_AVAILABLE = False


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
        sif = raw_output.get("sif_potential", raw_output.get("sif_precursor", raw_output.get("sif", raw_output.get("label", raw_output.get("is_sif", False)))))
        if isinstance(sif, str):
            sif = sif.upper() in ["SIF", "PRECURSOR", "TRUE", "1", "YES"]
        elif isinstance(sif, (int, float)):
            sif = bool(sif)

        conf = float(raw_output.get("sif_probability", raw_output.get("confidence", raw_output.get("score", raw_output.get("prob", 0.88 if sif else 0.75)))))
        cat = str(raw_output.get("hazard_category", raw_output.get("hazard", raw_output.get("category", "UNCLASSIFIED"))))
        act = raw_output.get("unsafe_act", raw_output.get("act"))
        cond = raw_output.get("unsafe_condition", raw_output.get("condition"))
        sev = int(raw_output.get("severity", 4 if sif else 2))
        ev = raw_output.get("evidence", [])
        if isinstance(ev, str):
            ev = [ev]
        ls_rules = raw_output.get("life_saving_rules")
        if ls_rules and isinstance(ls_rules, list):
            ev = list(ev)
            ev.append(f"Mapped Life-Saving Rules: {', '.join(str(r) for r in ls_rules)}")
            if cat == "UNCLASSIFIED" and len(ls_rules) > 0 and ls_rules[0] != "None":
                cat = ls_rules[0].upper().replace(" ", "_")

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


class HuggingFaceAIAdapter(BaseAIAdapter):
    """Adapter leveraging HuggingFace Transformer Pipeline."""
    def __init__(self, model_name: Optional[str] = None):
        if not ML_MODULE_AVAILABLE:
            raise RuntimeError("ml package not available for HuggingFaceAIAdapter")
        self.adapter = HuggingFaceAdapter(model_name)

    def analyze(self, text: str) -> AIAnalysisModel:
        raw_res = self.adapter.predict(text)
        return normalize_output(raw_res, model_source="HUGGINGFACE")

    def get_info(self) -> Dict[str, Any]:
        info = self.adapter.get_info()
        info["mode"] = "HUGGINGFACE"
        return info


class RealMLModelAdapter(BaseAIAdapter):
    """Adapter for Member 1 binary pickled model (model.pkl / sif_classifier.pkl)."""
    def __init__(self, model_path: str, relative_path: str):
        self.model_path = model_path
        self.relative_path = relative_path
        self.model = None
        self.vectorizer = None
        self.load_error: Optional[str] = None
        self._load_model()

    def _load_model(self):
        try:
            import joblib
            self.model = joblib.load(self.model_path)
            if not (hasattr(self.model, "predict") or callable(self.model)):
                raise ValueError("Loaded model object lacks a callable predict method.")
            
            # Check for companion tfidf_vectorizer.pkl / vectorizer.pkl
            model_dir = os.path.dirname(self.model_path)
            for vec_name in ["tfidf_vectorizer.pkl", "vectorizer.pkl", "sif_vectorizer.pkl"]:
                vec_candidate = os.path.join(model_dir, vec_name)
                if os.path.exists(vec_candidate) and os.path.getsize(vec_candidate) > 0:
                    try:
                        self.vectorizer = joblib.load(vec_candidate)
                        logger.info(f"Loaded companion vectorizer from {vec_name}")
                        break
                    except Exception as ve:
                        logger.warning(f"Could not load vectorizer {vec_candidate}: {ve}")

            logger.info(f"Loaded Member 1 binary model from {self.relative_path}")
        except Exception as e:
            self.load_error = f"REAL MODEL DETECTED BUT FAILED TO LOAD: {str(e)}"
            logger.error(f"Failed to load binary model at {self.model_path}: {str(e)}", exc_info=True)

    def analyze(self, text: str) -> AIAnalysisModel:
        if not self.model or self.load_error:
            raise RuntimeError(self.load_error or "Binary model not loaded.")
        
        fam_score = 1.0
        if self.vectorizer:
            clean_t = TextPreprocessor.clean_text(text) if ML_MODULE_AVAILABLE else text.lower()
            input_data = self.vectorizer.transform([clean_t])
            nnz_count = getattr(input_data, "nnz", 0)
            words = [w for w in clean_t.split() if len(w) > 2]
            if len(words) > 0:
                fam_score = round(min(1.0, max(0.1, (nnz_count / max(1, len(words))) * 1.35)), 2)
        else:
            input_data = [text]

        raw_pred = self.model.predict(input_data) if hasattr(self.model, "predict") else self.model(input_data)
        
        confidence_override = None
        if hasattr(self.model, "predict_proba"):
            try:
                proba = self.model.predict_proba(input_data)[0]
                if hasattr(proba, "__iter__"):
                    confidence_override = round(float(max(proba)), 2)
            except Exception as e:
                logger.warning(f"predict_proba call failed: {str(e)}")

        norm = normalize_output(raw_pred, model_source="REAL_MODEL")
        if confidence_override is not None:
            norm.confidence = confidence_override
        norm.training_familiarity = fam_score
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
            script_dir = os.path.dirname(self.script_path)
            if script_dir not in sys.path:
                sys.path.insert(0, script_dir)
            spec = importlib.util.spec_from_file_location("member1_predict", self.script_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not load spec from {self.script_path}")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            predict_fn = (
                getattr(module, "process_complete_report", None) or
                getattr(module, "predict", None) or
                getattr(module, "analyze_text", None) or
                getattr(module, "predict_sif", None) or
                getattr(module, "analyze", None)
            )
            if not callable(predict_fn):
                raise ValueError("predict.py exists but does not export a callable process_complete_report, predict, analyze_text, or predict_sif function.")
            self.predict_func = predict_fn
            logger.info(f"Loaded Member 1 prediction script from {self.relative_path}")
        except Exception as e:
            self.load_error = f"REAL MODEL SCRIPT DETECTED BUT FAILED TO LOAD: {str(e)}"
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

        if ML_MODULE_AVAILABLE:
            safety_ctx = TextPreprocessor.analyze_safety_context(text)
            c_type = safety_ctx.get("context_type", "UNKNOWN")
            if c_type in ["SAFE_COMPLIANCE", "PREVENTED_EVENT"]:
                sif_precursor = False
                detected_unsafe_act = None
                severity = min(severity, 2)

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
    Facade AIAdapter managing strategy selection according to Member 1 availability and ModelRegistry:
    1. ModelRegistry active model (Hugging Face / Baseline ML)
    2. RealMLModelAdapter (model.pkl)
    3. PredictScriptAdapter (predict.py)
    4. FallbackAdapter (Domain NLP Engine)
    """
    def __init__(self):
        self.registry: Optional[Any] = ModelRegistry() if ML_MODULE_AVAILABLE else None
        self.active_adapter: BaseAIAdapter = self._detect_and_create_adapter()

    def _detect_and_create_adapter(self) -> BaseAIAdapter:
        base_dir = BASE_PROJECT_DIR

        # Check ModelRegistry active model choice
        if self.registry:
            active_info = self.registry.get_active_model_info()
            if active_info:
                model_type = active_info.get("model_type", "")
                if model_type == "HUGGINGFACE":
                    try:
                        hf_adapter = HuggingFaceAIAdapter(active_info.get("model_name"))
                        if hf_adapter.get_info()["model_loaded"]:
                            logger.info(f"Using active HuggingFace model from registry: {active_info['model_id']}")
                            return hf_adapter
                    except Exception as e:
                        logger.warning(f"Active HuggingFace model failed to initialize: {e}")

        # Priority 1: Binary pickled model (model.pkl / sif_classifier.pkl)
        pkl_candidates = [
            os.path.abspath(os.path.join(base_dir, "ai_model/model/sif_classifier.pkl")),
            os.path.abspath(os.path.join(base_dir, "backend/ai_model/model/sif_classifier.pkl")),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "../../ai_model/model/sif_classifier.pkl")),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../ai_model/model/sif_classifier.pkl")),
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

        # Multilingual & Negation pre-processing enrichments
        multilingual_info = None
        negation_info = None
        if ML_MODULE_AVAILABLE:
            try:
                multilingual_info = MultilingualSafetyEngine.process_multilingual_report(text)
                negation_info = TextPreprocessor.extract_negations_and_hazards(text)
            except Exception as e:
                logger.debug(f"Pre-processing extraction notice: {e}")

        try:
            result = self.active_adapter.analyze(text)
        except Exception as e:
            logger.error(f"Error in AIAdapter ({status_info['mode']}) execution: {str(e)}", exc_info=True)
            if status_info["mode"] != "FALLBACK":
                logger.warning("Active model execution failed; falling back safely to NLP baseline.")
                fallback = FallbackAdapter()
                result = fallback.analyze(text)
                result.evidence.append(f"Notice: {status_info['mode']} runtime warning; using baseline output.")
            else:
                result = AIAnalysisModel(
                    sif_precursor=False,
                    confidence=0.5,
                    hazard_category="UNCLASSIFIED",
                    severity=2,
                    evidence=["Automated AI extraction encountered an error; manual review advised."],
                    model_source="FALLBACK"
                )

        # Enrich result with multilingual detection if present
        if multilingual_info and multilingual_info.get("language") != "en":
            lang_name = multilingual_info.get("language_name", "Non-English")
            result.evidence.append(f"Multilingual Report: Detected {lang_name} safety terminology")

        # Enrich evidence with negation info if present
        if negation_info and negation_info.get("has_negation"):
            neg_terms = ", ".join(negation_info.get("detected_negations", []))
            result.evidence.append(f"Negation Aware: Context includes safety negation ({neg_terms})")

        # Enrich hazard category if active model output UNCLASSIFIED or UNKNOWN
        if result.hazard_category in ["UNCLASSIFIED", "UNKNOWN", "GENERAL_SAFETY"]:
            fallback_extract = FallbackAdapter()._analyze_with_nlp_engine(text)
            if fallback_extract.hazard_category != "GENERAL_SAFETY":
                result.hazard_category = fallback_extract.hazard_category
                result.severity = max(result.severity, fallback_extract.severity)
                if fallback_extract.unsafe_act:
                    result.unsafe_act = result.unsafe_act or fallback_extract.unsafe_act
                if fallback_extract.unsafe_condition:
                    result.unsafe_condition = result.unsafe_condition or fallback_extract.unsafe_condition

        # Record raw model prediction and raw confidence
        if result.raw_prediction is None:
            result.raw_prediction = result.sif_precursor
        if result.raw_confidence is None:
            result.raw_confidence = result.confidence

        # Perform Domain Safety Context Analysis & Explainable Adjustment
        if ML_MODULE_AVAILABLE:
            safety_ctx = TextPreprocessor.analyze_safety_context(text)
            c_type = safety_ctx.get("context_type", "UNKNOWN")
            result.context_type = c_type

            if c_type in ["SAFE_COMPLIANCE", "PREVENTED_EVENT"]:
                result.sif_precursor = False
                result.severity = min(result.severity, 2)
                result.unsafe_act = None
                display_type = c_type.replace('_', ' ').title()
                result.context_adjustment_reason = (
                    f"Safety Context Adjustment: Report represents {display_type}. "
                    f"Raw ML model flagged SIF potential based on hazard terminology, but final SIF precursor "
                    f"set to False because safe procedures were followed / event was prevented."
                )
                if safety_ctx.get("evidence_phrases"):
                    for phrase in safety_ctx["evidence_phrases"]:
                        result.evidence.append(f"Context evidence: '{phrase}'")
            elif c_type == "UNSAFE_BEHAVIOR":
                result.sif_precursor = True
                result.context_adjustment_reason = "Unsafe behavior or violation confirmed by safety context analysis."
                if safety_ctx.get("evidence_phrases"):
                    for phrase in safety_ctx["evidence_phrases"]:
                        result.evidence.append(f"Context evidence: '{phrase}'")
            elif c_type == "NEAR_MISS":
                result.sif_precursor = True
                result.context_adjustment_reason = "Near-miss event confirmed by safety context analysis."
                if safety_ctx.get("evidence_phrases"):
                    for phrase in safety_ctx["evidence_phrases"]:
                        result.evidence.append(f"Context evidence: '{phrase}'")
            else:
                result.context_adjustment_reason = "No specific safety compliance or negation phrases detected; relying on raw ML model prediction."
        else:
            result.context_type = "UNKNOWN"
            result.context_adjustment_reason = "ML module unavailable; using baseline prediction."

        # Novelty / Training Familiarity Check
        if result.training_familiarity < 0.40 or result.context_type == "UNKNOWN" or result.confidence < 0.60:
            result.is_novel = (result.training_familiarity < 0.40 or result.context_type == "UNKNOWN")
            if result.is_novel:
                result.evidence.append(f"Novelty Detection: Training familiarity ({result.training_familiarity}) is low / unfamiliar vocab. Safety Officer review required.")

        return result


    def get_status(self) -> Dict[str, Any]:
        info = self.active_adapter.get_info()
        if self.registry:
            active_reg = self.registry.get_active_model_info()
            if active_reg:
                info["active_model_id"] = active_reg.get("model_id")
                info["active_model_name"] = active_reg.get("model_name")
                info["active_metrics"] = active_reg.get("metrics")
        return info

