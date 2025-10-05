from mistralai import Mistral
from mistralai.models import sdkerror
import os, subprocess, argparse, sys

# ---------------- SETUP ----------------
api_key = "CQx1GgPlnyr8IqqwbQmCFzFJH0dTj31k"
model = "mistral-medium"

client = Mistral(api_key=api_key)


# ---------------- BOT FUNCTIONS ----------------
def ask_model(task, error=None):
    """Ask Mistral to generate or fix code"""
    error_text = f"\nPrevious attempt failed with error:\n{error}" if error else ""
    prompt = f"""
    You are a coding assistant.
    Task: {task}
    {error_text}

    Write a complete working Python program.
    - ONLY output the Python code.
    - Do NOT include any explanations, comments, or backticks.
    - Do NOT write any text before or after the code.
    """

    try:
        response = client.chat.complete(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    except sdkerror.SDKError as e:
        print(f"⚠️ SDK Error: {e}")
        return None


# def save_code(path, code):
#     with open(path, "w", encoding="utf-8") as f:
#         f.write(code)
def save_code(path, code):
    # Clean out accidental markdown fences like ```python ... ```
    if code.strip().startswith("```"):
        code = "\n".join(
            line for line in code.splitlines()
            if not line.strip().startswith("```")
        )
    with open(path, "w", encoding="utf-8") as f:
        f.write(code.strip() + "\n")


# def run_code(path): #added functionality to install packages if missing
#     try:
#         result = subprocess.run(["python", path], capture_output=True, text=True)
#         return result.stdout.strip(), result.stderr.strip()
#     except ModuleNotFoundError as e:
#         missing_pkg = str(e).split("'")[1]  # extract package name
#         print(f"📦 Missing package: {missing_pkg}. Installing...")
#         subprocess.run(["pip", "install", missing_pkg])
#         # Retry once after installing
#         result = subprocess.run(["python", path], capture_output=True, text=True)
#         return result.stdout.strip(), result.stderr.strip()




#added functionality to install packages if missing. subprocess.run() never raises ModuleNotFoundError.Instead, it just returns the error as stderr text.That’s why except ModuleNotFoundError never runs.So code never reached the “📦 Missing package: … Installing...” part.
def run_code(path):
    result = subprocess.run([sys.executable, path], capture_output=True, text=True) #sys.executable points to the exact interpreter running.So both installation and code execution use the same environment.
    out, err = result.stdout.strip(), result.stderr.strip()

    if "ModuleNotFoundError" in err:
        missing_pkg = err.split("'")[1]
        print(f"📦 Missing package: {missing_pkg}. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", missing_pkg])
        # Retry with the same interpreter
        result = subprocess.run([sys.executable, path], capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip()

    return out, err


def validate_code(task, code):
    """Ask the model itself if the generated code matches the task"""
    prompt = f"""
    You are a strict code reviewer.
    Task: {task}

    Here is the generated code:
    {code}

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


def create_project(task, project_path, max_attempts=5, auto_run=False):
    os.makedirs(project_path, exist_ok=True)
    file_path = os.path.join(project_path, "main.py")

    error = None
    success = False
    final_code = None
    final_output = None

    for attempt in range(1, max_attempts + 1):
        code = ask_model(task, error)

        if code is None:
            print(f"❌ Attempt {attempt}: Model unavailable (API error).")
            if attempt == max_attempts:
                print("🚨 Model unavailable after retries. Exiting.")
            continue

        save_code(file_path, code)
        final_code = code

        if auto_run:
            out, err = run_code(file_path)
            if err:
                print(f"❌ Attempt {attempt}: Error while running code:\n{err}\nRetrying...\n")
                error = err
            else:
                print(f"✅ Attempt {attempt}: Code ran successfully.\nOutput:\n{out}")
                success = True
                final_output = out
                break
        else:
            print(f"✅ Code generated and saved at {file_path}")
            print("👉 Do you want to run it now? (y/n): ", end="")
            choice = input().strip().lower()
            if choice == "y":
                out, err = run_code(file_path)
                if err:
                    print(f"❌ Runtime error:\n{err}")
                else:
                    print("✅ Output:\n", out)
                    success = True
                    final_output = out
            break  # only one attempt if not auto_run

    # -------- Validation --------
    if final_code:
        valid, msg = validate_code(task, final_code)
        print(msg)
    else:
        valid = False

    # -------- Final Cross-check --------
    if success and valid:
        print("🎉 Project created successfully at:", project_path)
        sys.exit(0)
    elif success and not valid:
        print("⚠️ Code runs but may not fully match the task. Please review manually.")
        sys.exit(0)
    else:
        if os.path.exists(file_path):
            out, err = run_code(file_path)
            if not err:
                print("⚠️ Code was generated and runs, but loop thought it failed.")
                print("Output:\n", out)
                print("✅ Project created at:", project_path)
                sys.exit(0)
        print("🚨 Could not generate a working project after retries.")
        sys.exit(1)


# ---------------- RUN EXAMPLE ----------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("task", help="The coding task for the AI")
    parser.add_argument("project_path", help="Where to save the project")
    parser.add_argument("--auto-run", action="store_true", help="Run the generated code automatically")
    args = parser.parse_args()

    create_project(args.task, args.project_path, auto_run=args.auto_run)
