import json
import re
from datetime import datetime
import ast


# --- Configuration ---
# Adjust your input and output file paths here
INPUT_JSON_PATH = "/Users/m/Downloads/eai-2025-07-01.json"
OUTPUT_MD_PATH = "experiment_report.md"

# --- Helper Functions ---


def parse_links(input_string):
    parsed_dict = {}
    pattern = re.compile(r"(.+?):\s*(.*?)(?=\n[^\n:]+:|$)", re.DOTALL)
    matches = pattern.findall(input_string)
    for key, value in matches:
        clean_key = key.strip().lower().replace(" ", "_")
        value_str = value.strip()
        try:
            parsed_value = ast.literal_eval(value_str)
        except (ValueError, SyntaxError):
            parsed_value = value_str

        parsed_dict[clean_key] = parsed_value

    return parsed_dict


def get_safe(data_dict, key_path, default=None):
    """
    Safely get a value from a nested dictionary.
    key_path should be a string like 'key1.key2.key3'.
    """
    keys = key_path.split(".")
    current = data_dict
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


# --- Main Script ---

print(f"Loading data from {INPUT_JSON_PATH}...")
try:
    with open(INPUT_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"ERROR: Input file not found at {INPUT_JSON_PATH}")
    exit()
except json.JSONDecodeError:
    print(
        f"ERROR: Could not decode JSON from {INPUT_JSON_PATH}. Please check the file format."
    )
    exit()

if not data:
    print("The JSON file is empty. No report will be generated.")
    exit()

# --- 1. Extract Shared Experiment Metadata (from the first item) ---
first_item = data[0]
metadata = get_safe(first_item, "output.metadata", {})
experiment_metadata = get_safe(first_item, "output.experiment_metadata", {})

system_prompt = get_safe(experiment_metadata, "system_prompt", "Not available")
tools = get_safe(experiment_metadata, "tools", "Not available")
eval_model = get_safe(experiment_metadata, "eval_model", "Not available")
temperature = get_safe(experiment_metadata, "temperature", "Not available")
final_repose_model = get_safe(
    experiment_metadata, "final_repose_model", "Not available"
)
system_prompt_answer_similarity = get_safe(
    experiment_metadata, "system_prompt_answer_similatiry", "Not available"
)


# --- 2. Build the Markdown Report ---

report_parts = []

# Report Header
report_parts.append("\n## Summary")
report_parts.append("| Parameter | Value |")
report_parts.append("|---|---|")
report_parts.append(f"| **Evaluation Model** | `{eval_model}` |")
report_parts.append(f"| **Final Response Model** | `{final_repose_model}` |")
report_parts.append(f"| **Temperature** | `{temperature}` |")
report_parts.append(f"| **Tools Provided** | `{tools}` |")  # Tools can be long
report_parts.append("-" * 100)  # Visual separator for the main content

# Process each item in the data
for i, item in enumerate(data):
    # Extract item-specific data using safe access
    msg_id = get_safe(item, "output.metadata.id", f"Unknown_ID_{i+1}")
    msg = get_safe(item, "input.mensagem_whatsapp_simulada", "No message found.")

    # Safely get the assistant's answer
    assistant_messages = get_safe(
        item, "output.agent_output.grouped.assistant_messages", []
    )
    answer = (
        assistant_messages[0]["content"]
        if assistant_messages and "content" in assistant_messages[0]
        else "No answer found."
    )

    annotations = get_safe(item, "annotations", [])

    report_parts.append(f"\n## ID: {msg_id}")

    # Input Message
    report_parts.append("### User Message")
    report_parts.append(msg)

    # Agent Answer
    report_parts.append("\n### Agent Answer")
    report_parts.append(answer)

    # Annotations
    report_parts.append("\n### Evaluations")

    show_annotations = [
        "Answer Similarity",
        "Golden Link in Answer",
        "Golden Link in Tool Calling",
    ]
    annotations_by_name = {
        ann.get("name"): ann for ann in annotations if ann.get("name")
    }

    if not annotations_by_name:
        report_parts.append("_No annotations found for this record._")
    else:
        for name in show_annotations:
            if name in annotations_by_name:
                annotation = annotations_by_name[name]

                ann_name = annotation.get("name", "N/A")
                ann_score = annotation.get("score", "N/A")
                ann_explanation = annotation.get("explanation", "")

                report_parts.append(f"\n#### {ann_name}")
                report_parts.append(f"**Score:** `{ann_score}`")

                # Format explanation differently based on content type
                if "Link" in ann_name:
                    parsed_explanation = parse_links(input_string=ann_explanation)
                    formatted_explanation = json.dumps(parsed_explanation, indent=2)
                    report_parts.append("**Explanation:**")
                    report_parts.append(f"```json\n{formatted_explanation}\n```")
                else:
                    # Clean up escaped newlines for better readability
                    ann_explanation = ann_explanation.replace("\\n", "\n")
                    report_parts.append("**Explanation:**")
                    report_parts.append(ann_explanation)

    report_parts.append("\n" + "---")  # Horizontal rule to separate records

# --- 3. Add Appendix for Large Content ---
report_parts.append("\n# Appendix: Prompts and Tools")

# Main System Prompt
report_parts.append("\n## Main System Prompt")
report_parts.append(f"```text\n{system_prompt}\n```")

# Answer Similarity Prompt
report_parts.append("\n## Answer Similarity System Prompt")
report_parts.append(f"```text\n{system_prompt_answer_similarity}\n```")

# --- 4. Write to File ---
final_report = "\n".join(report_parts)

with open(OUTPUT_MD_PATH, "w", encoding="utf-8") as f:
    f.write(final_report)

print(f"✅ Report successfully generated at: {OUTPUT_MD_PATH}")
