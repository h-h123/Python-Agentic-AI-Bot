import os, sys, json, re
import subprocess, argparse
from mistralai import Mistral
from mistralai.models import sdkerror

# ---------------- CONFIG ----------------
API_KEY = "CQx1GgPlnyr8IqqwbQmCFzFJH0dTj31k"
MODEL = "mistral-medium"
client = Mistral(api_key=API_KEY)

# ---------------- UTILS ----------------
def clean_code(code):
    """Remove any non-Python lines accidentally inserted by LLM."""
    lines = code.splitlines()
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(("Here's", "Note", "File:")):
            continue
        new_lines.append(line)
    return "\n".join(new_lines)

def validate_python(code, filename="<string>"):
    """Check if code is valid Python syntax."""
    try:
        compile(code, filename, "exec")
        return True
    except SyntaxError as e:
        return False

def save_file(base_path, rel_path, code):
    """Save code to file, creating directories if needed."""
    full_path = os.path.join(base_path, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"✅ Saved: {full_path}")

def run_entry_file(path):
    """Run the entry file."""
    print(f"▶️ Running entry file: {path}")
    result = subprocess.run([sys.executable, path], capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ Runtime error:\n", result.stderr)
    else:
        print("✅ Output:\n", result.stdout.strip())

# ---------------- LLM FUNCTIONS ----------------
def ask_model_for_structure(task):
    """Ask LLM for 3 project structure options."""
    prompt = f"""
You are a coding assistant.
Task: {task}

Provide 3 well-structured Python project folder/file organization options.
- Each option should be distinct.
- Include file names and folder structure.
- Do NOT include actual code yet, only structure.
- Number them 1, 2, 3.
"""
    response = client.chat.complete(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def ask_model_for_file(task, file_path, file_summary, existing_text=""):
    """Ask LLM to generate Python code for a single file."""
    prompt = f"""
You are a coding assistant.
Task: {task}

Generate code for '{file_path}' based on this summary:
{file_summary}

Existing project files:
{existing_text}

Rules:
- Output ONLY valid Python code (or valid config if .ini/.json)
- Do NOT include explanations, markdown, or prose
- If file is empty by design, include minimal valid placeholder
"""
    for attempt in range(3):
        try:
            response = client.chat.complete(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            code = clean_code(response.choices[0].message.content.strip())
            if validate_python(code, file_path) or file_path.endswith((".ini", ".json")):
                return code
        except sdkerror.SDKError:
            continue
    return None

# ---------------- BOT LOGIC ----------------
def create_project(task, project_path):
    os.makedirs(project_path, exist_ok=True)
    # 1️⃣ Get project structure options
    structure_text = ask_model_for_structure(task)
    print("📁 LLM proposed project structures:\n")
    print(structure_text)
    print("\nSelect one option (1/2/3): ", end="")
    choice = input().strip()
    if choice not in ["1","2","3"]:
        choice = "1"
    print(f"Selected option: {choice}\n")

    # Parse structure for file generation
    # LLM might output in markdown/code blocks; extract file paths
    file_paths = re.findall(r"[├└]──\s*(\S+)", structure_text)
    file_paths = [fp for fp in file_paths if fp.strip() != ""]

    # 2️⃣ Generate files one by one
    existing_files = []
    for file_path in file_paths:
        print(f"\n📝 Preparing to generate file: {file_path}")
        default_summary = f"'{file_path}' should implement appropriate functionality as part of the '{task}' project."
        print(f"Suggested summary for '{file_path}': {default_summary}")
        print("Do you want to modify the summary? (y/n): ", end="")
        if input().strip().lower() == "y":
            print("Enter your modified summary: ", end="")
            file_summary = input().strip()
        else:
            file_summary = default_summary

        code = ask_model_for_file(task, file_path, file_summary, "\n".join(existing_files))
        if not code:
            print(f"⚠️ Failed to generate valid Python for {file_path}. Skipping...")
            continue
        save_file(project_path, file_path, code)
        existing_files.append(f"{file_path}:\n{code}")

    # 3️⃣ Run entry file
    entry_file = os.path.join(project_path, "main.py")
    if os.path.exists(entry_file):
        run_entry_file(entry_file)
    else:
        print("⚠️ No entry file 'main.py' found. Cannot run automatically.")

# ---------------- RUN ----------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("task", help="Coding task for the AI")
    parser.add_argument("project_path", help="Where to save the project")
    args = parser.parse_args()

    create_project(args.task, args.project_path)
