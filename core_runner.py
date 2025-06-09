def extract_var(solver_name, equations_list, constants_str=None):
    if solver_name == "gekko":
        import gekko_solver as selected_solver
    elif solver_name == "scipyroot":
        import scipy_root_solver as selected_solver
    elif solver_name == "scipyls":
        import scipy_ls_solver as selected_solver
    elif solver_name == "numpy":
        import newton_raphson as selected_solver
    else:
        raise ValueError("Unknown solver specified.")
    
    s = selected_solver.Solution()

    if constants_str:
        from tempfile import NamedTemporaryFile
        with NamedTemporaryFile(delete=False, mode='w', suffix=".txt") as f:
            f.write(constants_str)
            s.constantspath = f.name
    
    equations_list = s.process_equations(equations_list)
    s.get_variables(equations_list)
    return s.variables

def solve_equations(solver_name, equations_list, initial_guesses=None, constants_str=None): 
    if solver_name == "gekko":
        import gekko_solver as selected_solver
    elif solver_name == "scipyroot":
        import scipy_root_solver as selected_solver
    elif solver_name == "scipyls":
        import scipy_ls_solver as selected_solver
    elif solver_name == "numpy":
        import newton_raphson as selected_solver
    else:
        raise ValueError("Unknown solver specified.")
    
    s = selected_solver.Solution()

    if constants_str:
        from tempfile import NamedTemporaryFile
        with NamedTemporaryFile(delete=False, mode='w', suffix=".txt") as f:
            f.write(constants_str)
            s.constantspath = f.name
    
    answers = s.solution(equations_list, initial_guess=initial_guesses)
    return answers
