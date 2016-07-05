######################################
# File:             qrcode.py
# Author:           Wang Zixu
# Co-Author:        Chen Zhihan
# Last modified:    July 5, 2016
######################################

from PIL import Image, ImageDraw
import copy

'''''''''''''''''''''''''''''''''''''''''''''''''''
    Python version 1-L QR code generator.
    Other versions to be implemented.

    Usage:
        import qrcode
        qrcode.qrcode(data string [, width] [, filename])

    Or see qrcode_example.py

    Coordinate system used:
            i
        o-------->
        |
      j |   .--> (i, j) for mat[j][i]
        |
        v

'''''''''''''''''''''''''''''''''''''''''''''''''''

# Debug echo flag.
__DEBUG = False

# 1 represents light pixels and 0 represents dark pixels in PIL.
_LIGHT = 1
_DARK = 0

class CapacityOverflowException(Exception):
    '''Exception for data larger than 17 characters in V1-L byte mode.'''
    def __init__(self, arg):
        self.arg = arg

    def __str__(self):
        return repr(self.arg)

def _matCp(src, dst, top, left):
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

def _transpose(mat):
    '''Transpose a matrix'''
    res = [[mat[j][i] for j in range(len(mat))] for i in range(len(mat[0]))]
    return res

def _timSeq(len, vertical=False):
    '''
    Generate a horizontal, unless specified vertical
    timing sequence with alternating dark and light
    pixels with length len.
    '''
    res = [[i % 2 for i in range(len)]]
    if vertical:
        res = _transpose(res)
    return res

def _matAnd(mat1, mat2):
    '''
    Matrix-wise and.
    Dark and dark -> dark
    Light and light -> light
    Dark and light -> light
    Light and dark -> light
    '''
    res = [[_LIGHT for i in range(len(mat1[0]))] for j in range(len(mat1))]
    for j in range(len(mat1)):
        for i in range(len(mat1[0])):
            res[j][i] = int(mat1[j][i] == _LIGHT or mat2[j][i] == _LIGHT)
    return res

def _matXor(mat1, mat2):
    '''
    Matrix-wise xor.
    Dark xor dark -> light
    Light xor light -> light
    Dark xor light -> dark
    Light xor dark -> dark
    '''
    res = [[_LIGHT for i in range(len(mat1[0]))] for j in range(len(mat1))]
    for j in range(len(mat1)):
        for i in range(len(mat1[0])):
            res[j][i] = int(mat1[j][i] == mat2[j][i])
    return res


# Initialize pre-defined tool matrices.

# Finder pattern.
_finder = _matCp(_matCp([[_DARK for i in range(3)] for j in range(3)],
    [[_LIGHT for i in range(5)] for j in range(5)], 1, 1),
    [[_DARK for i in range(7)] for j in range(7)], 1, 1)

# Alignment pattern. Not used in version 1.
_align = _matCp(_matCp([[_DARK]],
    [[_LIGHT for i in range(3)] for j in range(3)], 1, 1),
    [[_DARK for i in range(5)] for j in range(5)], 1, 1)

# Version 1 QR code template with finder patterns and timing sequences.
_ver1 = [[_LIGHT for i in range(21)] for j in range(21)]
_ver1 = _matCp(_finder, _ver1, 0, 0)
_ver1 = _matCp(_finder, _ver1, 14, 0)
_ver1 = _matCp(_finder, _ver1, 0, 14)
_ver1 = _matCp(_timSeq(5), _ver1, 6, 8)
_ver1 = _matCp(_timSeq(5, vertical=True), _ver1, 8, 6)
_ver1 = _matCp([[_DARK]], _ver1, 13, 8)

# Data area mask to avoid applying masks to functional area.
_dataAreaMask = [[_DARK for i in range(21)] for j in range(21)]
_dataAreaMask = _matCp([[_LIGHT for i in range(9)] for j in range(9)],
    _dataAreaMask, 0, 0)
_dataAreaMask = _matCp([[_LIGHT for i in range(9)] for j in range(8)],
    _dataAreaMask, 13, 0)
_dataAreaMask = _matCp([[_LIGHT for i in range(8)] for j in range(9)],
    _dataAreaMask, 0, 13)
