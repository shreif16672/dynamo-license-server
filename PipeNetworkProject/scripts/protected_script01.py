import os
import json

def clean(text):
    return text.replace("\\P", "\n").replace("{", "").replace("}", "").strip()

def parse_item(line):
    item = {}
    parts = line.split("\\n")
    for part in parts:
        if "MH" in part:
            item["Name"] = part.strip()
        elif "CL" in part:
            item["CL"] = float(part.replace("CL=", "").strip())
        elif "IL" in part:
            item["IL"] = float(part.replace("IL=", "").strip())
        elif part.strip().startswith("E="):
            item["E"] = float(part.replace("E=", "").strip())
        elif part.strip().startswith("N="):
            item["N"] = float(part.replace("N=", "").strip())
    return item

# Load dynamic project path
conf_path = os.path.join("input", "project_path.txt")
with open(conf_path, "r") as f:
    project_path = f.read().strip()

# Load MText data
mtext_path = os.path.join(project_path, "input", "mtext_data.json")
with open(mtext_path, "r") as f:
    mtext_objects = json.load(f)

parsed = []
for m in mtext_objects:
    location = m["location"]
    text = m["text"]
    lines = clean(text).split("\n")
    data = parse_item("\n".join(lines))
    if "Name" in data:
        data["X"] = location[0]
        data["Y"] = location[1]
        parsed.append(data)

# Output grouped by base name
grouped = {}
for item in parsed:
    base = item["Name"].split("-")[0]
    if base not in grouped:
        grouped[base] = []
    grouped[base].append(item)

# Save result
output_path = os.path.join(project_path, "output", "first_names.json")
with open(output_path, "w") as f:
    json.dump(grouped, f, indent=2)