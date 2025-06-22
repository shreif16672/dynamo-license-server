import json
import os

# Set paths
project_path = os.path.dirname(os.path.abspath(__file__))
input_folder = os.path.join(project_path, "input")
output_folder = os.path.join(project_path, "output")

# Read structure names
with open(os.path.join(input_folder, "structures.json")) as f:
    structures = json.load(f)

# Read cogo names
with open(os.path.join(input_folder, "cogo_names.json")) as f:
    names = json.load(f)

# Export result
with open(os.path.join(output_folder, "structure_name_result.json"), "w") as f:
    json.dump({
        "structures": structures,
        "names": names
    }, f, indent=2)