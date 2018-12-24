from pprint import pprint


def find_empty_location(arr, l):
    for row in range(9):
        for col in range(9):
            if (arr[row][col] == 0):
                l[0] = row
                l[1] = col
                return True
    return False


# Returns a boolean which indicates whether any assigned entry in the specified row matches the given number.
def used_in_row(arr, row, num):
    for i in range(9):
        if (arr[row][i] == num):
            return True
    return False


# Returns a boolean which indicates whether any assigned entry in the specified column matches the given number.
def used_in_col(arr, col, num):
    for i in range(9):
        if (arr[i][col] == num):
            return True
    return False


# Returns a boolean which indicates whether any assigned entry within the specified 3x3 box matches the given number
def used_in_box(arr, row, col, num):
    for i in range(3):
        for j in range(3):
            if (arr[i + row][j + col] == num):
                return True
    return False


# Checks whether it will be legal to assign num to the given row,col
def check_location_is_safe(arr, row, col, num):
    return not used_in_row(arr, row, num) and not used_in_col(arr, col, num) and not used_in_box(arr, row - row % 3,col - col % 3, num)


# Function to solve sudoku
def solve_sudoku(arr):
    # 'l' is a list variable that keeps the record of row and col in find_empty_location Function
    l = [0, 0]

    # If there is no unassigned location, we are done
    if (not find_empty_location(arr, l)):
        return True

    # Assigning list values to row and col that we got from the above Function
    row = l[0]
    col = l[1]

    # consider digits 1 to 9
    for num in range(1, 10):
        if (check_location_is_safe(arr, row, col, num)):
            # make tentative assignment
            arr[row][col] = num

            # return, if success
            if (solve_sudoku(arr)):
                return True

            # failure, unmake & try again
            arr[row][col] = 0

    # this triggers backtracking
    return False


Input = [[0, 0, 7, 2, 2, 3, 1, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 6, 0],
         [9, 0, 6, 1, 0, 0, 0, 0, 0],
         [0, 0, 9, 0, 0, 1, 0, 4, 0],
         [0, 4, 0, 9, 0, 7, 0, 2, 0],
         [0, 1, 0, 3, 0, 0, 9, 0, 0],
         [0, 0, 0, 0, 0, 8, 2, 0, 7],
         [0, 7, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 8, 5, 0, 2, 3, 0, 0]]

print("Solving using BruteForceSearch")

pprint(Input)
if not solve_sudoku(Input):
    print "No solution exists"

print("Solution obtained is:")
pprint(Input)