_dataAreaMask = _matCp([[_LIGHT for i in range(4)]], _dataAreaMask, 6, 9)
_dataAreaMask = _matCp([[_LIGHT] for i in range(4)], _dataAreaMask, 9, 6)

# Data masks defined in QR standard.

def darkPolicy(index):
    def choose(index,i,j):
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
    return lambda i,j:choose(index,i,j)

maskList = [[[_DARK if darkPolicy(c)(i,j) else _LIGHT for i in range(21)] for j in range(21)] for c in range(8)]
_dataMasks = [_matAnd(_dataAreaMask,mask) for mask in maskList]

def _genImage(bitmap, width, filename):
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

# Generate images for predefined patterns for debug use.
if __DEBUG:
    _genImage(_finder, 70, 'finder.jpg')
    _genImage(_align, 50, 'alignment.jpg')
    _genImage(_ver1, 210, 'version1.jpg')
    _genImage(_dataAreaMask, 210, 'dataAreaMask.jpg')
    for i in range(8):
        _genImage(_dataMasks[i], 210, 'mask'+str(i)+'.jpg')

def _gfpMul(x, y, prim=0x11d, field_charac_full=256, carryless=True):
    '''Galois field GF(2^8) multiplication.'''
    r = 0
    while y:
        if y & 1:
            r = r ^ x if carryless else r + x
        y = y >> 1
        x = x << 1
        if prim > 0 and x & field_charac_full:
            x = x ^ prim
    return r

# Calculate alphas to simplify GF calculations.

_gfExp = [0] * 512
_gfLog = [0] * 256
_gfPrim = 0x11d

_x = 1

for i in range(255):
    _gfExp[i] = _x
    _gfLog[_x] = i
    _x = _gfpMul(_x, 2)

for i in range(255, 512):
    _gfExp[i] = _gfExp[i-255]

def _gfPow(x, pow):
    '''GF power.'''
    return _gfExp[(_gfLog[x] * pow) % 255]

def _gfMul(x, y):
    '''Simplified GF multiplication.'''
    if x == 0 or y == 0:
        return 0
    return _gfExp[_gfLog[x] + _gfLog[y]]

def _gfPolyMul(p, q):
    '''GF polynomial multiplication.'''
    r = [0] * (len(p) + len(q) - 1)
    for j in range(len(q)):
        for i in range(len(p)):
            r[i+j] ^= _gfMul(p[i], q[j])
    return r

def _gfPolyDiv(dividend, divisor):
    '''GF polynomial division.'''
    res = list(dividend)
    for i in range(len(dividend) - len(divisor) + 1):
        coef = res[i]
        if coef != 0:
            for j in range(1, len(divisor)):
                if divisor[j] != 0:
                    res[i+j] ^= _gfMul(divisor[j], coef)
    sep = -(len(divisor) - 1)
    return res[:sep], res[sep:]

def _rsGenPoly(nsym):
    '''Generate generator polynomial for RS algorithm.'''
    g = [1]
    for i in range(nsym):
        g = _gfPolyMul(g, [1, _gfPow(2, i)])
    return g

def _rsEncode(bitstring, nsym):
    '''Encode bitstring with nsym EC bits using RS algorithm.'''
    gen = _rsGenPoly(nsym)
    res = [0] * (len(bitstring) + len(gen) - 1)
    res[:len(bitstring)] = bitstring
    for i in range(len(bitstring)):
        coef = res[i]
        if coef != 0:
            for j in range(1, len(gen)):
                res[i+j] ^= _gfMul(gen[j], coef)
    res[:len(bitstring)] = bitstring
    return res

def _fmtEncode(fmt):
    '''Encode the 15-bit format code using BCH code.'''
    g = 0x537
    code = fmt << 10
    for i in range(4,-1,-1):
        if code & (1 << (i+10)):
            code ^= g << i
    return ((fmt << 10) ^ code) ^ 0b101010000010010

