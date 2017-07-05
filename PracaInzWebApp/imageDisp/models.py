from django.db import models

# Create your models here.
# def input_image_directory_path(filename):
#     # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
#     return "Images"
#     return '{0}'.format(filename)

class PantomogramInfo(models.Model):
    image_name_text = models.CharField(max_length=200, primary_key=True)
    present_teeth_text = models.CharField(max_length=32)
    input_image = models.ImageField(upload_to='Images')
    pub_date = models.DateTimeField('date published')
