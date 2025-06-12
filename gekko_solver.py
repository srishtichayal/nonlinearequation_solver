from gekko import GEKKO
from sympy import *
import re
import ast
import random
import contextlib
import io
import math
random.seed(42) 

class Solution():
    def __init__(self):
        self.equations = []
        self.variables = []
        self.coefficients = {} 
        self.constantspath = None

    def process_equations(self, equations):
        # for i in range(len(equations)):
        #     equations[i] = re.sub(r'e\*\*', 'e', equations[i])
        equations = [x.replace('=', '==') for x in equations]
        equations = [x.replace('sin', 'm.sin') for x in equations]
        equations = [x.replace('cos', 'm.cos') for x in equations]
        equations = [x.replace('tan', 'm.tan') for x in equations]
        equations = [x.replace('sqrt', 'm.sqrt') for x in equations]
        equations = [x.replace('log', 'm.log') for x in equations]
        equations = [x.replace('ln', 'm.log') for x in equations]
        #equations = [x.replace('exp', '2.718281828459') for x in equations]
        equations = [x.replace('pi', 'm.pi') for x in equations]
        equations = [x.replace('exp', 'm.exp') for x in equations]
        #equations = [x.replace('e', '2.718281828459') for x in equations]
        #equations = [x.replace('E', '2.718281828459') for x in equations]
        return equations
                        

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
        

    def solution(self, equations, initial_guess=None):  # initial_guess is a dictionary
        original_eqs = [eq.strip() for eq in equations]  # keep original for residuals
        equations = self.process_equations(equations)
        self.get_variables(equations)
        m = GEKKO(remote=False)

        if initial_guess is None:
            g_vars = {var: m.Var(value=random.uniform(0, 2), name=var) for var in self.variables}
        else:
            g_vars = {}
            for var in self.variables:
                if var in initial_guess:
                    g_vars[var] = m.Var(value=initial_guess[var], name=var)
                else:
                    g_vars[var] = m.Var(value=random.uniform(0, 2), name=var)

        # Inject coefficient values directly into locals
        local_context = {**g_vars, **self.coefficients, "m": m}

        # Add equations
        for eq_str in equations:
            m.Equation(eval(eq_str, {}, local_context))

        output_log = io.StringIO()
        with contextlib.redirect_stdout(output_log):
            print("\nSolving using GEKKO: ")
            m.solve(disp=True)
            solution_dict = {str(var): g_vars[var].value[0] for var in self.variables if var != 'm'}
            print("\nFinal Solution: ")
            for var, val in solution_dict.items():
                print(f"{var} = {val:.6f}")

            # --- Residual Computation ---
            print("\nResiduals:")
            sym_table = {k: v for k, v in solution_dict.items()}
            sym_table.update(self.coefficients)
            sym_table.update({
                'sqrt': math.sqrt, 'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
                'log': math.log, 'ln': math.log, 'exp': math.exp, 'pi': math.pi, 'e': math.e
            })

            for i, eq in enumerate(original_eqs, 1):
                try:
                    # Convert equation to residual form: lhs - rhs
                    lhs, rhs = eq.split('=')
                    lhs_val = eval(lhs.strip(), {}, sym_table)
                    rhs_val = eval(rhs.strip(), {}, sym_table)
                    residual = lhs_val - rhs_val
                    print(f"Eq{i}: {residual:.6e}")
                except Exception as e:
                    print(f"Eq{i}: Could not compute residual → {e}")

        return {
            "solution_dict": solution_dict,
            "log": output_log.getvalue()
        }