def _encode(data):
    '''
    Encode the input data stream.
    Add mode prefix, encode data using ISO-8859-1,
    group data, add padding suffix, and call RS encoding method.
    '''
    if len(data) > 17:
        raise CapacityOverflowException(
            'Error: Version 1 QR code encodes no more than 17 characters.')
    # Byte mode prefix 0100.
    bitstring = '0100'
    # Character count in 8 binary bits.
    bitstring += '{:08b}'.format(len(data))
    # Encode every character in ISO-8859-1 in 8 binary bits.
    for c in data:
        bitstring += '{:08b}'.format(ord(c.encode('iso-8859-1')))
    # Terminator 0000.
    bitstring += '0000'
    res = list()
    # Convert string to byte numbers.
    while bitstring:
        res.append(int(bitstring[:8], 2))
        bitstring = bitstring[8:]
    # Add padding pattern.
    while len(res) < 19:
        res.append(int('11101100', 2))
        res.append(int('00010001', 2))
    # Slice to 19 bytes for V1-L.
    res = res[:19]
    # Call _rsEncode to add 7 EC bits.
    return _rsEncode(res, 7)

def _fillByte(byte, downwards=False):
    '''
    Fill a byte into a 2 by 4 matrix upwards,
    unless specified downwards.
    Upwards:    Downwards:
        0|1         6|7
        -+-         -+-
        2|3         4|5
        -+-         -+-
        4|5         2|3
        -+-         -+-
        6|7         0|1
    '''
    bytestr = '{:08b}'.format(byte)
    res = [[0, 0] for i in range(4)]
    for i in range(8):
        res[i//2][i%2] = not int(bytestr[7-i])
    if downwards:
        res = res[::-1]
    return res

def _fillData(bitstream):
    '''Fill the encoded data into the template QR code matrix'''
    res = copy.deepcopy(_ver1)
    for i in range(15):
        res = _matCp(_fillByte(bitstream[i], (i//3)%2!=0),
            res,
            21-4*((i%3-1)*(-1)**((i//3)%2)+2),
            21-2*(i//3+1))
    tmp = _fillByte(bitstream[15])
    res = _matCp(tmp[2:], res, 7, 11)
    res = _matCp(tmp[:2], res, 4, 11)
    tmp = _fillByte(bitstream[16])
    res = _matCp(tmp, res, 0, 11)
    tmp = _fillByte(bitstream[17], True)
    res = _matCp(tmp, res, 0, 9)
    tmp = _fillByte(bitstream[18], True)
    res = _matCp(tmp[:2], res, 4, 9)
    res = _matCp(tmp[2:], res, 7, 9)
    for i in range(3):
        res = _matCp(_fillByte(bitstream[19+i], True),
            res, 9+4*i, 9)
    tmp = _fillByte(bitstream[22])
    res = _matCp(tmp, res, 9, 7)
    for i in range(3):
        res = _matCp(_fillByte(bitstream[23+i], i%2==0),
            res, 9, 4-2*i)
    # Generate image after filling data for debug use.
    if __DEBUG:
        _genImage(res, 210, 'data.jpg')
    return res

def _fillInfo(arg):
    '''
    Fill the encoded format code into the masked QR code matrix.
    arg: (masked QR code matrix, mask number).
    '''
    mat, mask = arg
    # 01 is the format code for L error control level,
    # concatenated with mask id and passed into _fmtEncode
    # to get the 15 bits format code with EC bits.
    fmt = _fmtEncode(int('01'+'{:03b}'.format(mask), 2))
    fmtarr = [[not int(c)] for c in '{:015b}'.format(fmt)]
    mat = _matCp(_transpose(fmtarr[7:]), mat, 8, 13)
    mat = _matCp(fmtarr[9:][::-1], mat, 0, 8)
    mat = _matCp(fmtarr[7:9][::-1], mat, 7, 8)
    mat = _matCp(fmtarr[:7][::-1], mat, 14, 8)
    mat = _matCp(_transpose(fmtarr[:6]), mat, 8, 0)
    mat = _matCp([fmtarr[6]], mat, 8, 7)
    return mat

def _penalty(mat):
    '''
    Calculate penalty score for a masked matrix.
    N1: penalty for more than 5 consecutive pixels in row/column,
        3 points for each occurrence of such pattern,
        and extra 1 point for each pixel exceeding 5
        consecutive pixels.
    N2: penalty for blocks of pixels larger than 2x2.
        3*(m-1)*(n-1) points for each block of mxn
        (larger than 2x2).
    N3: penalty for patterns similar to the finder pattern.
        40 points for each occurrence of 1:1:3:1:1 ratio
        (dark:light:dark:light:dark) pattern in row/column,
        preceded of followed by 4 consecutive light pixels.
    N4: penalty for unbalanced dark/light ratio.
        10*k points where k is the rating of the deviation of
        the proportion of dark pixels from 50% in steps of 5%.
    '''
    # Initialize.
    n1 = n2 = n3 = n4 = 0
    # Calculate N1.
    def getN1(mat,strategy):
        n1=0
        for j in range(len(mat)):
            count = 1
            adj = False
            for i in range(1, len(mat)):
                if strategy == "j":
                    compare = mat[j][i-1]
                elif strategy == "i":
                    i,j=j,i
                    compare = mat[j-1][i]
                if mat[j][i] == compare:
                    count += 1
                else:
                    count = 1
                    adj = False
                if count >= 5:
                    if not adj:
                        adj = True
                        n1 += 3
                    else:
                        n1 += 1
        return n1

    n1=getN1(mat,"i")+getN1(mat,"j")

    # Calculate N2.
    m = n = 1
    for j in range(1, len(mat)):
        for i in range(1, len(mat)):
            if mat[j][i] == mat[j-1][i] and mat[j][i] == mat[j][i-1] and mat[j][i] == mat[j-1][i-1]:
                if mat[j][i] == mat[j-1][i]:
                    m += 1
                if mat[j][i] == mat[j][i-1]:
                    n += 1
            else:
                n2 += 3 * (m-1) * (n-1)
                m = n = 1

    # Calculate N3.
    count = 0
    def getCount(mat):
        count=0
        for row in mat:
            rowstr = ''.join(str(e) for e in row)
            occurrences = []
            begin = 0
            while rowstr.find('0100010', begin) != -1:
                begin = rowstr.find('0100010', begin) + 7
                occurrences.append(begin)
            for begin in occurrences:
                if rowstr.count('00000100010', begin-4) != 0 or rowstr.count('01000100000', begin) != 0:
                    count += 1
        return count

    transposedMat = _transpose(mat)
    n3 += 40 * (getCount(mat)+getCount(transposedMat))

    # Calculate N4.
    dark = sum(row.count(_DARK) for row in mat)
    percent = int((float(dark) / float(len(mat)**2)) * 100)
    pre = percent - percent % 5
    nex = percent + 5 - percent % 5
    n4 = min(abs(pre-50)//5, abs(nex-50)//5) * 10

    # Return final penalty score.
    return n1 + n2 + n3 + n4

def _mask(mat):
    '''
    Mask the data QR code matrix with all 8 masks,
    call _penalty to calculate penalty scores for each
    and select the best mask.
    Return tuple(selected masked matrix, number of selected mask).
    '''
    maskeds = [_matXor(mat, dataMask) for dataMask in _dataMasks]
    penalty = [0] * 8
    for i, masked in enumerate(maskeds):
        penalty[i] = _penalty(masked)
        # Print penalty scores for debug use.
        if __DEBUG:
            print ('penalty for mask {}: {}'.format(i, penalty[i]))
    # Find the id of the best mask.
    selected = penalty.index(min(penalty))
    # Print selected mask and penalty score,
    # and generate image for masked QR code for debug use.
    if __DEBUG:
        print ('mask {} selected with penalty {}'.format(selected, penalty[selected]))
        _genImage(maskeds[selected], 210, 'selectedMasked(' + str(selected) + ').jpg')
        for i, masked in enumerate(maskeds):
            if i != selected:
                _genImage(masked, 210, 'masked(' + str(i) + ').jpg')
    return maskeds[selected], selected

def _genBitmap(bitstream):
    '''
    Take in the encoded data stream and generate the
    final QR code bitmap.
    '''
    return _fillInfo(_mask(_fillData(bitstream)))

def qrcode(data, width=210, filename='qrcode.jpg'):
    '''Module public interface'''
    try:
        _genImage(_genBitmap(_encode(data)), width, filename)
    except Exception as e:
        print (e)
        raise e
