import discord
from discord.ext import commands
import asyncio 
import datetime
#All of the functions are defined outside of the Cog class, so they can be used by the coroutines inside the class

#Ensures list actually represents a Matrix (every row must have the same number of entries)
def isMatrix(matrix):
    cols = len(matrix[0])
    for i in range(len(matrix)):
        if len(matrix[i]) != cols:
            return False
    return True

#Ensures a matrix is square
def isSquareMatrix(matrix):
    if not isMatrix(matrix):
        return False
    else:
        if (len(matrix) == len(matrix[0])):
            return True
    return False

#Ensures dimensions of matrices are equal
def equalDimensions(matrix1, matrix2): 
    if not (isMatrix(matrix1) and isMatrix(matrix2)):
        return False
    else: 
        if (len(matrix1) != len(matrix2)) or (len(matrix1[0]) != len(matrix2[0])):
            return False
    return True

#Ensures matrix1 can be multiplied by matrix2
def canMultiply(matrix1, matrix2):
    if not (isMatrix(matrix1) and isMatrix(matrix2)):
        return False
    else:
        cols1 = len(matrix1[0])
        rows2 = len(matrix2)
        if (cols1 != rows2):
            return False
    return True

#Produces a easy-to-read string representation 
def matrixToString(matrix): 
    output = "```"
    for i in range(len(matrix)):
        output += "["
        for j in range(len(matrix[i])):
            output += str("{0:.2f}".format(round(matrix[i][j], 2)))
            if j != len(matrix[i]) - 1:
                output += " "
        output += "]\n"
    output += "```"
    return output 

#Converts argument to a 2d list representing a matrix 
def stringToMatrix(text):
    result = []
    temp = text.split("|")
    i = 0
    for x in temp: 
        result.append([])
        result[i] = [float(num) for num in x.split(",")]
        i += 1
    return result

#Returns the matrix with the specified row and column omitted. Used for determinant calculations
def excludeRowColMatrix(matrix, excludeRow, excludeCol):
    numOfRows = len(matrix)
    #slices and rejoins the 2d list 
    result = [matrix[x][:excludeCol] + matrix[x][excludeCol + 1:] for x in range(numOfRows) if x != excludeRow]
    return result 

#Returns the determinant of a matrix
def determinant(matrix):
    numOfRows = len(matrix)
    numOfCols = len(matrix[0])
    result = 0.0 
    if numOfCols == 1:
        return matrix[0][0]
    elif numOfCols == 2: 
        return (matrix[0][0] * matrix[1][1]) - (matrix[0][1] * matrix[1][0])
    else:
        for i in range(numOfCols):
            cofactor = excludeRowColMatrix(matrix, 0, i)
            result += (pow(-1, i + 2) * matrix[0][i] * determinant(cofactor))
    return result 

#Returns transposed matrix
def transpose(matrix):
    numOfRows = len(matrix)
    numOfCols = len(matrix[0])
    result = [[0 for x in range(numOfRows)] for y in range(numOfCols)]
    for i in range(numOfRows):
        for j in range(numOfCols):
            result[j][i] = matrix[i][j]
    return result 

#Ensures matrix is invertible
def isInvertible(matrix):
    return (determinant(matrix) != 0)

#External function to calculate scalar multiplication
def scalarmultiply(matrix, scalar):
    numOfRows = len(matrix)
    numOfCols = len(matrix[0])
    result = [[0 for x in range(numOfCols)] for y in range(numOfRows)]
    for i in range(numOfRows):
        for j in range(numOfCols):
            result[i][j] = matrix[i][j] * scalar
    return result 

#Returns sum of two matrices
def add(matrix1, matrix2):
    numOfRows = len(matrix1)
    numOfCols = len(matrix1[0])
    result = [[0 for x in range(numOfCols)] for y in range(numOfRows)] 
    for i in range (numOfRows):
        for j in range (numOfCols): 
            result[i][j] = matrix1[i][j] + matrix2[i][j]        
    return result

#Returns difference of two matrices
def subtract(matrix1, matrix2):
    numOfRows = len(matrix1)
    numOfCols = len(matrix1[0])
    result = [[0 for x in range(numOfCols)] for y in range(numOfRows)] 
    for i in range (numOfRows):
        for j in range (numOfCols): 
            result[i][j] = matrix1[i][j] - matrix2[i][j]        
    return result

#Returns product of two matrices
def multiply(matrix1, matrix2):
    numOfRows1 = len(matrix1)
    numOfCols1 = len(matrix1[0])
    numOfRows2 = len(matrix2)
    numOfCols2 = len(matrix2[0])
    result = [[0 for x in range(numOfCols2)] for y in range(numOfRows1)]
    for i in range(numOfRows1):
        for j in range(numOfCols2):
            for k in range(numOfCols1):
                result[i][j] += matrix1[i][k] * matrix2[k][j]
    return result

#Returns the inverse of a matrix 
def inverse(matrix):
    numOfRows = len(matrix)
    numOfCols = len(matrix[0])
    cofactorMatrix = [[0 for x in range(numOfCols)] for y in range(numOfRows)]
    for i in range(numOfRows):
        for j in range(numOfCols):
            cofactorMatrix[i][j] = determinant(excludeRowColMatrix(matrix, i, j))
            cofactorMatrix[i][j] *= pow(-1, i + j + 2)
    result = scalarmultiply(transpose(cofactorMatrix), 1.0 / determinant(matrix))
    return result

