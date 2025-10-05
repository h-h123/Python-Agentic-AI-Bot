# multi-python-bot.py
# Agentic Python Project Generator - One file at a time, interactive

from mistralai import Mistral
from mistralai.models import sdkerror
import os, sys, json, re, argparse, subprocess, time

# ---------------- SETUP ----------------
API_KEY = "CQx1GgPlnyr8IqqwbQmCFzFJH0dTj31k"
MODEL = "mistral-medium"
client = Mistral(api_key=API_KEY)

# ---------------- HELPERS ----------------
def ask_model_for_structures(task):
    """Ask LLM for top 3 project structure options"""
    prompt = f"""
    You are a coding assistant.
    Task: {task}

    Suggest **three different Python project structures** (folders/files) 
    suitable for this project. Show only valid filenames/folders.
    Include a **main entry file**. Use folder hierarchy like:
    folder/
        file.py
    Do not include code yet. Just structure options.
    """
    try:
        resp = client.chat.complete(model=MODEL, messages=[{"role":"user","content":prompt}])
        return resp.choices[0].message.content.strip()
    except sdkerror.SDKError as e:
        print(f"⚠️ SDK Error: {e}")
        return None

def ask_model_for_file(task, file_path, existing_files):
    """Ask LLM to generate code for a single file"""
    existing_text = json.dumps(existing_files, indent=2)
    prompt = f"""
    You are a coding assistant.
    Task: {task}

    Generate **Python code** for this file: {file_path}
    Existing files in project: {existing_text}

    Requirements:
    - Do not leave the file empty
    - Include at least minimal placeholder code if needed
    - Do not add markdown fences or explanations
    - Only output valid Python code (or valid config if file is .ini/.json)
    """
    try:
        resp = client.chat.complete(model=MODEL, messages=[{"role":"user","content":prompt}])
        return resp.choices[0].message.content.strip()
    except sdkerror.SDKError as e:
        print(f"⚠️ SDK Error: {e}")
        return None

def sanitize_filename(fname):
    """Remove comments or invalid chars"""
    fname = fname.split("#")[0].strip()
    if fname.endswith("/"):
        fname = fname[:-1]
    return fname

def save_file(project_root, file_path, code):
    """Save code to a file, creating folders if needed"""
    full_path = os.path.join(project_root, file_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"✅ Saved: {full_path}")

def run_entry_file(entry_file):
    """Run entry file and install missing packages if needed"""
    result = subprocess.run([sys.executable, entry_file], capture_output=True, text=True)
    out, err = result.stdout.strip(), result.stderr.strip()

    if "ModuleNotFoundError" in err:
        missing_pkg = err.split("'")[1]
        print(f"📦 Installing missing package: {missing_pkg} ...")
        subprocess.run([sys.executable, "-m", "pip", "install", missing_pkg])
        # Retry
        result = subprocess.run([sys.executable, entry_file], capture_output=True, text=True)
        out, err = result.stdout.strip(), result.stderr.strip()
    return out, err


def clean_code(code):
    """
    Remove markdown fences or unwanted leading/trailing characters
    so that only valid Python/code remains.
    """
    lines = code.splitlines()
    cleaned = []
    for line in lines:
        # skip code fences or triple backticks
        if line.strip().startswith("```"):
            continue
        # remove common LLM-generated prompts accidentally included
        if line.strip().startswith(("Here's", "File:", "Note:")):
            continue
        cleaned.append(line)
    return "\n".join(cleaned).strip()


# ---------------- CORE LOGIC ----------------
def create_project(task, project_root):
    os.makedirs(project_root, exist_ok=True)

    # Step 1: Ask LLM for structures
    structures_text = ask_model_for_structures(task)
    if not structures_text:
        print("❌ Could not get project structures. Exiting.")
        sys.exit(1)

    print("📁 LLM proposed project structures:\n")
    print(structures_text)
    print("\nSelect an option (1/2/3): ", end="")
    choice = input().strip()
    if choice not in ["1","2","3"]:
        print("Invalid choice, defaulting to Option 1")
        choice = "1"

    # Step 2: Parse chosen structure into files
    file_lines = [line.strip() for line in structures_text.splitlines() if line.strip()]
    files_to_create = []
    capture = False
    for line in file_lines:
        if f"Option {choice}" in line:
            capture = True
            continue
        if capture:
            if line.startswith("---"):  # end of option
                break
            if "│" in line or "├──" in line or "└──" in line:
                fname = line.split("──")[-1].strip()
                fname = sanitize_filename(fname)
                if fname and (fname.endswith(".py") or fname.endswith(".txt") or fname.endswith(".md") or fname.endswith(".json") or fname.endswith(".ini")):
                    files_to_create.append(fname)

    # Step 3: Generate files **one by one**
    existing_files = {}
    for file_path in files_to_create:
        print(f"\n📝 Generating file: {file_path}")
        for attempt in range(3):
            code = ask_model_for_file(task, file_path, existing_files)
            if code and code.strip():
                code = clean_code(code)
                save_file(project_root, file_path, code)
                existing_files[file_path] = code
                break
            else:
                print(f"⚠️ Attempt {attempt+1}: Empty code, retrying...")
                time.sleep(1)
        else:
            print(f"❌ Failed to generate code for {file_path}, skipping.")

    # Step 4: Detect entry file
    entry_file = None
    for f in existing_files:
        if "main.py" in f:
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
        print("⚠️ No entry file found. Please check manually.")

    print("\n🎉 Project generation completed.")

# ---------------- RUN ----------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("task", help="Describe the coding task for the AI")
    parser.add_argument("project_path", help="Where to save the project")
    args = parser.parse_args()

    create_project(args.task, args.project_path)
