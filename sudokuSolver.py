import math
import copy

class Sudoku:
    def __init__(self, board): # board is a list of lists
        self.board = board
        self.nRows = len(board)
        self.nCols = self.nRows
        self.colFlag = int(math.sqrt(self.nRows)) if math.sqrt(self.nRows).is_integer() else (int(math.sqrt(self.nRows)) + 1)
        self.rowFlag = int(self.nRows / self.colFlag)

        self.variables = [(i, j) for i in range(0, self.nRows) for j in range(0, self.nCols) if self.board[i][j] == 0]
        # variables are going to be locations of 0s. will be stored as list of tuples

        # self.tempVariables = copy.deepcopy(self.variables) # deleting the indices in self.variables will disallow us to reach the domains. So we have its deepcopy

        # self.domains = [[x for x in range(1, self.nRows+1)] for _ in range(0, len(self.variables))]
        # [1, 2, 3 ... numRows] for each variable. will be stored as list of lists
        domains = []
        for v in self.variables:
            i, j = v
            allPossibleValues = [x for x in range(1, self.nRows+1)] # allPossibleValues=[1,2,3,4,5,6,7,8,9]
            valuesInSameRow = [x for x in board[i] if x != 0] # valuesInSameRow = [] or [1,3,5]
            valuesInSameCol = [x for x in [row[j] for row in board] if x != 0] # valuesInSameColumn = [] or [1,3,5]
            x = int(i / self.rowFlag) * self.rowFlag  # row index of top left corner of the box
            y = int(j / self.colFlag) * self.colFlag  # column index of top left corner of the box
            valuesInSameBox = [(x + a, y + b) for a in range(0, self.rowFlag) for b in range(0, self.colFlag) if self.board[x + a][y + b] == 0]
            domainValues = list(set(allPossibleValues) - (set(valuesInSameRow).union(set(valuesInSameCol).union(set(valuesInSameBox)))))
            domains.append(domainValues)
        self.domains = domains


		# # Heuristic -- if a variable has shorter domain try it first.
        # self.tempIndex = [i for i in range(0, len(self.variables))]
        # self.tempDomainLength = [len(item) for item in self.domains]
        # self.tempIndex = [x for _,x in sorted(zip(self.tempDomainLength, self.tempIndex))]
        # x = []
        # y = []
        # for i in range(0, len(self.tempIndex)):
        #     index = self.tempIndex[i]
        #     item = self.domains[index]
        #     x.append(item)
        #     item = self.variables[index]
        #     y.append(item)
        # self.domains = x
        # self.variables = y

        self.tempVariables = copy.deepcopy(self.variables) # deleting the indices in self.variables will disallow us to reach the domains. So we have its deepcopy



    def printBoard(self):
        for i in range(0, self.nRows):
            line = ""
            for j in range(0, self.nCols):
                entry = self.board[i][j]
                if entry == 0:
                    line += "* "
                else:
                    line += str(entry) + " "

                if (j + 1) % self.colFlag == 0 and (j + 1) != self.nCols:
                    line += "| "

            print(line)
            if (i + 1) % self.rowFlag == 0 and (i + 1) != self.nRows:
                entry = "-" * len(line)
                print(entry)

    def isSolved(self):
        for row in self.board:
            if 0 in row:
                return False
        return True

    def selectUnassignedVariable(self):
        # This function will select a variable index based on some heuristics
        if self.variables: # if there are variables
            return self.variables[0]
        else:
            return None

    def orderDomainValues(self, variable):
        return self.domains[self.tempVariables.index(variable)]

    def isValueConsistentForVariable(self, value, variable):
        # Checking constraint satisfaction. If value satisfies the constraints for that variable
        i, j = variable
        row = self.board[i]
        column = [self.board[x][j] for x in range(0, self.nRows)]
        boxRowI = int(i / self.rowFlag) * self.rowFlag
        boxColI = int(j / self.colFlag) * self.colFlag
        subPartOfBoard = [self.board[x][y] for x in range(boxRowI, boxRowI + self.rowFlag) for y in range(boxColI, boxColI + self.colFlag)]

        if value in row:
            return False
        if value in column:
            return False
        if value in subPartOfBoard:
            return False

        return True

    def inferences(self, variable, value):
        i, j = variable
        row = self.board[i]
        column = [self.board[x][j] for x in range(0, self.nRows)]
        boxRowI = int(i / self.rowFlag) * self.rowFlag # row index of top left corner of the box
        boxColI = int(j / self.colFlag) * self.colFlag # column index of top left corner of the box
        box = [self.board[x][y] for x in range(boxRowI, boxRowI + self.rowFlag) for y in range(boxColI, boxColI + self.colFlag)]
        result = []

        if row.count(0) == 1: # if there is only 1 unassigned entry(variable) left for that row
            allPossibleValues = [x for x in range(1, self.nCols+1)]
            theInferredRowValue = list(set(allPossibleValues) - set(row))[0]
            theInferredIndex = (i, row.index(0))
            if self.isValueConsistentForVariable(theInferredRowValue, theInferredIndex):
                result.append((theInferredRowValue, theInferredIndex)) # the inferred value should be assigned to inferred index of that row
            else:
                return [] # return failure. If there is one value left for a row and it does not satisfy the constraints we should return failure.
        else:
            result.append((value, ("r", i))) # row with index i cannot have the value

        if column.count(0) == 1: # if there is only 1 unassigned entry(variable) left for that column
            allPossibleValues = [x for x in range(1, self.nRows+1)]
            theInferredColValue = list(set(allPossibleValues) - set(column))[0]
            theInferredIndex = (column.index(0), j)
            if self.isValueConsistentForVariable(theInferredColValue, theInferredIndex):
                result.append((theInferredColValue, theInferredIndex))  # the inferred value should be assigned to inferred index of that column
            else:
                return []
        else:
            result.append((value, ("c", j))) # column with index j cannot have the value

        if box.count(0) == 1: # if there is only 1 unassigned entry(variable) left for that box
            allPossibleValues = [x for x in range(1, self.nRows+1)] # or self.nCols, they are same anyway.
            theInferredBoxValue = list(set(allPossibleValues) - set(box))[0]
            inC = 0 # increment amount of column index
            inR = 0 # increment amount of row index
            for x in range(0, box.index(0)):
                inC += 1
                if inC == self.colFlag:
                    inC = 0
                    inR += 1
					
            theInferredIndex = (boxRowI + inR, boxColI + inC)
            if self.isValueConsistentForVariable(theInferredBoxValue, theInferredIndex):
                result.append((theInferredBoxValue, theInferredIndex))  # the inferred value should be assigned to inferred index of that column
            else:
                return []
        else:
            result.append((value, (boxRowI, boxColI)))

        return result

    def addInferences(self, inferences, variable, value):
        for inference in inferences:
            inferredValue = inference[0]
            inferredLocation = inference[1]
            if inferredValue != value: # then there is an inferred value for a variable(which is a location(indices) of the board)
                i, j = inferredLocation
                if self.board[i][j] == 0: # if the board is not changed yet. this could have done by another condition beforehand. For example if the variable is the only one left in the row and the box.
                    self.board[i][j] = inferredValue
                    self.variables.remove(inferredLocation)
            else: # then it means that the value should be deleted from the domains of the variables in a row,column or box.
                x, y = inferredLocation # inferred location is either ("c", 1) or ("r", 1) or (1,1)

                if x == "r": # from row y's variables' domains, we should delete value
                    variablesInThatRow = [(y, t) for t in range(0, self.nCols) if self.board[y][t] == 0]
                    for v in variablesInThatRow:
                        if value in self.domains[self.tempVariables.index(v)]: # we check if this value is in the domain, because it might be deleted by below conditions beforehand. (Note that row and column might have intersected variables with a box)
                            self.domains[self.tempVariables.index(v)].remove(value)

                elif x == "c": # from col y's variables' domains, we should delete value
                    variablesInThatCol = [(t, y) for t in range(0, self.nRows) if self.board[t][y] == 0]
                    for v in variablesInThatCol:
                        if value in self.domains[self.tempVariables.index(v)]:
                            self.domains[self.tempVariables.index(v)].remove(value)

                else: # (x,y) is the location of the left top corner of the box. from that box's variables' domains, we should delete value
                    variablesInThatBox = [(x + a, y + b) for a in range(0, self.rowFlag) for b in range(0, self.colFlag) if self.board[x + a][y + b] == 0]
                    for v in variablesInThatBox:
                        if value in self.domains[self.tempVariables.index(v)]:
                            self.domains[self.tempVariables.index(v)].remove(value)

    def removeInferences(self, inferences, variable, value):
        for inference in inferences:
            inferredValue = inference[0]
            inferredLocation = inference[1]
            if inferredValue != value: # then there is an inferred value for a variable(which is a location(indices) of the board)
                i, j = inferredLocation
                if self.board[i][j] != 0:
                    self.board[i][j] = 0
                    self.variables.append(inferredLocation)
            else: # then it means that the value should be added back to the domains of the variables in a row,column or box.
                x, y = inferredLocation # inferred location is either ("c", 1) or ("r", 1) or (1,1)

                if x == "r": # from row y's variables' domains, we should delete value
                    variablesInThatRow = [(y, t) for t in range(0, self.nCols) if self.board[y][t] == 0]
                    for v in variablesInThatRow:
                        if value not in self.domains[self.tempVariables.index(v)]: # we check if this value is in the domain, because it might be deleted by below conditions beforehand. (Note that row and column might have intersected variables with a box)
                            self.domains[self.tempVariables.index(v)].append(value)

                elif x == "c": # from col y's variables' domains, we should delete value
                    variablesInThatCol = [(t, y) for t in range(0, self.nRows) if self.board[t][y] == 0]
                    for v in variablesInThatCol:
                        if value not in self.domains[self.tempVariables.index(v)]:
                            self.domains[self.tempVariables.index(v)].append(value)

                else: # (x,y) is the location of the left top corner of the box. from that box's variables' domains, we should delete value
                    variablesInThatBox = [(x + a, y + b) for a in range(0, self.rowFlag) for b in range(0, self.colFlag) if self.board[x + a][y + b] == 0]
                    for v in variablesInThatBox:
                        if value not in self.domains[self.tempVariables.index(v)]:
                            self.domains[self.tempVariables.index(v)].append(value)

    def solveSudoku(self): # solving sudoku with recursive backtracking search
        if self.isSolved():
            return self.board

        variable = self.selectUnassignedVariable()

        # if variable is not None:
        domain = self.orderDomainValues(variable)
        for value in domain:
            if self.isValueConsistentForVariable(value, variable):
                i, j = variable

                # add the assignment
                self.board[i][j] = value # giving the value to the variable
                self.variables.remove(variable)

                inferences = self.inferences(variable, value)

                if inferences:
                    self.addInferences(inferences, variable, value)

                    result = self.solveSudoku()

                    if result != False:
                        return result

                # remove the assignment
                self.removeInferences(inferences, variable, value)
                self.board[i][j] = 0
                self.variables.append(variable)


        return False



