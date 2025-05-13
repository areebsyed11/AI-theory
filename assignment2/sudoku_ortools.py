from ortools.constraint_solver import pywrapcp

def read_puzzles(filename):
    puzzles = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if len(line) == 81:
                puzzles.append(line)
    return puzzles

def solve_sudoku_ortools(puzzle):
    solver = pywrapcp.Solver("Sudoku")
    grid = {}
    # Create variables
    for i in range(9):
        for j in range(9):
            grid[(i, j)] = solver.IntVar(1, 9, f'cell_{i}_{j}')
    
    # Add initial values
    for i in range(9):
        for j in range(9):
            pos = i * 9 + j
            if puzzle[pos] != '0':
                solver.Add(grid[(i, j)] == int(puzzle[pos]))
    
    # Row constraints
    for i in range(9):
        solver.Add(solver.AllDifferent([grid[(i, j)] for j in range(9)]))
    
    # Column constraints
    for j in range(9):
        solver.Add(solver.AllDifferent([grid[(i, j)] for i in range(9)]))
    
    # 3x3 box constraints
    for box_i in range(0, 9, 3):
        for box_j in range(0, 9, 3):
            cells = [grid[(i, j)] for i in range(box_i, box_i + 3) for j in range(box_j, box_j + 3)]
            solver.Add(solver.AllDifferent(cells))
    
    # Collect all variables
    all_vars = [grid[(i, j)] for i in range(9) for j in range(9)]
    
    # Decision builder
    db = solver.Phase(all_vars, solver.CHOOSE_FIRST_UNBOUND, solver.ASSIGN_MIN_VALUE)
    
    # Solve
    solver.NewSearch(db)
    if solver.NextSolution():
        solution = ['0'] * 81
        for i in range(9):
            for j in range(9):
                solution[i * 9 + j] = str(grid[(i, j)].Value())
        solver.EndSearch()
        return ''.join(solution)
    solver.EndSearch()
    return None

def main():
    puzzles = read_puzzles('sudoku.txt')
    for puzzle in puzzles:
        solution = solve_sudoku_ortools(puzzle)
        if solution:
            print(solution)
        else:
            print("No solution")

if __name__ == "__main__":
    main()