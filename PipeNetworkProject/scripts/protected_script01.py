
import os
import sys
import re
import json
from math import hypot
from collections import defaultdict

# --- License Check ---
import hashlib

def get_license_path():
    appdata = os.getenv('APPDATA')
    return os.path.join(appdata, 'DynamoLicense', 'license.txt')

def is_license_valid():
    expected = "LICENSE-VALID-1234567890"  # This will be replaced later with actual key
    license_path = get_license_path()
    if not os.path.exists(license_path):
        print("❌ License file not found.")
        return False
    with open(license_path, 'r') as f:
        content = f.read().strip()
        return content == expected

if not is_license_valid():
    sys.exit("⛔ Unauthorized: License invalid or missing.")

# --- Begin Original Logic ---
input_folder = os.path.join(os.path.dirname(sys.argv[0]), "input")
output_file = os.path.join(input_folder, "grouped_data.json")

with open(os.path.join(input_folder, "mtext_data.json"), "r") as f:
    mtexts = json.load(f)

tolerance = 20.0  # meters: max distance between separate MText pieces of the same MH

# Step 1: Extract text and location
mtext_data = []
for m in mtexts:
    try:
        pt = m["Location"]
        mtext_data.append({
            "text": m["Contents"],
            "X": pt["X"],
            "Y": pt["Y"]
        })
    except:
        continue

# Step 2: Group MText entries that are close together (belong to one manhole)
groups = []
while mtext_data:
    base = mtext_data.pop(0)
    group = [base]
    remaining = []

    for other in mtext_data:
        dist = hypot(base["X"] - other["X"], base["Y"] - other["Y"])
        if dist <= tolerance:
            group.append(other)
        else:
            remaining.append(other)
    groups.append(group)
    mtext_data = remaining

# Step 3: Merge the grouped text entries
combined_texts = []
for g in groups:
    merged = "\\P".join([item["text"] for item in g])
    combined_texts.append(merged)

# Step 4: Clean and parse MText contents
def clean_mtext(raw):
    raw = re.sub(r'{\\.*?;', '', raw)
    raw = raw.replace('}', '')
    return raw

def parse_mtext(text):
    text = clean_mtext(text)
    lines = text.replace('\\P', '\n').split('\n')
    data = {"Name": "", "E": 0.0, "N": 0.0, "CL": 0.0, "IL": 0.0}

    for line in lines:
        line = line.strip().lower()
        if any(key in line for key in ["cl", "gl", "fl"]):
            matches = re.findall(r"[-+]?\d*\.\d+|\d+", line)
            if matches:
                data["CL"] = float(matches[0])
        elif "il" in line:
            matches = re.findall(r"[-+]?\d*\.\d+|\d+", line)
            if matches:
                data["IL"] = float(matches[0])
        elif line.startswith("e") or "e:" in line:
            matches = re.findall(r"[-+]?\d*\.\d+|\d+", line)
            if matches:
                data["E"] = float(matches[0])
        elif line.startswith("n") or "n:" in line:
            matches = re.findall(r"[-+]?\d*\.\d+|\d+", line)
            if matches:
                data["N"] = float(matches[0])
        elif "mh" in line:
            data["Name"] = line.upper()
    return data

parsed = [parse_mtext(txt) for txt in combined_texts]

# Step 5: Group by base name (e.g., MH-1)
def get_base_name(name):
    parts = name.split('-')
    return '-'.join(parts[:-1]) if len(parts) > 1 else name

grouped = defaultdict(list)
for item in parsed:
    name = item.get("Name")
    if name:
        base = get_base_name(name)
        grouped[base].append(item)

# Step 6: Smart sort inside each group by padded name
def pad_name(name):
    parts = name.split('-')
    padded = [parts[0]]
    for part in parts[1:]:
        padded.append(part.zfill(3) if part.isdigit() else part)
    return '-'.join(padded)

all_groups = []
for base_name in sorted(grouped.keys()):
    group_items = grouped[base_name]
    group_items.sort(key=lambda x: pad_name(x['Name']))

    names = [i['Name'] for i in group_items]
    easting = [i['E'] for i in group_items]
    northing = [i['N'] for i in group_items]
    cl = [i['CL'] for i in group_items]
    il = [i['IL'] for i in group_items]

    all_groups.append({
        "Name": names,
        "E": easting,
        "N": northing,
        "CL": cl,
        "IL": il
    })

# Save output to JSON
with open(output_file, "w") as f:
    json.dump(all_groups, f, indent=2)
