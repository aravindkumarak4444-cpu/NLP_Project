import os
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from preprocessing import clean_report_text

# 1. Set up the exact paths to your folders
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
data_path = os.path.join(project_root, "data", "sample", "sample_reports.csv")
model_dir = os.path.join(project_root, "ai_model", "model")

# Create the model folder if it does not exist
os.makedirs(model_dir, exist_ok=True)

# 2. Load the mock dataset we generated
df = pd.read_csv(data_path)

# 3. Clean the text using the preprocessing function
df['clean_text'] = df['description'].apply(clean_report_text)

X = df['clean_text']
y = df['sif_potential']

# 4. Split data into training (80%) and testing (20%)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 5. Convert text descriptions into numerical data
vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
X_train_vec = vectorizer.fit_transform(X_train)

# 6. Train the AI model
model = LogisticRegression(class_weight='balanced', random_state=42)
model.fit(X_train_vec, y_train)

# 7. Save the intelligence so predict.py can use it
joblib.dump(model, os.path.join(model_dir, "sif_classifier.pkl"))
joblib.dump(vectorizer, os.path.join(model_dir, "tfidf_vectorizer.pkl"))

print("Training finished! Files saved in ai_model/model/")