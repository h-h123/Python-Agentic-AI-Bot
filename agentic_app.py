from mistralai import Mistral
from mistralai.models import sdkerror
import os, subprocess, argparse

# ---------------- SETUP ----------------
api_key = "CQx1GgPlnyr8IqqwbQmCFzFJH0dTj31k"
model = "mistral-medium"  # can switch to mistral-small if needed

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


def save_code(path, code):
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)


def run_code(path):
    result = subprocess.run(["python", path], capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip()


def create_project(task, project_path, max_attempts=5):
    os.makedirs(project_path, exist_ok=True)
    file_path = os.path.join(project_path, "main.py")

    error = None
    success = False
    final_output = None

    for attempt in range(1, max_attempts + 1):
        code = ask_model(task, error)

        if code is None:
            print(f"❌ Attempt {attempt}: Model unavailable (API error).")
            if attempt == max_attempts:
                print("🚨 Model unavailable after retries. Exiting.")
            continue

        save_code(file_path, code)
        out, err = run_code(file_path)

        if err:
            print(f"❌ Attempt {attempt}: Error while running code:\n{err}\nRetrying...\n")
            error = err
        else:
            print(f"✅ Attempt {attempt}: Code ran successfully.")
            print("Output:\n", out)
            success = True
            final_output = out
            break  # stop retrying once success is achieved

    # -------- Final Cross-check --------
    if success:
        print("🎉 Project created successfully at:", project_path)
    else:
        # last chance check: maybe code file exists and runs
        if os.path.exists(file_path):
            out, err = run_code(file_path)
            if not err:
                print("⚠️ Code was generated and runs, but loop thought it failed.")
                print("Output:\n", out)
                print("✅ Project created at:", project_path)
                return
        print("🚨 Could not generate a working project after retries.")


# ---------------- RUN EXAMPLE ----------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("task", help="The coding task for the AI")
    parser.add_argument("project_path", help="Where to save the project")
    args = parser.parse_args()

    create_project(args.task, args.project_path)

# ---------------- RUN EXAMPLE ----------------
# if __name__ == "__main__":
#     create_project(
#         "Make a Python scientific calculator app. Include 10 different operations. Exclude add, subtract, multiply, divide", #task
#         "./my_projects/scientific_calculator_app" #project_path
#     )


