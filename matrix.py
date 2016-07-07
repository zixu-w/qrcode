#!usr/bin/python3

import copy


def transpose(mat):
    '''Transpose a matrix'''
    res = [[mat[j][i] for j in range(len(mat))] for i in range(len(mat[0]))]
    return res

def copyFrom(src, dst, top, left):
    '''
    Copy the content of matrix src into matrix dst.
    The top-left corner of src is positioned at (left, top)
    in dst.
    '''
    res = copy.deepcopy(dst)
    for j in range(len(src)):
        for i in range(len(src[0])):
            res[top+j][left+i] = src[j][i]
    return res

def getPart(matrix,top,left,width=2,height=4):
    result = [[False for i in range(width)] for j in range(height)]
    for j in range(height):
        for i in range(width):
            result[j][i]=matrix[top+j][left+i]
    return result

def logicAnd(mat1, mat2):
    '''
    Matrix-wise and.
    Dark and dark -> dark
    Light and light -> light
    Dark and light -> light
    Light and dark -> light
    '''
    res = [[True for i in range(len(mat1[0]))] for j in range(len(mat1))]
    for j in range(len(mat1)):
        for i in range(len(mat1[0])):
            res[j][i] = mat1[j][i] or mat2[j][i] 
    return res



def logicOr(mat1,mat2):
    """
    B + B -> B
    B + W -> B
    W + W -> W
    """
    res = [[False for i in range(len(mat1[0]))] for j in range(len(mat1))]
    for j in range(len(mat1)):
        for i in range(len(mat1[0])):
            res[j][i] = mat1[j][i] and mat2[j][i]
    return res

def logicNot(mat1):
    res = [[False for i in range(len(mat1[0]))] for j in range(len(mat1))]
    for j in range(len(mat1)):
        for i in range(len(mat1[0])):
            res[j][i] = not mat1[j][i]
    return res
def logicXor(mat1, mat2):
    '''
    Matrix-wise xor.
    Dark xor dark -> light
    Light xor light -> light
    Dark xor light -> dark
    Light xor dark -> dark
    '''
    res = [[True for i in range(len(mat1[0]))] for j in range(len(mat1))]
    for j in range(len(mat1)):
        for i in range(len(mat1[0])):
            res[j][i] = mat1[j][i] == mat2[j][i]
    return res

