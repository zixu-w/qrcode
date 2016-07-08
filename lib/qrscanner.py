##########################################
# File:             qrscanner.py
# Author:           CHEN Zhihan
# Last modified:    July 8, 2016
##########################################

"""
Mainly developed from QRCode by Zixu WANG

Special thanks to Tomer Filiba, rotorgit and Stephen Larroque for their rsDecoder

Author: Zhihan CHEN<CHEN.Zhihan@outlook.com>
"""

import sys
import copy
import reedsolo
from qrgenerator import _fmtEncode, _fillByte, _encode
from PIL import Image
from util import *
from util import _dataAreaMask

class ImageError(Exception):
    def __init__(self,arg):
        self.arg=arg
    def __str__(self):
        return str(self.arg)

def _readImage(file):
    try:
        image = Image.open(file)
        return image
    except Exception as e:
        raise e

def _boolize(pixel):
    return pixel>122

def _sizeCheck(width,height):
    if not width==height:
        raise ImageError("The image must be a square")

def _pixelCheck(pixels,width,matrixWidth=21):
    pixelWidth=width//matrixWidth
    for jNormal in range(matrixWidth):
        for iNormal in range(matrixWidth):
            color=_boolize(pixels[iNormal*pixelWidth,jNormal*pixelWidth])
            for i in range(pixelWidth):
                for j  in range(pixelWidth):
                    if _boolize(pixels[iNormal*pixelWidth+i,jNormal*pixelWidth+j])!=color:
                        raise ImageError("Not a QR Code")
    return True

def _fillMaskCodeArea(matrix,maskCodeArray):
    newMatrix = copy.deepcopy(matrix)
    newMatrix = copyFrom(transpose(maskCodeArray[7:]), newMatrix, 8, 13)
    newMatrix = copyFrom(maskCodeArray[9:][::-1], newMatrix, 0, 8)
    newMatrix = copyFrom(maskCodeArray[7:9][::-1], newMatrix, 7, 8)
    newMatrix = copyFrom(maskCodeArray[:7][::-1], newMatrix, 14, 8)
    newMatrix = copyFrom(transpose(maskCodeArray[:6]), newMatrix, 8, 0)
    newMatrix = copyFrom([maskCodeArray[6]], newMatrix, 8, 7)
    return newMatrix

_maskCodeArea = _fillMaskCodeArea([[True for i in range(21)] for j in range(21)],[[False] for i in range(15)])
def _maskCodeAreaAsList():
    result = []
    for i in range(21):
        for j in range(21):
            if not _maskCodeArea[j][i]:
                result.append((j,i))
    return result

def _QRFormatCheck(version,bitMap):
    if version==1:
        fourDarks = logicAnd(logicXor(ver1Temp,bitMap), logicNot(_dataAreaMask))
        result = copy.deepcopy(bitMap)
        for i in range(len(bitMap)):
            for j in range(len(bitMap[0])):
                if not _dataAreaMask[j][i] or not _maskCodeArea[j][i]:
                    result[j][i]=True
        if not all([all(i) for i in logicXor(result,ver1Temp)]):
            raise ImageError("QRCode version 1 Format not satisfied")

def _generateBitMap(pixels,width,matrixWidth=21):
    result={}
    bitMap = [[False for x in range(21)] for y in range(21)]
    pixelWidth=width//matrixWidth
    for j in range(21):
        for i in range(21):
            bitMap[j][i]=_boolize(pixels[i*pixelWidth,j*pixelWidth])
    return bitMap

def _getMaskCode(bitMap):
    for maskCode in range(8):
        formatMaskCode = _fmtEncode(int('01'+'{:03b}'.format(maskCode), 2))
        maskCodeArray = [[not int(c)] for c in '{:015b}'.format(formatMaskCode)]
        emptyMatrix = [[True for i in range(21)] for j in range(21)]
        emptyMatrix = _fillMaskCodeArea(emptyMatrix,maskCodeArray)
        allFit = True
        for (j,i) in _maskCodeAreaAsList():
            if emptyMatrix[j][i]!=bitMap[j][i]:
                allFit=False
                break
        if allFit:
            return maskCode

def _getUnmaskedData(bitMap,maskCode):
    return logicXor(logicAnd(bitMap,_dataAreaMask),dataMasks[maskCode])

def _getByte(matrix,downwards=False):
    if downwards:
        matrix=matrix[::-1]
    byteList = [0 for i in range(8)]
    for i in range(8):
        byteList[7-i]=1-int(matrix[i//2][i%2])
    byte = sum([byteList[i]*2**(7-i) for i in range(8)])
    return byte

def _getEncodedData(bitMap):
    bytes23_25=[ _getByte(getPart(bitMap,9,4-2*i),i%2==0)for i in range(3)]
    byte22 = _getByte(getPart(bitMap,9,7))
    oracle=_fillByte(_encode("hello")[22])
    bytes19_21 = [ _getByte(getPart(bitMap,9+4*i,9),True) for i in range(3)]
    byte18_p1 = getPart(bitMap,4,9,2,2)
    byte18_p2 = getPart(bitMap,7,9,2,2)
    byte18 = _getByte(byte18_p1+byte18_p2,True)
    byte17 = _getByte(getPart(bitMap,0,9),True)
    byte16 = _getByte(getPart(bitMap,0,11))
    byte15_p1 = getPart(bitMap,4,11,2,2)
    byte15_p2 = getPart(bitMap,7,11,2,2)
    byte15 = _getByte(byte15_p1+byte15_p2)
    bytes0_14 = [ _getByte(getPart(bitMap,21-4*((i%3-1)*(-1)**((i//3)%2)+2),21-2*(i//3+1)),(i//3)%2!=0) for i in range(15)]
    return bytes0_14+[byte15]+[byte16]+[byte17]+[byte18]+bytes19_21+[byte22]+bytes23_25

def _decodeData(data):
    decoder = reedsolo.RSCodec(7)
    data=decoder.decode(data)[:19]
    heximal = ""
    for i in data:
        heximal+="{:02X}".format(i)
    heximal=heximal[3:]
    while heximal[-1:]!="0":
        heximal = heximal[:-2]
    heximal=heximal[:-1]
    bytesarr=bytearray.fromhex(heximal)
    return bytesarr

def _decodeBytes(bytes):
    return bytes.decode("iso-8859-1")

def scan(filename,matrixWidth=21):
    try:
        image = _readImage(filename)
        pixels=image.load()
        width,height=image.size
        _sizeCheck(width,height)
        _pixelCheck(pixels,width,matrixWidth)
        bitMap=_generateBitMap(pixels,width)
        _QRFormatCheck(1,bitMap)
        maskCode = _getMaskCode(bitMap)
        unmaskedData = _getUnmaskedData(bitMap,maskCode)
        encodedData = _getEncodedData(unmaskedData)
        decodedData = _decodeData(encodedData)
        original = _decodeBytes(decodedData)
        return original
    except Exception as e:
        raise e
