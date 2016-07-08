##########################################
# File:             util.py
# Author:           Wang Zixu
# Co-Author:        CHEN Zhihan
# Last modified:    July 8, 2016
##########################################

import copy
from PIL import Image, ImageDraw

# Debug echo flag.
DEBUG = False

# True represents light pixels and False represents dark pixels in PIL.
LIGHT = True
DARK = False

def genImage(bitmap, width, filename):
    '''
    Generate image corresponding to the input bitmap
    with specified width and filename.
    '''
    # New image in black-white mode initialized with white.
    img = Image.new('1', (width, width), 'white')
    drw = ImageDraw.Draw(img)
    # Normalized pixel width.
    pwidth = width // len(bitmap)
    for j in range(width):
        # Normalized j coordinate in bitmap
        normalj = j // pwidth
        for i in range(width):
            # Normalized i coordinate in bitmap
            normali = i // pwidth
            if normalj < len(bitmap) and normali < len(bitmap):
                # Draw pixel.
                drw.point((i, j), fill=bitmap[normalj][normali])
    img.save(filename)

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

def _timSeq(len, vertical=False):
    '''
    Generate a horizontal, unless specified vertical
    timing sequence with alternating dark and light
    pixels with length len.
    '''
    res = [[i % 2 for i in range(len)]]
    if vertical:
        res = transpose(res)
    return res

# Initialize pre-defined tool matrices.

# Finder pattern.
_finder = copyFrom(copyFrom([[DARK for i in range(3)] for j in range(3)],
    [[LIGHT for i in range(5)] for j in range(5)], 1, 1),
    [[DARK for i in range(7)] for j in range(7)], 1, 1)

# Alignment pattern. Not used in version 1.
_align = copyFrom(copyFrom([[DARK]],
    [[LIGHT for i in range(3)] for j in range(3)], 1, 1),
    [[DARK for i in range(5)] for j in range(5)], 1, 1)

# Version 1 QR code template with finder patterns and timing sequences.
ver1Temp = [[LIGHT for i in range(21)] for j in range(21)]
ver1Temp = copyFrom(_finder, ver1Temp, 0, 0)
ver1Temp = copyFrom(_finder, ver1Temp, 14, 0)
ver1Temp = copyFrom(_finder, ver1Temp, 0, 14)
ver1Temp = copyFrom(_timSeq(5), ver1Temp, 6, 8)
ver1Temp = copyFrom(_timSeq(5, vertical=True), ver1Temp, 8, 6)
ver1Temp = copyFrom([[DARK]], ver1Temp, 13, 8)

# Data area mask to avoid applying masks to functional area.
_dataAreaMask = [[DARK for i in range(21)] for j in range(21)]
_dataAreaMask = copyFrom([[LIGHT for i in range(9)] for j in range(9)],
    _dataAreaMask, 0, 0)
_dataAreaMask = copyFrom([[LIGHT for i in range(9)] for j in range(8)],
    _dataAreaMask, 13, 0)
_dataAreaMask = copyFrom([[LIGHT for i in range(8)] for j in range(9)],
    _dataAreaMask, 0, 13)
_dataAreaMask = copyFrom([[LIGHT for i in range(4)]], _dataAreaMask, 6, 9)
_dataAreaMask = copyFrom([[LIGHT] for i in range(4)], _dataAreaMask, 9, 6)

# Data masks defined in QR standard.

def _maskIsDark(index,i,j):
    if index==0:
        policy = (i+j)%2
    elif index == 1:
        policy = j%2
    elif index == 2:
        policy = i%3
    elif index == 3:
        policy = (i+j)%3
    elif index == 4:
        policy = (j//2 + i//3)%2
    elif index == 5:
        policy = (i*j)%2+(i*j)%3
    elif index == 6:
        policy = ((i*j)%2+(i*j)%3)%2
    elif index == 7:
        policy = ((i+j)%2+(i*j)%3)%2
    return policy == 0

_maskList = [[[DARK if _maskIsDark(c,i,j) else LIGHT for i in range(21)] for j in range(21)] for c in range(8)]
dataMasks = [logicAnd(_dataAreaMask,mask) for mask in _maskList]

# Generate images for predefined patterns for debug use.
if DEBUG:
    genImage(_finder, 70, 'finder.jpg')
    genImage(_align, 50, 'alignment.jpg')
    genImage(ver1Temp, 210, 'version1.jpg')
    genImage(_dataAreaMask, 210, 'dataAreaMask.jpg')
    for i in range(8):
        genImage(dataMasks[i], 210, 'mask'+str(i)+'.jpg')