# sudokuBoard = [
#                [1, 0, 3, 2],
#                [0, 0, 1, 4],
#                [4, 1, 2, 0],
#                [2, 3, 0, 0]
#               ]


# sudokuBoard = [[0,0,0,0,0,3],
#                [0,6,0,4,5,0],
#                [0,0,0,0,1,5],
#                [1,2,0,0,0,0],
#                [0,1,2,0,3,0],
#                [6,0,0,0,0,0]]



# sudokuBoard =   [[0, 0, 3, 6, 0, 0],
#             [0, 2, 0, 0, 0, 4],
#             [5, 0, 0, 0, 6, 0],
#             [0, 3, 0, 0, 0, 5],
#             [3, 0, 0, 0, 1, 0],
#             [0, 0, 1, 4, 0, 0]]


# --- MEDIUM BOARDS ---
# sudokuBoard =    [[0, 8, 0, 0, 3, 1, 7, 6, 0],
#             [7, 5, 2, 0, 0, 9, 3, 0, 0],
#             [0, 1, 6, 0, 2, 0, 0, 0, 0],
#             [0, 0, 0, 0, 9, 0, 0, 1, 0],
#             [0, 0, 0, 0, 1, 0, 0, 0, 6],
#             [0, 9, 1, 0, 0, 0, 0, 2, 4],
#             [8, 0, 3, 0, 6, 2, 0, 0, 0],
#             [0, 6, 0, 0, 0, 4, 0, 0, 0],
#             [0, 0, 4, 0, 0, 0, 0, 7, 3]]



