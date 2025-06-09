from flask import Flask, render_template, request, jsonify
from core_runner import solve_equations
from core_runner import extract_var
import webbrowser
import threading

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
        eq_blocks = [block.strip().split('\n') for block in equations_raw.split('---')]
        equations = [eq.strip() for block in eq_blocks for eq in block if eq.strip()]
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
        eq_blocks = [block.strip().split('\n') for block in equations_raw.split('---')]
        equations = [eq.strip() for block in eq_blocks for eq in block if eq.strip()]
        results = solve_equations(solver, equations, initial_guesses, constants_raw)

        return jsonify({"success": True, "solution": results['log']})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    import os
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        # This only runs once — after reloader kicks in
        threading.Timer(1.0, open_browser).start()
    app.run(debug=True)