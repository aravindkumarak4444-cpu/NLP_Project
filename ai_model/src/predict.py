import os
import joblib
from preprocessing import clean_report_text

current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, "../model/sif_classifier.pkl")
vectorizer_path = os.path.join(current_dir, "../model/tfidf_vectorizer.pkl")

model = joblib.load(model_path)
vectorizer = joblib.load(vectorizer_path)

def predict_sif(report_text):
    cleaned = clean_report_text(report_text)
    text_vec = vectorizer.transform([cleaned])
    
    pred = model.predict(text_vec)[0]
    probs = model.predict_proba(text_vec)[0]
    confidence = probs[pred]
    
    return {
        "sif_potential": bool(pred == 1),
        "sif_probability": round(float(confidence), 2)
    }

if __name__ == "__main__":
    sample = "Worker performing welding near active crude oil pipe without gas test."
    print("Test Output:", predict_sif(sample))