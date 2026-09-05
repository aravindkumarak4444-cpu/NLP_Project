import os
import pandas as pd
import random

# 1. Create the data/sample/ directory if it doesn't exist
os.makedirs("data/sample", exist_ok=True)

# 2. Define realistic safety reports
descriptions = [
    "Worker doing welding near pressurized gas line without fire watch.",
    "Tripped on an extension cord in the office hallway, no injury.",
    "Entering confined space for inspection without oxygen monitoring.",
    "Slipped on wet floor in the cafeteria.",
    "Working on a scaffold at 10 meters without safety harness tied off.",
    "Scratched arm while opening a cardboard box in the storeroom.",
    "Electrical panel left open with live wires exposed during maintenance.",
    "Dropped a heavy wrench from 2nd floor, narrowly missing a worker below.",
    "Dust fell in eye due to not wearing safety goggles.",
    "Forklift driving at high speed in a pedestrian walking zone."
]

sif_labels = [1, 0, 1, 0, 1, 0, 1, 1, 0, 1]

# 3. Generate 100 rows of data
data = []
for i in range(100):
    idx = i % 10
    data.append({
        "report_id": f"REP-{1000 + i}",
        "description": descriptions[idx],
        "sif_potential": sif_labels[idx]
    })

# 4. Save directly into your data folder
df = pd.DataFrame(data)
save_path = "data/sample/sample_reports.csv"
df.to_csv(save_path, index=False)
print(f"Dataset successfully created at: {save_path}")