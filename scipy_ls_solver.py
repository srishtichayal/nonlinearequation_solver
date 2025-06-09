from scipy.optimize import least_squares
import numpy as np
import sympy as sp
import re
import ast
import random
import io
import contextlib
random.seed(42)

class Solution():
    def __init__(self):
        self.equations = []
        self.variables = []
        self.coefficients = {}
        self.constantspath = None

    def process_equations(self, equations):
        self.equations = [eq.split('=')[0].strip() for eq in equations]
        return self.equations

    def safe_eval(self, expr):
        node = ast.parse(expr, mode='eval')
        for subnode in ast.walk(node):
            if not isinstance(subnode, (
                ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
                ast.operator, ast.unaryop
            )):
                raise ValueError(f"Disallowed expression: '{expr}'")
        return eval(expr, {"__builtins__": {}})

    def parse_constants_file(self):
        if self.constantspath:
            filepath = self.constantspath
            with open(filepath, 'r') as file:
                for line in file:
                    line = line.strip()
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        try:
                            self.coefficients[key] = self.safe_eval(value)
                        except Exception as e:
                            raise ValueError(f"Invalid expression for '{key}': '{value}' → {e}")

    def get_variables(self, equations):
        self.parse_constants_file()
        var_pattern = re.compile(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b')
        to_remove = set(['sin', 'cos', 'tan', 'sqrt', 'log', 'ln', 'exp', 'pi']) | set(self.coefficients.keys())
        variables = set()
        for eq in equations:
            for var in var_pattern.findall(eq):
                if var not in to_remove:
                    variables.add(var)
        self.variables = list(variables)

    def create_symbolic_system(self, equations):
        equations = self.process_equations(equations)
        self.get_variables(equations)
        sym_vars = sp.symbols(self.variables)
        var_map = dict(zip(self.variables, sym_vars))
        sym_table = {**var_map, **{k: sp.sympify(v) for k, v in self.coefficients.items()}}
        equations = [sp.sympify(eq_str, locals=sym_table) for eq_str in equations]
        f_lambdified = sp.lambdify(sym_vars, equations, modules='numpy')
        return f_lambdified, sym_vars

    def solution(self, equations, initial_guess=None):
        f_lambdified, sym_vars = self.create_symbolic_system(equations)

        if initial_guess is None:
            initial_guesses = np.random.uniform(0, 2, size=len(self.variables))
        else:
            initial_guesses = []
            for var in self.variables:
                if var in initial_guess:
                    initial_guesses.append(initial_guess[var])
                else:
                    initial_guesses.append(random.uniform(0, 2))

        # Start capturing output
        output_log = io.StringIO()
        with contextlib.redirect_stdout(output_log):
            def func(x):
                return np.array(f_lambdified(*x), dtype=np.float64)

            print("\nInitial Guess Used:")
            for var, val in zip(self.variables, initial_guesses):
                print(f"{var} = {val:.4f}")

            print("\n--- Solving Using Least Squares ---")
            sol = least_squares(func, initial_guesses, verbose=2)

            if not sol.success:
                raise ValueError(f"Solver failed: {sol.message}")

            print("\nFinal Solution:")
            for var, val in zip(sym_vars, sol.x):
                print(f"{var} = {val:.6f}")

            print("\nResiduals: [")
            for val in sol.fun:
                print(f" {val:.4e},")
            print("]")

            print(f"\nFinal Residual Norm: {np.linalg.norm(sol.fun):.4e}")
            print(f"Function Evaluations (Total nfev): {sol.nfev}")
            print(f"Jacobian Evaluations (Total njev): {sol.njev}")

        return {
            "solution_dict": {str(var): val for var, val in zip(sym_vars, sol.x)},
            "log": output_log.getvalue()  # This will include verbose=2 output
        }
