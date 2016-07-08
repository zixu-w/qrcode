##########################################
# File:             qrcode.py
# Author:           Wang Zixu
# Co-Author:        CHEN Zhihan
# Last modified:    July 8, 2016
##########################################

from lib.qrgenerator import generate
from lib.qrscanner import scan

if __name__ == '__main__':
    import sys

    class InvalidArgs(Exception):
        """Invalid arguments passed in."""
        def __init__(self, arg):
            self.arg = arg
        def __str__(self):
            return repr(self.arg)
    
    try:
        if len(sys.argv) < 2:
            raise InvalidArgs('Invalid arguments')
        if sys.argv[1] == '-g':
            width = 210
            filename = 'qrcode.jpg'
            if sys.argv.index('-w') != -1:
                idxw = sys.argv.index('-w')
                try:
                    width = int(sys.argv[idxw+1])
                except Exception:
                    raise InvalidArgs('Invalid arguments')
                sys.argv.remove('-w')
                sys.argv.remove(str(width))
            if sys.argv.index('-f') != -1:
                idxf = sys.argv.index('-f')
                try:
                    filename = sys.argv[idxf+1]
                except Exception:
                    raise InvalidArgs('Invalid arguments')
                sys.argv.remove('-f')
                sys.argv.remove(filename)
            if len(sys.argv) == 3:
                generate(sys.argv[2], width, filename)
            else:
                raise InvalidArgs('Invalid arguments')
        elif sys.argv[1] == '-s':
            if len(sys.argv) == 3:
                print(scan(filename=sys.argv[2]))
            else:
                raise InvalidArgs('Invalid arguments')
        else:
            raise InvalidArgs('Invalid arguments')
    except InvalidArgs:
        print('Usage:\n'
            +'Generating: python qrcode.py -g data [-w width] [-f filename]\n'
            +'Scanning: python qrcode.py -s filename')
    except Exception as e:
        print(e)
