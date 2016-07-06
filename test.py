#!usr/bin/python3

import qrcode
import qrscanner







qrcode.qrcode("hello")
qrscanner.scan("qrcode.jpg")

qrcode.qrcode("hello world")
qrscanner.scan("qrcode.jpg")