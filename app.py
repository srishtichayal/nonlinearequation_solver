from flask import Flask, render_template, request, jsonify
from core_runner import solve_equations
from core_runner import extract_var
import webbrowser
import threading
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extract_variables', methods=['POST'])
def extract_variables():
    data = request.json
    solver = data.get('solver')
    equations_raw = data.get('equations')
    constants_raw = data.get('constants', '')

    try:
        equations_raw = equations_raw.strip()

        # Step 1: Split into blocks if multiple equation blocks are separated by '---'
        eq_blocks = [block.strip() for block in equations_raw.split('---')]

        equations = []

        # Step 2: For each block, process each line
        for block in eq_blocks:
            lines = block.split('\n')
            for line in lines:
                # Remove comments and strip whitespace
                clean = line.split('#', 1)[0].strip()
                if clean:
                    equations.append(clean)


        # Now pass cleaned equations to your solver
        results = extract_var(solver, equations, constants_raw)

        output_str = ""
        for k in results:
            output_str += f"{k} = \n"

        return jsonify({"success": True, "solution": output_str})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/solve', methods=['POST'])
def solve(): 
    data = request.json
    solver = data.get('solver')
    equations_raw = data.get('equations')
    constants_raw = data.get('constants', '')
    initial_guesses = data.get('initial_guesses', '')

    try:
        equations_raw = equations_raw.strip()
        # Step 1: Split into blocks if multiple equation blocks are separated by '---'
        eq_blocks = [block.strip() for block in equations_raw.split('---')]

        equations = []

        # Step 2: For each block, process each line
        for block in eq_blocks:
            lines = block.split('\n')
            for line in lines:
                # Remove comments and strip whitespace
                clean = line.split('#', 1)[0].strip()
                if clean:
                    equations.append(clean)

        results = solve_equations(solver, equations, initial_guesses, constants_raw)

        return jsonify({"success": True, "solution": results['log']})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

_browser_opened = False  # Declare globally at the top

def open_browser_once():
    global _browser_opened  # So the function can access and modify the global variable
    if not _browser_opened:
        _browser_opened = True
        webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    # Safe browser opening that works across terminal and IDE
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Timer(1.0, open_browser_once).start()

    # You can set debug=False in production
    app.run(debug=True)
