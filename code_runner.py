import argparse
import time
import os

# --- Argument parser setup ---
parser = argparse.ArgumentParser(description="Run nonlinear equation solver.")

parser.add_argument(
    "--solver",
    choices=["gekko", "scipyroot", "scipyls", "numpy"],
    required=True,
    help="Choose the solver to use: 'gekko' or 'scipy'"
)

parser.add_argument(
    "--equations",
    required=True,
    nargs='+',  # Accepts one or more files
    help="One or more paths to equations files (required)"
)

parser.add_argument(
    "--constants",
    required=False,
    help="Optional path to coefficients file"
)

parser.add_argument(
    "--answers",
    required=False,
    help="Directory to save _Answers.txt (default: current directory)"
)

args = parser.parse_args()

# --- Select solver ---
if args.solver == "gekko":
    import gekko_solver as selected_solver
if args.solver == "scipyroot":
    import scipy_root_solver as selected_solver
if args.solver == "scipyls":
    import scipy_ls_solver as selected_solver
if args.solver == "numpy":
    import newton_raphson as selected_solver 


s = selected_solver.Solution()
if args.constants:
    s.constantspath = args.constants

# --- Output path ---
output_dir = args.answers if args.answers else os.getcwd()
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "_Answers.txt")

# --- Load equations ---
equations = []
for eq_file in args.equations:
    if not os.path.isfile(eq_file):
        raise FileNotFoundError(f"Equations file not found: {eq_file}")
    with open(eq_file, 'r') as f:
        for line in f:
            line = line.split('#', 1)[0].strip()  # Remove comments and trailing spaces
            if line:
                equations.append(line)

# --- Solve ---
start_time = time.time()
answers = s.solution(equations)
end_time = time.time()

# --- Save results ---
with open(output_path, 'a') as f:  # <-- Use append mode
    f.write(f"\n--- Solving---\n")
    f.write(f"Total time: {end_time - start_time:.4f} seconds\n")
    for key, value in answers.items():
        f.write(f"{key} = {value}\n")

        
        

