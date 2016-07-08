import qrcode

qrcode.generate('Hello world!')

qrcode.generate('Python QR code!', width=420, filename='example.jpg')

qrcode.scan('qrcode.jpg')

qrcode.scan('example.jpg')

# Exception raised here, as version 1 QR code cannot encode 
# more than 17 characters in byte mode.
qrcode.generate('012345678901234567')
