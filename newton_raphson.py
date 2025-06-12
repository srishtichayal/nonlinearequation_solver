import numpy as np
import sympy as sp
import ast
import re
import random
import io
import contextlib
import math
random.seed(42)

class Solution:
    def __init__(self):
        self.equations = []
        self.variables = []
        self.coefficients = {}
        self.constantspath = None

    def process_equations(self, equations):
        return [eq.split('=')[0].strip() for eq in equations]

    def parse_constants_file(self):
        if self.constantspath:
            filepath = self.constantspath
            with open(filepath, 'r') as file:
                lines = file.readlines()

            # First, preprocess lines to strip comments and empty lines
            cleaned_lines = []
            for line in lines:
                line = line.split('#', 1)[0].strip()  # remove comment and trim
                if line:  # skip empty lines
                    cleaned_lines.append(line)

            # Allowed math functions/constants
            safe_math = {
                'sqrt': math.sqrt,
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
                'log': math.log,  # natural log
                'ln': math.log,   # alias for natural log
                'exp': math.exp,
                'pi': math.pi,
                'e': math.e
            }

            # Evaluate constants in order; constants may depend on previous ones
            for line in cleaned_lines:
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    try:
                        # Combine safe math functions with previously defined constants
                        self.coefficients[key] = eval(value, {"__builtins__": {}}, {**safe_math, **self.coefficients})
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
        sym_eqs = [sp.sympify(eq_str, locals=sym_table) for eq_str in equations]
        jacobian = sp.Matrix(sym_eqs).jacobian(sym_vars)

        f_lambdified = sp.lambdify(sym_vars, sym_eqs, modules='numpy')
        jac_lambdified = sp.lambdify(sym_vars, jacobian, modules='numpy')
        return f_lambdified, jac_lambdified, sym_vars

    def solution(self, equations, initial_guess=None, tol=1e-6, max_iter=50):
        f_lambdified, jac_lambdified, sym_vars = self.create_symbolic_system(equations)

        if initial_guess is None:
            x = np.random.uniform(0, 2, size=len(self.variables))
        else:
            x = []
            for var in self.variables:
                if var in initial_guess:
                    x.append(initial_guess[var])
                else:
                    x.append(random.uniform(0, 2))

        output_log = io.StringIO()
        with contextlib.redirect_stdout(output_log):
            print("\nSolving using Newton's Raphson Method:")
            print("\nInitial Guess Used:")
            for var, val in zip(self.variables, x):
                print(f" {var} = {val:.4f}")

            for iteration in range(max_iter):
                F = np.array(f_lambdified(*x), dtype=np.float64)
                J = np.array(jac_lambdified(*x), dtype=np.float64)

                if np.linalg.norm(F) < tol:
                    print(f"\nConverged in {iteration} iterations")
                    break

                try:
                    delta = np.linalg.solve(J, -F)
                except np.linalg.LinAlgError:
                    raise ValueError("Jacobian is singular. Cannot proceed.")

                x += delta

                print(f"\nIteration {iteration + 1}:")
                print(" Residuals: ", np.round(F, 6))
                print(" Residual Norm: ", np.linalg.norm(F))

            else:
                raise ValueError("Newton method did not converge within the maximum number of iterations.")

            print("\nFinal Solution:")
            for var, val in zip(sym_vars, x):
                print(f" {var} = {val:.6f}")

            print("\nResiduals:")
            for i, res in enumerate(F):
                print(f"Eq{i+1}: {res:.6e}")       
            print(f"\nFinal Residual Norm: {np.linalg.norm(F):.4e}")

        return {
            "solution_dict": {str(var): val for var, val in zip(sym_vars, x)},
            "log": output_log.getvalue()  
        }
