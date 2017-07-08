from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
# Create your models here.
# def input_image_directory_path(filename):
#     # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
#     return "Images"
#     return '{0}'.format(filename)

class PantomogramInfo(models.Model):
    image_name_text = models.CharField(max_length=200, primary_key=True)
    present_teeth_text = models.CharField(max_length=32)
    input_image = models.ImageField(upload_to='Images')
    output_image = models.ImageField(upload_to='OutputImages')
    thresh_image = models.ImageField(upload_to='ThreshImages')
    pub_date = models.DateTimeField('date published')

def validate_tooth_name(value):
    prefix = ['UL', 'UR', 'DL', 'DR']
    if not ( len(value) == 3 and value[2] in '12345678' and value[0:2] in prefix ):
        raise ValidationError(
            _('%(value)s is not correct'),
            params={'value': value},
        )

class ToothInfo(models.Model):
    start_x1 = models.IntegerField()
    start_y1 = models.IntegerField()
    start_x2 = models.IntegerField()
    start_y2 = models.IntegerField()
    is_present = models.BooleanField()
    teeth_image = models.ImageField(upload_to='TeethImages')
    teeth_id = models.CharField(max_length=3, validators=[validate_tooth_name])
    pantomogram = models.ForeignKey(PantomogramInfo, on_delete=models.CASCADE)
