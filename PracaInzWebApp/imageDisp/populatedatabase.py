import os
import urllib
import urllib.request

import django.core.files.uploadedfile
import io
import sys

import requests
from PIL import Image

def prep_image_file(image, image_name):
    byteImgIO = io.BytesIO()
    image.save(byteImgIO, "JPEG")
    byteImgIO.seek(0)
    byteImg = byteImgIO.read()
    return django.core.files.uploadedfile.InMemoryUploadedFile(io.BytesIO(byteImg),
                                                               "input_image", image_name,
                                                               'image/jpeg',
                                                               sys.getsizeof(byteImg),
                                                               None, )

def populate_database():
    dir_str = os.path.dirname(os.path.realpath(__file__)) + "\\testSetSuperb\\"
    directory = os.fsencode(dir_str)

    print(directory)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".jpg"):
            image = Image.open(dir_str + filename)
            imagefile = prep_image_file(image, filename)
            print(filename)
            r = requests.post('http://127.0.0.1:8000/gallery/add/', files={'input_image': imagefile})

            continue
        else:
            continue

populate_database()