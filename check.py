# multi-python-bot.py
# Agentic Python Project Generator - JSON-based Folder Structure (with src-safe imports)

from mistralai import Mistral
from mistralai.models import sdkerror
import os, sys, json, argparse, subprocess, time, importlib

# ---------------- SETUP ----------------
API_KEY = "CQx1GgPlnyr8IqqwbQmCFzFJH0dTj31k"
MODEL = "mistral-medium"
client = Mistral(api_key=API_KEY)

# ---------------- HELPERS ----------------
def ask_model_for_json_structure(task):
    """Ask LLM to return ONE project structure in JSON form."""
    prompt = f"""
    You are an expert Python project designer.

    Task: {task}

    Respond **only** with a valid JSON object describing the folder structure,
    not markdown text or explanations.

    Example format:
    {{
        "project_name": "sample_project",
        "structure": {{
            "src": {{
                "__init__.py": "",
                "main.py": "",
                "utils": {{
                    "__init__.py": "",
                    "helpers.py": ""
                }}
            }},
            "README.md": "# Sample Project"
        }}
    }}

    Important:
    - Use only valid JSON syntax.
    - Every file must end with .py, .md, .json, or .ini.
    - Include at least one main entry file (e.g., main.py or app.py).
    - Keep folder depth realistic (max 3 levels).
    """
    try:
        resp = client.chat.complete(model=MODEL, messages=[{"role": "user", "content": prompt}])
        content = resp.choices[0].message.content.strip()
        json_str = content[content.find("{"):content.rfind("}") + 1]
        return json.loads(json_str)
    except Exception as e:
        print(f"⚠️ Failed to parse JSON structure: {e}")
        print("Raw response:", resp.choices[0].message.content if 'resp' in locals() else "")
        return None


def ask_model_for_file(task, file_path, existing_files):
    """Ask LLM to generate code for a single file."""
    existing_text = json.dumps(existing_files, indent=2)
    prompt = f"""
    You are a coding assistant.
    Task: {task}

    Generate **Python code** for this file: {file_path}
    Existing project files: {existing_text}

    Requirements:
    - Do not leave the file empty.
    - No explanations, only valid code.
    - No markdown fences (```).
    """
    try:
        resp = client.chat.complete(model=MODEL, messages=[{"role": "user", "content": prompt}])
        return resp.choices[0].message.content.strip()
    except sdkerror.SDKError as e:
        print(f"⚠️ SDK Error: {e}")
        return None


def clean_code(code):
    """Remove markdown fences or unwanted text."""
    lines = []
    for line in code.splitlines():
        if line.strip().startswith("```") or line.strip().lower().startswith("file:"):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def save_file(project_root, rel_path, code):
    """Create folder hierarchy and save code."""
    full_path = os.path.join(project_root, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    # ✅ Option B — inject sys.path fix into main/app files
    if os.path.basename(rel_path) in ("main.py", "app.py"):
        inject = (
            "import sys, os\n"
            "sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))\n\n"
        )
        if inject not in code:
            code = inject + code

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"✅ Saved: {rel_path}")


def build_structure_from_json(project_root, structure_dict):
    """Recursively create all folders/files from JSON description."""
    created_files = []
    for name, value in structure_dict.items():
        path = os.path.join(project_root, name)
        if isinstance(value, dict):
            os.makedirs(path, exist_ok=True)
            sub_files = build_structure_from_json(path, value)
            created_files.extend([os.path.join(name, sf) for sf in sub_files])
        else:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(value or "")
            created_files.append(name)
    return created_files

# ---------------- SAFE IMPORT LOGIC ----------------
def safe_import_or_install(project_root, entry_file):
    """
    Try to run and fix missing imports.
    - If missing module is local (exists inside project_root), add to sys.path.
    - If external, install via pip once.
    """
    # ✅ Option A — ensure project_root on sys.path before running anything
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    result = subprocess.run([sys.executable, entry_file], capture_output=True, text=True)
    out, err = result.stdout.strip(), result.stderr.strip()

    if "ModuleNotFoundError" in err:
        missing_pkg = err.split("'")[1]
        local_path = os.path.join(project_root, missing_pkg)
        if os.path.isdir(local_path):
            print(f"🔹 Detected local module '{missing_pkg}', adding to sys.path dynamically.")
            sys.path.insert(0, project_root)
            result = subprocess.run([sys.executable, entry_file], capture_output=True, text=True)
            out, err = result.stdout.strip(), result.stderr.strip()
        else:
            print(f"📦 Installing missing external package: {missing_pkg} ...")
            subprocess.run([sys.executable, "-m", "pip", "install", missing_pkg])
            result = subprocess.run([sys.executable, entry_file], capture_output=True, text=True)
            out, err = result.stdout.strip(), result.stderr.strip()

    return out, err


def run_entry_file(entry_file):
    """Run entry file with safe import handling."""
    project_root = os.path.dirname(entry_file)
    out, err = safe_import_or_install(project_root, entry_file)
    return out, err

# ---------------- CORE LOGIC ----------------
def create_project(task, project_root):
    os.makedirs(project_root, exist_ok=True)

    # Step 1 — Ask LLM for JSON-based structure
    structure_json = ask_model_for_json_structure(task)
    if not structure_json or "structure" not in structure_json:
        print("❌ Could not get valid JSON structure. Exiting.")
        sys.exit(1)

    project_name = structure_json.get("project_name", "generated_project")
    structure = structure_json["structure"]

    print(f"\n📁 Generating project: {project_name}")
    print(json.dumps(structure, indent=2))

    # Step 2 — Build folder hierarchy & empty files
    created_files = build_structure_from_json(project_root, structure)

    # Step 3 — Fill each file with code
    existing_files = {}
    for file_path in created_files:
        if not file_path.endswith((".py", ".json", ".ini")):
            continue
        print(f"\n📝 Generating code for: {file_path}")
        for attempt in range(3):
            code = ask_model_for_file(task, file_path, existing_files)
            if code:
                code = clean_code(code)
                save_file(project_root, file_path, code)
                existing_files[file_path] = code
                break
            else:
                print(f"⚠️ Attempt {attempt + 1}: Empty output, retrying...")
                time.sleep(1)
        else:
            print(f"❌ Failed to generate code for {file_path}")

    # Step 4 — Run main/entry file
    entry_file = None
    for f in existing_files:
        if f.endswith("main.py") or f.endswith("app.py"):
            entry_file = os.path.join(project_root, f)
            break

    if entry_file and os.path.exists(entry_file):
        print(f"\n▶️ Running entry file: {entry_file}")
        out, err = run_entry_file(entry_file)
        if err:
            print(f"❌ Runtime error:\n{err}")
        else:
            print(f"✅ Output:\n{out}")
    else:
        print("⚠️ No entry file found.")

    print("\n🎉 Project generation complete.")
    
# ---------------- RUN ----------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("task", help="Describe the coding task for the AI")
    parser.add_argument("project_path", help="Where to save the project")
    args = parser.parse_args()

    create_project(args.task, args.project_path)
