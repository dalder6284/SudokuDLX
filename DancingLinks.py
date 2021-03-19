from time import perf_counter

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

class LinkedList:

    def __init__(self):
        self.header = ColumnNode('Header')

    def makeDLX(self, constraints, rows):
        # For each constraint, make a column.
        tic = perf_counter()
        temp_column = self.header
        for column in constraints:
            temp_column.right = ColumnNode(column)
            temp_column.right.left = temp_column
            temp_column = temp_column.right
        temp_column.right = self.header
        self.header.left = temp_column

        # For each row, go across and add one node down.
        for row in rows:
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
        print(f"Linked list made in {toc - tic:0.4f} seconds.")


def CoverColumn(c):
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


def UncoverColumn(c):
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

def AlgorithmX(matrix, k=0, solution={}):

    if matrix.header == matrix.header.right:
        for o in solution.values():
            print(o.column.name, end='/')
            n = o.right
            while(n != o):
                print(n.column.name, end='/')
                n = n.right
            print('')
        print('')
        return
    else:
        # Choose column c (smallest size to minimize branching)... 
        #s = float('inf')
        #j = matrix.header.right
        #while j != matrix.header:
        #    if j.size < s:
        #        c = j
        #        s = j.size
        #    j = j.right

        c = matrix.header.right
        # ...and cover it.
        CoverColumn(c)
        # For each r below c, make r the k-th part of the solution.
        r = c.down
        while r != c:
            solution[k] = r

            j = r.right
            while j != r:
                CoverColumn(j.column)
                j = j.right

            AlgorithmX(matrix, k=k+1, solution=solution)

            r = solution[k]
            c = r.column

            j = r.left
            while j != r:
                UncoverColumn(j.column)
                j = j.left

            r = r.down
        
        UncoverColumn(c)
        return