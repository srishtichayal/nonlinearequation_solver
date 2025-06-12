from scipy.optimize import root
import numpy as np
import sympy as sp
import re
import ast
import random
import io
import contextlib
import math
random.seed(42) 

class Solution():
    def __init__(self):
        self.equations = []
        self.variables = []
        self.coefficients = {} 
        self.constantspath = None
    
    def process_equations(self, equations):
        """
        Removes '= 0' from each equation string.
        Assumes all equations are of the form 'expression = 0'.
        """
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
        '''Parameters:
        - variables: list of variable names as strings.
        - equations: list of equations as strings.
        - coefficients: dictionary of constant names and values.

        Returns:
        - f_lambdified: numerical function evaluating the equations.
        - sym_vars: symbolic variables in the same order as 'variables'.
        '''

        equations = self.process_equations(equations)
        self.get_variables(equations)
        sym_vars = sp.symbols(self.variables)
        var_map = dict(zip(self.variables, sym_vars))
        sym_table = {**var_map, **{k: sp.sympify(v) for k, v in self.coefficients.items()}}

        equations = [sp.sympify(eq_str, locals=sym_table) for eq_str in equations]
        f_lambdified = sp.lambdify(sym_vars, equations, modules='numpy')

        return f_lambdified, sym_vars

    def solution(self, equations, initial_guess=None, method='hybr'):
        '''Parameters:
        - coefficients: dictionary of named constants used in the equations.
        - variables: list of variable names as strings.
        - equations: list of equations as strings.
        - initial_guess: optional initial guess for the variables.
        - method: root-finding method ('hybr', 'lm', 'broyden1', etc.)

        Returns:
        - Dictionary mapping variable names to their solved values.
        '''
        
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

        def func(x):
            return np.array(f_lambdified(*x), dtype=np.float64)

        sol = root(func, initial_guesses, method=method)

        if not sol.success:
            raise ValueError(f"Solver failed: {sol.message}")
        
        output_log = io.StringIO()
        with contextlib.redirect_stdout(output_log):
            print("\nInitial Guess Used:")
            for var, val in zip(self.variables, initial_guesses):
                print(f" {var} = {val:.4f}")
            
            print("\nFinal Solution:")
            for var, val in zip(sym_vars, sol.x):
                print(f" {var} = {val:.6f}")

            print("\nResiduals: [")
            for i, val in enumerate(sol.fun):
                print(f" {val:.4e},")
            print("]")

            print(f"\nFinal Residual Norm: {np.linalg.norm(sol.fun):.4e}")

            if hasattr(sol, 'nfev'):
                print(f"Function Evaluations: {sol.nfev}")
        
        return {
            "solution_dict": {str(var): val for var, val in zip(sym_vars, sol.x)},
            "log": output_log.getvalue() 
        }