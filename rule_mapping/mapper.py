import json
import os
import re


def get_life_saving_rules(report_text):
    text = str(report_text).lower()

    rules_path = os.path.join(os.path.dirname(__file__), "rules.json")
    with open(rules_path, "r", encoding="utf-8") as rules_file:
        rules_keywords = json.load(rules_file)
    
    detected_rules = []
    
    # Check the report text against keywords
    for rule, keywords in rules_keywords.items():
        for word in keywords:
            if re.search(r"(?<!\w)" + re.escape(word) + r"(?!\w)", text):
                detected_rules.append(rule)
                break  # Stop checking keywords for this specific rule to avoid duplicates
                
    # If no specific keywords are found, return a default tag
    if not detected_rules:
        return ["General Safety"]
        
    return detected_rules

# --- Testing the Mapper ---
if __name__ == "__main__":
    sample_report = "Worker was welding on a scaffold without a permit."
    mapped_rules = get_life_saving_rules(sample_report)
    print(f"Report: {sample_report}")
    print(f"Assigned Rules: {mapped_rules}")