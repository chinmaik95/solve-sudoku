from pprint import pprint
import copy

def test_cell(s, row, col):
    """
    Given a Sudoku puzzle s, row, and column number, return a list which represents
    the valid numbers that can go in that cell. 0 = possible, 1 = not possible
    """
    used = [0]*10
    used[0] = 1
    block_row = row // 3
    block_col = col // 3

    # Row and Column
    for m in range(9):
        used[s[m][col]] = 1;
        used[s[row][m]] = 1;

    # Square
    for m in range(3):
        for n in range(3):
            used[s[m + block_row*3][n + block_col*3]] = 1

    return used

def initial_try(s):
    """
    Given a Sudoku puzzle, try to solve the puzzle by iterating through each
    cell and determining the possible numbers in that cell. If only one possible
    number exists, fill it in and continue on until the puzzle is stuck.
    """
    stuck = False

    while not stuck:
        stuck = True
        # Iterate through the Sudoku puzzle
        for row in range(9):
            for col in range(9):
                used = test_cell(s, row, col)
                # More than one possibility
                if used.count(0) != 1:
                    continue

                for m in range(1, 10):
                    # If current cell is empty and there is only one possibility, then fill in the current cell
                    if s[row][col] == 0 and used[m] == 0:
                        s[row][col] = m
                        stuck = False
                        break

def DFS_solve(s, row, col):
    """
    Given a Sudoku puzzle, solve the puzzle by recursively performing DFS
    which tries out the possible solutions and by using backtracking.
    """
    if row == 8 and col == 8:
        used = test_cell(s, row, col)
        if 0 in used:
            s[row][col] = used.index(0)
        return True

    if col == 9:
        row = row+1
        col = 0

    if s[row][col] == 0:
        used = test_cell(s, row, col)
        for i in range(1, 10):
            if used[i] == 0:
                s[row][col] = i
                if DFS_solve(s, row, col+1):
                    return True

        # Then we tried 1-9 without success
        s[row][col] = 0
        return False

    return DFS_solve(s, row, col+1)


Input = [[4, 0, 7, 2, 2, 3, 1, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 6, 0],
         [9, 0, 6, 1, 0, 0, 0, 0, 0],
         [0, 0, 9, 0, 0, 1, 0, 4, 0],
         [0, 4, 0, 9, 0, 7, 0, 2, 0],
         [0, 1, 0, 3, 0, 0, 9, 0, 0],
         [0, 0, 0, 0, 0, 8, 2, 0, 7],
         [0, 7, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 8, 5, 0, 2, 3, 0, 0]]

print("Original:")
orig = copy.deepcopy(Input)
pprint(Input)
initial_try(Input)
for line in Input:
    if 0 in line:
        DFS_solve(Input, 0, 0)
        break


if orig == Input:
    print("No Solution exists")
else:
    pprint("Solved:")
    pprint(Input)
