import os
#


import django

script_path = os.path.dirname(__file__)
os.environ['DJANGO_SETTINGS_MODULE'] = 'PracaInzWebApp.PracaInzWebApp.settings'
django.setup()

from django.conf import settings
from PracaInzWebApp.imageDisp import models
import datetime

def addImageToDb(image_name_text, present_teeth_text):
    settings.configure()
    root = settings.MEDIA_ROOT
    now = datetime.datetime.now()
    input_image = "Images/{}.jpg".format(image_name_text)
    output_image = "OutputImages/{}.jpg".format(image_name_text)
    thresh_image = "ThreshImages/Images/{}.jpg".format(image_name_text)

    models.PantomogramInfo.objects.create(input_image = input_image,
                                          output_image = output_image,
                                          thresh_image = thresh_image,
                                          image_name_text = image_name_text,
                                          present_teeth_text = present_teeth_text,
                                          pub_date = now,)
    print("Test")