class MatrixCog(commands.Cog, name = "Matrix"):

    def __init__(self, bot):
        self.bot = bot 

    @commands.group(invoke_without_command=True) #this makes it so when you call a sub command, this is not run
    async def matrix(self, ctx):
        commands = """Avaliable Commands:\nadd <matrix1> <matrix2>\nsubtract <matrix1> <matrix2>\nscalarmultiply <matrix1> <scalar>\nmultiply <matrix1> <matrix2>\ntranspose <matrix>\ndeterminant <matrix>\ninverse <matrix>\nAll matrices should be entered in the form a,b,c|d,e,f|g,h,i with commas separating elements and | separating rows with the first list of numbers as the first row of the matrix, and so on.\nEvery row in a matrix must have the same number of entries. 
                    """
        await ctx.send(commands)
    
    @matrix.command()
    async def add(self, ctx, input1=None, input2=None):
        #Verifies that the list initialized only contains numbers
        try:
            #verifies that user entered an input
            if (input1 is None or input2 is None):
                await ctx.send("Your input must match the format above")
            else:
                matrix1 = stringToMatrix(input1)
                matrix2 = stringToMatrix(input2)
                #verifies that the lists actually represent matrices 
                if (not (isMatrix(matrix1) and isMatrix(matrix2))):
                    await ctx.send("The lists entered do not represent matrices")
                #verifies that the two matrices are of equal dimensions
                elif(not equalDimensions(matrix1, matrix2)):
                    await ctx.send("Addition is only supported for matrices of equal dimensions")
                else: 
                    await ctx.send(matrixToString(add(matrix1, matrix2)))
        except:
            await ctx.send("Matrices can only contain numbers")
        
    @matrix.command()
    async def subtract(self, ctx, input1=None, input2=None):
        try:
            if (input1 is None or input2 is None):
                await ctx.send("Your input must match the format above")
            else:
                matrix1 = stringToMatrix(input1)
                matrix2 = stringToMatrix(input2)
                if (not (isMatrix(matrix1) and isMatrix(matrix2))):
                    await ctx.send("The lists entered do not represent matrices")
                elif(not equalDimensions(matrix1, matrix2)):
                    await ctx.send("Subtraction is only supported for matrices of equal dimensions")
                else: 
                    await ctx.send(matrixToString(subtract(matrix1, matrix2)))
        except:
            await ctx.send("Matrices can only contain numbers")
    
    #fix this 
    @matrix.command()
    async def scalarmultiply(self, ctx, input1=None, input2=None):
        #Ensures that list only contains numbers
        try:
            if (input1 is None or input2 is None):
                await ctx.send("The first argument must match the format above. The second argument must be a number")
            else:
                matrix = stringToMatrix(input1)
                #Ensures that the second parameter is actually a number 
                try:    
                    scalar = float(input2)
                    #Ensures that input actually represents a matrix 
                    if (not isMatrix(matrix)):
                        await ctx.send("The lists entered do not represent matrices")
                    else: 
                        await ctx.send(matrixToString(scalarmultiply(matrix, scalar)))
                except:
                    await ctx.send("The second input must be a number")
        except:
            await ctx.send("Matrices can only contain numbers")        

    @matrix.command()
    async def multiply(self, ctx, input1=None, input2=None):
        #Ensures that matrix only contains numbers
        try:
            if (input1 is None or input2 is None):
                await ctx.send("Your input must match the format above")
            else:
                matrix1 = stringToMatrix(input1)
                matrix2 = stringToMatrix(input2)
                #Ensures that both lists actually represent matrices
                if (not (isMatrix(matrix1) and isMatrix(matrix2))):
                    await ctx.send("The lists entered do not represent matrices")
                #Ensures that the two matrices are multipliable 
                elif (not canMultiply(matrix1, matrix2)):
                    await ctx.send("Matrix multiplication is only defined when the number of columns of the first matrix equals the number of rows of the second")
                else:
                    await ctx.send(matrixToString(multiply(matrix1, matrix2)))
        except:
            await ctx.send("Matrices can only contain numbers")

    @matrix.command()
    async def transpose(self, ctx, input1=None):
        #Ensures that matrix only contains numbers
        try:
            if (input1 is None):
                await ctx.send("Your input must match the format above")
            else:
                matrix = stringToMatrix(input1)
                #Ensures that the list entered actually represents a matrix
                if (not isMatrix(matrix)):
                    await ctx.send("The list entered does not represent a matrix")
                else:
                    await ctx.send(matrixToString(transpose(matrix)))
        except:
            await ctx.send("Matrices can only contain numbers")
    
    @matrix.command()
    async def determinant(self, ctx, input1=None):
        try:
            if (input1 is None):
                await ctx.send("Your input must match the format above")
            else:
                matrix = stringToMatrix(input1)
                if (not (isMatrix(matrix))):
                    await ctx.send("The list entered does not represent a matrix")
                elif (not (isSquareMatrix(matrix))):
                    await ctx.send("Determinant is only defined for square matrices.")
                else:
                    await ctx.send(determinant(matrix))
        except:
            await ctx.send("Matrices can only contain numbers")
    
    @matrix.command()
    async def inverse(self, ctx, input1=None):
        try:
            if (input1 is None):
                await ctx.send("Your input must match the format above")
            else:
                matrix = stringToMatrix(input1)
                if (not (isMatrix(matrix))):
                    await ctx.send("The list entered does not represent a matrix")
                elif(not (isSquareMatrix(matrix))):
                    await ctx.send("The matrix is not square")
                elif (not (isInvertible(matrix))):
                    await ctx.send("The matrix is not invertible")
                else:
                    await ctx.send(matrixToString(inverse(matrix)))
        except:
            await ctx.send("Matrices can only contain numbers")
                    
def setup(bot):
    bot.add_cog(MatrixCog(bot))
    print("MatrixCalculations is loaded")