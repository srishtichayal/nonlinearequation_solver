# Nonlinear Equation Solver

This project provides a flexible Python implementation for solving nonlinear equations, including **coupled systems** of equations. It supports multiple solvers and offers both an interactive web interface and command line execution.

---

## Supported Solvers

- **SciPy `optimize.root`**:  
  Uses a variety of root-finding algorithms (e.g., hybrid, Broyden, Newton-Krylov) to find zeros of a function by iteratively improving guesses. The algorithm used in this implementation is hybrid. 

- **SciPy `optimize.least_squares`**:  
  Minimizes the sum of squares of nonlinear functions to solve systems using algorithms like Levenberg-Marquardt, suitable for nonlinear least squares problems.

- **Gekko**:  
  A powerful Python package for mixed-integer and differential algebraic equation (DAE) optimization, leveraging advanced solvers like IPOPT.

- **Newton-Raphson (NumPy based)**:  
  A classical iterative method using function values and derivatives (Jacobian) to converge quickly on roots, implemented with NumPy operations.

---

## Setup

Install required dependencies using:

```bash
pip install -r requirements.txt
```

---

## Usage

### Interactive Web App

A Flask interface lets you interactively:

- Edit your equations and constants
- Upload `.txt` files from your local machine
- View and download the computed answers

To launch the app:

```bash
python app.py
```

