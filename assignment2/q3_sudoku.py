def read_puzzles(filename):
    puzzles = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if len(line) == 81:
                puzzles.append(line)
    return puzzles

def initialize_csp(puzzle):
    variables = [f'R{r}C{c}' for r in range(1, 10) for c in range(1, 10)]
    
    domains = {}
    for i, var in enumerate(variables):
        if puzzle[i] == '0':
            domains[var] = set(range(1, 10))
        else:
            domains[var] = {int(puzzle[i])}

    constraints = []
    # Row constraints
    for r in range(1, 10):
        row_vars = [f'R{r}C{c}' for c in range(1, 10)]
        for i in range(len(row_vars)):
            for j in range(i + 1, len(row_vars)):
                constraints.append((row_vars[i], row_vars[j]))
    
    # Column constraints
    for c in range(1, 10):
        col_vars = [f'R{r}C{c}' for r in range(1, 10)]
        for i in range(len(col_vars)):
            for j in range(i + 1, len(col_vars)):
                constraints.append((col_vars[i], col_vars[j]))
    
    # 3x3 box constraints
    for box_row in range(0, 3):
        for box_col in range(0, 3):
            box_vars = [
                f'R{r}C{c}' 
                for r in range(1 + box_row * 3, 4 + box_row * 3)
                for c in range(1 + box_col * 3, 4 + box_col * 3)
            ]
            for i in range(len(box_vars)):
                for j in range(i + 1, len(box_vars)):
                    constraints.append((box_vars[i], box_vars[j]))
    
    return variables, domains, constraints

def ac3(variables, domains, constraints):
    queue = constraints.copy()
    while queue:
        (xi, xj) = queue.pop(0)
        if revise(domains, xi, xj):
            if not domains[xi]:
                return False
            
            for (xk, xl) in constraints:
                if xk == xi and xl != xj:
                    queue.append((xl, xi))
                if xl == xi and xk != xj:
                    queue.append((xk, xi))
    return True

def revise(domains, xi, xj):
    revised = False
    values_to_remove = set()
    for x in domains[xi]:
        conflict = True
        for y in domains[xj]:
            if x != y:
                conflict = False
                break
        if conflict:
            values_to_remove.add(x)
            revised = True
    domains[xi] -= values_to_remove
    return revised

def select_unassigned_variable(assignment, variables, domains):
    unassigned = [var for var in variables if var not in assignment]
    return min(unassigned, key=lambda var: len(domains[var]), default=None)

def order_domain_values(var, domains):
    return list(domains[var])

def is_consistent(var, value, assignment, constraints):
    for (v1, v2) in constraints:
        if v1 == var and v2 in assignment:
            if value == assignment[v2]:
                return False
        if v2 == var and v1 in assignment:
            if value == assignment[v1]:
                return False
    return True

def backtrack(assignment, variables, domains, constraints):
    if len(assignment) == len(variables):
        return assignment
    var = select_unassigned_variable(assignment, variables, domains)
    if var is None:
        return None
    for value in order_domain_values(var, domains):
        if is_consistent(var, value, assignment, constraints):
            assignment[var] = value
           
            saved_domains = {v: domains[v].copy() for v in domains}
            domains[var] = {value}
            if ac3(variables, domains, constraints):
                result = backtrack(assignment, variables, domains, constraints)
                if result is not None:
                    return result
           
            domains.update(saved_domains)
            del assignment[var]
    return None

def solve_sudoku_csp(puzzle):
    variables, domains, constraints = initialize_csp(puzzle)
    
    if not ac3(variables, domains, constraints):
        return None
    assignment = {var: next(iter(domains[var])) for var in variables if len(domains[var]) == 1}
    result = backtrack(assignment, variables, domains, constraints)
    if result is None:
        return None
   
    solution = ['0'] * 81
    for r in range(1, 10):
        for c in range(1, 10):
            var = f'R{r}C{c}'
            solution[(r-1)*9 + (c-1)] = str(result[var])
    return ''.join(solution)

def main():
    puzzles = read_puzzles('sudoku.txt')
    for puzzle in puzzles:
        solution = solve_sudoku_csp(puzzle)
        if solution:
            print(solution)
        else:
            print("No solution")

if __name__ == "__main__":
    main()