# sudokuBoard =    [[8, 1, 0, 0, 3, 0, 0, 2, 7],
#             [0, 6, 2, 0, 5, 0, 0, 9, 0],
#             [0, 7, 0, 0, 0, 0, 0, 0, 0],
#             [0, 9, 0, 6, 0, 0, 1, 0, 0],
#             [1, 0, 0, 0, 2, 0, 0, 0, 4],
#             [0, 0, 8, 0, 0, 5, 0, 7, 0],
#             [0, 0, 0, 0, 0, 0, 0, 8, 0],
#             [0, 2, 0, 0, 1, 0, 7, 5, 0],
#             [3, 8, 0, 0, 7, 0, 0, 4, 2]]






# --- HARD BOARD ---
sudokuBoard = [[1, 3, 0, 6, 0, 0, 0, 0, 0],
            [0, 0, 6, 0, 0, 1, 7, 0, 0],
            [0, 0, 8, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 8, 0, 0, 0, 0],
            [6, 0, 0, 1, 0, 7, 0, 0, 3],
            [0, 0, 0, 0, 9, 0, 5, 7, 0],
            [0, 0, 9, 0, 0, 0, 8, 0, 0],
            [0, 8, 0, 0, 0, 3, 9, 4, 0],
            [0, 7, 3, 0, 0, 0, 0, 5, 6]]

# ------SOLUTION OF THE HARD PROBLEM -----#
#  ----    1 3 5 | 6 7 2 | 4 9 8    ----- #
#  ----    9 4 6 | 8 3 1 | 7 2 5    ----- #
#  ----    7 2 8 | 5 4 9 | 3 6 1    ----- #
#  ----    ----------------------   ----- #
#  ----    3 5 7 | 2 8 4 | 6 1 9    ----- #
#  ----    6 9 4 | 1 5 7 | 2 8 3    ----- #
#  ----    8 1 2 | 3 9 6 | 5 7 4    ----- #
#  ----    ----------------------   ----- #
#  ----    2 6 9 | 4 1 5 | 8 3 7    ----- #
#  ----    5 8 1 | 7 6 3 | 9 4 2    ----- #
#  ----    4 7 3 | 9 2 8 | 1 5 6    ----- #
# ----------------------------------------#








sudoku = Sudoku(sudokuBoard)
sudoku.printBoard()

print("\n\n")



import time
s = time.time()
if sudoku.solveSudoku():
    sudoku.printBoard()
print("Execution time:", time.time() - s)

