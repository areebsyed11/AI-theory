def read_puzzles(filename):
    puzzles = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if len(line) == 81:
                puzzles.append(line)
    return puzzles

def is_valid(board, row, col, num):
    # Check row
    for x in range(9):
        if board[row][x] == num:
            return False
    
    # Check column
    for x in range(9):
        if board[x][col] == num:
            return False
    
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[i + start_row][j + start_col] == num:
                return False
    return True

def solve_sudoku_chatgpt(board):
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                for num in range(1, 10):
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        if solve_sudoku_chatgpt(board):
                            return True
                        board[row][col] = 0
                return False
    return True

def puzzle_to_board(puzzle):
    board = [[0] * 9 for _ in range(9)]
    for i in range(9):
        for j in range(9):
            pos = i * 9 + j
            board[i][j] = int(puzzle[pos]) if puzzle[pos] != '0' else 0
    return board

def board_to_string(board):
    return ''.join(str(board[i // 9][i % 9]) for i in range(81))

def main():
    puzzles = read_puzzles('sudoku.txt')
    for puzzle in puzzles:
        board = puzzle_to_board(puzzle)
        if solve_sudoku_chatgpt(board):
            print(board_to_string(board))
        else:
            print("No solution")

if __name__ == "__main__":
    main()