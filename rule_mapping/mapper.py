def get_life_saving_rules(report_text):
    text = str(report_text).lower()
    
    # Her exact dictionary, plus the new Oil & Gas terms
    rules_keywords = {
        "Bypassing Safety Controls": ["bypass", "bypassing", "override", "overriding", "disable safety", "disabled safety", "safety control", "interlock", "alarm", "safety system"],
        "Confined Space": ["confined space", "confined area", "tank", "vessel", "manhole", "oxygen", "gas testing", "gas test", "entry permit", "h2s", "toxic gas", "trench", "excavation"],
        "Driving": ["driving", "driver", "vehicle", "car", "truck", "seat belt", "seatbelt", "speeding", "speed limit", "mobile phone", "phone while driving"],
        "Energy Isolation": ["isolate", "isolation", "isolated", "hazardous energy", "energy isolation", "lockout", "lockout tagout", "loto", "zero energy", "electrical isolation", "power supply", "blind", "spading", "bleed", "depressurize"],
        "Hot Work": ["hot work", "welding", "weld", "cutting", "grinding", "spark", "flame", "ignition", "flammable", "flammable material"],
        "Line of Fire": ["line of fire", "moving object", "moving equipment", "vehicle", "pressure release", "dropped object", "falling object", "pinch point", "struck by", "exclusion zone", "unsafe position"],
        "Safe Mechanical Lifting": ["lifting", "lifting operation", "crane", "hoist", "rigging", "rigging operation", "suspended load", "lifting equipment", "lift plan", "mechanical lifting"],
        "Work Authorisation": ["work authorisation", "work authorization", "permit", "work permit", "permit to work", "ptw", "authorization", "authorisation", "permit required", "jsa", "jha", "tbt"],
        "Work at Height": ["work at height", "working at height", "height", "ladder", "scaffold", "scaffolding", "fall", "fall protection", "harness", "safety harness", "elevated work"]
    }
    
    detected_rules = []
    
    # Check the report text against keywords
    for rule, keywords in rules_keywords.items():
        for word in keywords:
            if word in text:
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