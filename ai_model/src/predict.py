import os
import sys
import joblib
from preprocessing import clean_report_text

# 1. Setup paths to load your AI model
current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, "../model/sif_classifier.pkl")
vectorizer_path = os.path.join(current_dir, "../model/tfidf_vectorizer.pkl")

# 2. Add the project root to Python's path so we can import Member 2's folder
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
sys.path.append(project_root)

# Import Member 2's function
from rule_mapping.mapper import get_life_saving_rules

# 3. Load the AI Brain
model = joblib.load(model_path)
vectorizer = joblib.load(vectorizer_path)

def process_complete_report(report_text):
    """
    This is the master function Member 4 will call.
    It runs Member 1's AI and Member 2's Rule Mapping together.
    """
    # --- MEMBER 1: AI PREDICTION ---
    cleaned_text = clean_report_text(report_text)
    text_vec = vectorizer.transform([cleaned_text])
    
    pred = model.predict(text_vec)[0]
    probs = model.predict_proba(text_vec)[0]
    confidence = probs[pred]
    
    is_sif = bool(pred == 1)
    
    # --- MEMBER 2: RULE MAPPING ---
    # We only care about broken rules if the AI says it is a SIF danger
    mapped_rules = ["None"]
    if is_sif:
        mapped_rules = get_life_saving_rules(report_text)
        
    # --- THE FINAL CONTRACT FOR MEMBER 4 ---
    return {
        "sif_potential": is_sif,
        "sif_probability": round(float(confidence), 2),
        "life_saving_rules": mapped_rules
    }

# --- Final Sanity Check for Member 1 ---
if __name__ == "__main__":
    print("--- TEST 1: SIF INCIDENT ---")
    bad_report = "Worker performing welding on a scaffold near active crude oil pipe without permit."
    print(process_complete_report(bad_report))
    
    print("\n--- TEST 2: MINOR INCIDENT ---")
    good_report = "Worker attended regular morning safety meeting in the cafeteria."
    print(process_complete_report(good_report))