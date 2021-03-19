from time import perf_counter
from copy import copy

# SUDOKU GRID
sudoku = [[0, 7, 0, 9, 4, 2, 0, 1, 0],
          [0, 0, 8, 5, 0, 1, 0, 0, 0],
          [0, 9, 0, 0, 0, 0, 0, 0, 0],
          [8, 3, 0, 0, 0, 0, 0, 0, 0],
          [6, 5, 7, 2, 0, 0, 0, 8, 0],
          [0, 2, 9, 0, 0, 0, 0, 7, 0],
          [0, 8, 0, 1, 9, 0, 0, 0, 0],
          [9, 0, 0, 0, 0, 7, 1, 2, 5],
          [5, 0, 0, 6, 2, 3, 8, 0, 7]]

# HEADER GENERATION

def generateColumns(size):
    size += 1
    row_column = []
    for i in range(1, size):
        for j in range(1, size):
            row_column.append('R'+str(i)+'C'+str(j))
    row_number = []
    for i in range(1,size):
        for j in range(1, size):
            row_number.append('R'+str(i)+'#'+str(j))
    column_number = []
    for i in range(1, size):
        for j in range(1, size):
            column_number.append('C'+str(i)+'#'+str(j))
    box_number = []
    for i in range(1, size):
        for j in range(1, size):
            box_number.append('B'+str(i)+'#'+str(j))

    return row_column + row_number + column_number + box_number

# ROW GENERATION
# DOES NOT CURRENTLY WORK FOR NUMBERS OTHER THAN 9
def generateRows(size, X):
    final = []
    for row in range(size):
        for column in range(size):
            for cell in range(size):
                temp = []
                # Add Row-Column
                temp.append(X[row*size + column])
                # Add Row-Number
                temp.append(X[size**2 + row*size + cell])
                # Add Column-Number
                temp.append(X[((size**2)*2) + column*size + cell])
                # Add Box-Number
                box = 0
                if row > 2:
                    box += 3
                if row > 5:
                    box += 3
                if column > 2:
                    box += 1
                if column > 5:
                    box += 1
                temp.append(X[((size**2)*3) + box*size + cell])
                final.append(temp)
    return final

class Node:

    def __init__(self):
        self.right = None
        self.left = None
        self.up = None
        self.down = None
        self.column = None

class ColumnNode:

    def __init__(self, name):
            self.name = name
            self.right = None
            self.left = None
            self.up = None
            self.down = None
            self.size = None

class SudokuSolver:

    def __init__(self, sudoku):
        self.header = ColumnNode('Header')
        self.sudoku = sudoku
        self.constraints = generateColumns(9)
        self.rows = generateRows(9, self.constraints)

        self.solution = {}
        self.solution_key = 0

        
        # For each constraint, make a column.
        tic = perf_counter()
        temp_column = self.header
        for column in self.constraints:
            temp_column.right = ColumnNode(column)
            temp_column.right.left = temp_column
            temp_column = temp_column.right
        temp_column.right = self.header
        self.header.left = temp_column

        # For each row, go across and add one node down.
        for row in self.rows:
            first_node = None
            previous_node = None
            for item in row:
                temp_column = self.header.right
                while temp_column != self.header:
                    if item == temp_column.name:
                        #print("Placing a node in Node " + temp_column.name)
                        temp = temp_column
                        while temp.down != None:
                            temp = temp.down
                        temp.down = Node()
                        if first_node == None:
                            first_node = temp.down
                        if previous_node != None:
                            temp.down.left = previous_node
                            temp.down.left.right = temp.down
                        temp.down.up = temp
                        temp.down.column = temp_column
                        previous_node = temp.down
                        break
                    temp_column = temp_column.right
            first_node.left = previous_node
            previous_node.right = first_node

            #print('\n')

        # Link up each bottom node with their header node.
        temp = self.header.right
        while temp != self.header:
            size = 0
            while temp.down != None:
                size += 1
                temp = temp.down
            temp.column.size = size
            temp.down = temp.column
            temp.down.up = temp
            temp = temp.down.right

        toc = perf_counter()
        self.SolvedLinkRemoval()
        print(f"Linked list made in {toc - tic:0.4f} seconds.")

    def SolvedLinkRemoval(self):

        self.solved_parts = []
        self.rows_to_remove = []

        for row in self.sudoku:
            for digit in row:
                if digit != 0:
                    self.solved_parts.append((self.sudoku.index(row) + 1, row.index(digit) + 1, digit))

        for row, column, digit in self.solved_parts:
            temp = self.header.right
            temp_name = 'R'+str(row)+'C'+str(column)
            while temp != self.header:
                if temp.name == temp_name:
                    for i in range(digit):
                        temp = temp.down
                    self.rows_to_remove.append(temp)
                    break
                temp = temp.right

        for node in self.rows_to_remove:
            self.CoverColumn(node.column)
            j = node.right
            while j != node:
                self.CoverColumn(j.column)
                j = j.right

    def CoverColumn(self, c):
        c.right.left = c.left
        c.left.right = c.right
        i = c.down
        while i != c:
            j = i.right
            while j != i:
                j.down.up = j.up
                j.up.down = j.down
                j.column.size = j.column.size - 1
                j = j.right
            i = i.down


    def UncoverColumn(self, c):
        i = c.up
        while i != c:
            j = i.left
            while j != i:
                j.column.size = j.column.size + 1
                j.down.up = j
                j.up.down = j
                j = j.left
            i = i.up
        c.right.left = c
        c.left.right = c

    def SudokuSolve(self, k=0, solution={}, size_heuristic=False):

        if self.header == self.header.right:
            self.solution[self.solution_key] = []
            for o in solution.values():
                self.solution[self.solution_key].append(o.column.name + o.right.column.name[-2:])
            self.solution_key += 1
            return
        else:
            # Choose column c...
            if size_heuristic: 
                s = float('inf')
                j = self.header.right
                while j != self.header:
                    if j.size < s:
                        c = j
                        s = j.size
                    j = j.right
            else:
                c = self.header.right
            # ...and cover it.
            self.CoverColumn(c)
            # For each r below c, make r the k-th part of the solution.
            r = c.down
            while r != c:
                solution[k] = r

                j = r.right
                while j != r:
                    self.CoverColumn(j.column)
                    j = j.right

                self.SudokuSolve(k=k+1, solution=solution)

                r = solution[k]
                c = r.column

                j = r.left
                while j != r:
                    self.UncoverColumn(j.column)
                    j = j.left

                r = r.down
            
            self.UncoverColumn(c)

            if k == 0:
                return (self.solution)

            return

    def FillInSudoku(self, solutions_dict):

        number = 1
        for solution in solutions_dict.values():
            for cell in solution:
                # cell is a string like 'R1C1#1'
                # cell[1] is the row + 1
                row = int(cell[1]) - 1
                # cell[3] is the column + 1
                column = int(cell[3]) - 1
                # cell[5] is the digit
                digit = int(cell[5])
                self.sudoku[row][column] = digit
            print(f'Solution #{number}')
            for i in self.sudoku:
                print(i)
            print('')
            number += 1



llist = SudokuSolver(sudoku)
llist.FillInSudoku(llist.SudokuSolve())
