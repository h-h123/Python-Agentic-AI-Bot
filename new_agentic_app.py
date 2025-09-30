#Key Upgrades in This Version:
#Detects entry file automatically (any .py containing if __name__ == "__main__").
#Supports multi-file projects via JSON or === filename === blocks.
#Auto-installs missing packages.
#Prompts user to run entry file if not --auto-run.
#Validates entry file code using LLM itself.
#Cleans accidental markdown fences.
#Prints all saved file paths for confirmation.


from mistralai import Mistral
from mistralai.models import sdkerror
import os, subprocess, argparse, sys, json, re

# ---------------- SETUP ----------------
api_key = "CQx1GgPlnyr8IqqwbQmCFzFJH0dTj31k"
model = "mistral-medium"
client = Mistral(api_key=api_key)

# ---------------- BOT FUNCTIONS ----------------
def ask_model(task, error=None):
    """Ask Mistral to generate multi-file project"""
    error_text = f"\nPrevious attempt failed with error:\n{error}" if error else ""
    prompt = f"""
    You are a coding assistant.
    Task: {task}
    {error_text}

    Write a complete working Python project.
    - You can output multiple files.
    - Either output as a JSON object: keys are relative paths, values are code,
      OR as plain text blocks using:
      === filename ===
      <code here>
    - Only output code; no explanations or markdown fences.
    """
    try:
        response = client.chat.complete(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except sdkerror.SDKError as e:
        print(f"⚠️ SDK Error: {e}")
        return None

def parse_files_from_text(text):
    """Parse plain text blocks with === filename === sections"""
    files = {}
    pattern = re.compile(r"===\s*(.+?)\s*===\s*\n([\s\S]*?)(?=(?:\n===|$))", re.MULTILINE)
    for match in pattern.findall(text):
        filename, code = match
        code_lines = [line for line in code.splitlines() if not line.strip().startswith("```")]
        files[filename.strip()] = "\n".join(code_lines).strip() + "\n"
    return files

def save_project(project_path, files_dict):
    """Save multiple files from a dict {relative_path: code}"""
    for rel_path, code in files_dict.items():
        full_path = os.path.join(project_path, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"✅ Saved: {full_path}")

def run_code(path):
    """Run Python file with auto-install for missing packages"""
    result = subprocess.run([sys.executable, path], capture_output=True, text=True)
    out, err = result.stdout.strip(), result.stderr.strip()
    if "ModuleNotFoundError" in err:
        missing_pkg = err.split("'")[1]
        print(f"📦 Missing package: {missing_pkg}. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", missing_pkg])
        result = subprocess.run([sys.executable, path], capture_output=True, text=True)
        out, err = result.stdout.strip(), result.stderr.strip()
    return out, err

def validate_code(task, main_code):
    """Ask the model to validate the main entry file"""
    prompt = f"""
    You are a strict code reviewer.
    Task: {task}

    Here is the generated code of the main entry file:
    {main_code}

    Does this code fully satisfy the task requirements?
    - Answer only 'YES' or 'NO' in the first line.
    - If NO, provide a one-line reason after that.
    """
    try:
        response = client.chat.complete(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("YES"):
            return True, "✅ Code appears to meet the requirements."
        else:
            return False, f"⚠️ Validation feedback: {content}"
    except Exception as e:
        return False, f"⚠️ Validation failed: {e}"

def detect_entry_file(project_path):
    """Detect first Python file containing `if __name__ == '__main__'`"""
    for root, _, files in os.walk(project_path):
        for f in files:
            if f.endswith(".py"):
                full_path = os.path.join(root, f)
                with open(full_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    if 'if __name__' in content:
                        return full_path
    # Fallback: main.py
    return os.path.join(project_path, "main.py")

def create_project(task, project_path, max_attempts=5, auto_run=False):
    os.makedirs(project_path, exist_ok=True)
    error = None
    success = False
    files_dict = {}

    for attempt in range(1, max_attempts + 1):
        code_str = ask_model(task, error)
        if code_str is None:
            print(f"❌ Attempt {attempt}: Model unavailable (API error).")
            if attempt == max_attempts:
                print("🚨 Model unavailable after retries. Exiting.")
            continue

        # Try JSON first
        try:
            files_dict = json.loads(code_str)
        except json.JSONDecodeError:
            # Fallback to plain text parsing
            files_dict = parse_files_from_text(code_str)

        if not files_dict:
            print(f"❌ Attempt {attempt}: No files parsed. Retrying...")
            error = "No files parsed"
            continue

        save_project(project_path, files_dict)

        entry_file = detect_entry_file(project_path)
        if not os.path.exists(entry_file):
            print("⚠️ No entry file found. Cannot run or validate project.")
            continue

        if auto_run:
            out, err = run_code(entry_file)
            if err:
                print(f"❌ Attempt {attempt}: Error running entry file:\n{err}\nRetrying...")
                error = err
                continue
            print(f"✅ Entry file ran successfully.\nOutput:\n{out}")
            success = True
        else:
            print(f"👉 Do you want to run the entry file now? (y/n): ", end="")
            choice = input().strip().lower()
            if choice == "y":
                out, err = run_code(entry_file)
                if err:
                    print(f"❌ Runtime error:\n{err}")
                else:
                    print("✅ Output:\n", out)
                    success = True
        break  # one attempt if not auto_run

    # -------- Validation --------
    if entry_file and os.path.exists(entry_file):
        with open(entry_file, "r", encoding="utf-8") as f:
            main_code = f.read()
        valid, msg = validate_code(task, main_code)
        print(msg)
    else:
        valid = False

    if success and valid:
        print("🎉 Project created successfully at:", project_path)
        sys.exit(0)
    elif success and not valid:
        print("⚠️ Code runs but may not fully match the task. Please review manually.")
        sys.exit(0)
    else:
        print("🚨 Could not generate a working project after retries.")
        sys.exit(1)

# ---------------- RUN ----------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("task", help="The coding task for the AI")
    parser.add_argument("project_path", help="Where to save the project")
    parser.add_argument("--auto-run", action="store_true", help="Run the generated code automatically")
    args = parser.parse_args()

    create_project(args.task, args.project_path, auto_run=args.auto_run)
