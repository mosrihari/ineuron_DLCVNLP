import base64


# To decode to images
def decodeImage(imgstring):
    imgdata = base64.b64decode(imgstring)
    with open("myimage.jpeg", 'wb') as f:
        f.write(imgdata)
        f.close()