Then open the link shown in your terminal (usually [http://127.0.0.1:5000/](http://127.0.0.1:5000/)).

---

### Command Line Execution

Run the solver directly via:

```bash
python code_runner.py
```

**Options:**

- `--solver`: Choose the solver to use (`scipyls`, `scipyroot`, `numpy` or `gekko`) **(Required)**
- `--equations`: Path(s) to your equation text file(s) **(Required)**
- `--constants`: Path to your constants/coefficients text file **(Optional)**
- `--answers`: Path to directory for output file (`_Answers.txt`) **(Optional, defaults to current directory)**

---

### Example

This implementation supports **multiple equation files**, allowing you to solve coupled systems of equations. It also lets you provide initial guesses via the web interface. The command line version generates random initial guesses automatically.

#### Important Notes:

- If using the Flask interface, upload **all equation files** (one file contains one system).
- If running from the command line, provide all equation files as arguments to `--equations`.

---

#### Sample equation file: `_Equations.txt`

```
5-z*abc+23*9*b-23*20*abc**2+23*20*b**2 = 0
100*abc-z*b+23*9*c-23*20*b**2+23*20*c**2 = 0
100*b-z*c+23*9*d-23*20*c**2+23*20*d**2 = 0
100*c-z*d+23*9*k-23*20*d**2+23*20*k**2 = 0
100*d-z*k+23*9*f-23*20*k**2+23*20*f**2 = 0
100*k-z*f+23*9*g-23*20*f**2+23*20*g**2 = 0
0.039+100*f+__z__*g-9*10*h+20*23*g**2-20*10*h**2 = 0
100*g-_z_*h-9*10*i-20*10*h**2-20*10*i**2 = 0
100*h-_z_*i-9*10*j-20*10*i**2-20*10*j**2 = 0
100*i-_z_*j-20*10*j**2 = 0
```

---

#### Sample constants file: `_Coefficients.txt`

```
z=100+23*9
_z_=100+9*10
__z__=-100+9*23
```

---

#### Running the solver:

```bash
python code_runner.py --solver scipyls --equations _Equations.txt --constants _Coefficients.txt
```

Output (in `_Answers.txt` in current directory by default):

```
--- Solving---
Total time: 0.1138 seconds
solution_dict = {'h': -0.00018293361411102652, 'f': -0.00010933156211938929, 'abc': 0.022650801201351156, 'c': 0.0045853284172748645, 'g': -0.00041686085686591716, 'b': 0.010341116968465323, 'k': 0.0005265097079217704, 'i': -7.707311110913585e-05, 'j': -4.056652757655531e-05, 'd': 0.0018439213286844487}
log = 
Initial Guess Used:
h = 0.2470
f = 0.7938
abc = 0.3704
c = 1.7184
g = 1.5009
b = 1.9405
k = 1.7941
i = 1.0769
j = 1.7937
d = 0.2401

--- Solving Using Least Squares ---
   Iteration     Total nfev        Cost      Cost reduction    Step norm     Optimality   
       0              1         8.8695e+06                                    6.71e+06    
       1              2         4.9881e+05      8.37e+06       2.27e+00       8.32e+05    
       2              3         2.7850e+04      4.71e+05       1.15e+00       1.09e+05    
       3              4         1.2433e+03      2.66e+04       5.45e-01       1.44e+04    
       4              5         2.3561e+01      1.22e+03       2.09e-01       1.85e+03    
       5              6         4.3486e-02      2.35e+01       4.16e-02       9.47e+01    
       6              7         1.4638e-07      4.35e-02       1.66e-03       1.66e-01    
       7              8         7.2247e-19      1.46e-07       2.32e-06       3.91e-07    
       8              9         1.5874e-30      7.22e-19       3.90e-12       5.93e-13    
`gtol` termination condition is satisfied.
Function evaluations 9, initial cost 8.8695e+06, final cost 1.5874e-30, first-order optimality 5.93e-13.

Final Solution:
h = -0.000183
f = -0.000109
abc = 0.022651
c = 0.004585
g = -0.000417
b = 0.010341
k = 0.000527
i = -0.000077
j = -0.000041
d = 0.001844

Residuals: [
 -1.7764e-15,
 1.1102e-16,
 -5.5511e-17,
 5.5511e-17,
 -2.7756e-17,
 0.0000e+00,
 -6.9389e-18,
 -7.8063e-18,
 3.0358e-18,
 0.0000e+00,
]

Final Residual Norm: 1.7818e-15
Function Evaluations (Total nfev): 9
Jacobian Evaluations (Total njev): 9

```

---

#### Multiple Equation Files Example

Suppose you have two equation files: `equations.txt` and `equations1.txt` representing coupled systems, and a constants file `constants.txt` with coefficients. You can provide them all to the solver like:

```bash
python code_runner.py --solver scipyls --equations equations.txt equations1.txt --constants constants.txt
```

---

## Guidelines for Writing Equations and Constants
### Equations
1. Each equation must be written in the form expression = 0.
   e.g: (write ```a*x**2 + b*x + c = 0``` instead of ```a*x**2 + b*x + c```)
2. Do not define any constants in the equations file.
   e.g: (define ```a = 5``` in the constants file instead of the equations file)
3. Use ** for powers instead of ^.
   e.g: (write ```x**2``` instead of ```x^2```)
4. Use * for multiplication, even between constants and variables.
   e.g: (write ```a*b``` instead of ```ab```, and ```2*x``` instead of ```2x```)
5. Use exp(x) for exponentials instead of ```e**x```.
   e.g: (write ```exp(g)``` instead of ```e**g```)
6. Allowed math functions: sqrt, sin, cos, tan, log, ln, exp, pi.
   e.g: (write ```sqrt(x) + cos(pi/4)``` instead of custom or undefined math)
7. e has no special meaning in equations, it will be treated as a normal variable or constant name.
   e.g: (write exp(1) if you mean Euler’s number, not e)

### Constants
1. All constants must be defined numerically in the constants file.
   e.g: (write g = 9.8 in the constants file, not in the equations)
2. Constants can depend on other constants, just define them in the correct order.
   e.g: (write ```a = 2```, ```b = sqrt(a) + 1```, with a above b)
3. Constants must be fully numeric — they cannot depend on any variables.
   e.g: (write ```k = 2*pi``` instead of ```k = 2*x```)
4. Allowed functions in constants: sqrt, sin, cos, tan, log, ln, exp, pi.
   e.g: (write ```theta = cos(pi/3)```)
5. e will be interpreted as Euler's number by default, unless explicitly redefined.
   e.g: (by default: e = exp(1), or you can write e = 2 to override)
6. Avoid using names that contain math function names (like sin, cos, tan, sqrt, log, ln, exp, pi) when using the Gekko solver.
   e.g: (write k_sine instead of ksin, or lambda_val instead of lexp)

### General Rules
1. Variable and constant names must be different.
   e.g: (use x as a variable and a as a constant, not both named x)
2. Names can contain letters and underscores, but cannot start with a number.
   e.g: (use temp_1, _k, or lambda_val instead of 2value or a*b)
3. Lines starting with # are treated as comments and ignored. Any text after # in a line is ignored.
   e.g: (write ```# this is a comment``` or ```a = 3  # acceleration constant```)


---

## References

- [SciPy `optimize.root`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.root.html)
- [SciPy `optimize.least_squares`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.least_squares.html)
- [Gekko Documentation](https://gekko.readthedocs.io/en/latest/)
- Newton-Raphson method references




