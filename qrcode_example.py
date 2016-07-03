import qrcode

qrcode.qrcode('Hello world!')

qrcode.qrcode('Python QR code!', width=420, filename='example.jpg')

# Exception raised here, as version 1 QR code cannot encode 
# more than 17 characters in byte mode.
qrcode.qrcode('012345678901234567')
