from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
import django.core.files.uploadedfile
import io
import sys
import numpy as np
from Segmentation import ImageProcessing as ip


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
    process_image_starting_points = models.ImageField(upload_to='ProcessImages', null=True)
    process_image_laplace = models.ImageField(upload_to='ProcessImages', null=True)
    process_image_gap = models.ImageField(upload_to='ProcessImages', null=True)
    b_edit = models.BooleanField(default=False)
    pub_date = models.DateTimeField(null=True)


def validate_tooth_name(value):
    # TODO TO JEST MEGA SPIERDOLONE:
    prefix = ['UL', 'UR', 'DL', 'DR']
    if not (len(value) == 3 and value[2] in '12345678' and value[0:2] in prefix):
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
    teeth_image = models.ImageField(upload_to='TeethImages', null=True)
    teeth_id = models.CharField(max_length=3, validators=[validate_tooth_name])
    pantomogram = models.ForeignKey(PantomogramInfo, on_delete=models.CASCADE)


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
def add_tooth_infos(image_name, thisToothPossition, bTeeth, teethImages, panto):
    present_teeth_text_array = np.empty(32, dtype='str')
    present_teeth_text_array.fill("3")
    for i in range(0, len(bTeeth)):
        index = 31
        if i < 8:
            # upper left:
            index = i
        elif i < 16:
            # down left revers, don't shorten so it's readable :
            index = 31 - i
        elif i < 24:
            # upper right revers:
            index = 31 - i
        elif i < 32:
            # down right:
            index = i

        present_teeth_text_array[index] = bTeeth[i]

    present_teeth_text = ""
    for c in present_teeth_text_array:
        present_teeth_text += str(c)

    for i in range(0, thisToothPossition.shape[1]):
        y1 = thisToothPossition[1][i]
        x1 = thisToothPossition[0][i]
        y2 = thisToothPossition[3][i]
        x2 = thisToothPossition[2][i]
        is_present = bTeeth[i]

        teeth_id = ""
        if i < 8:
            # upper left:
            teeth_id = 'UL{}'.format(8 - i)
        elif i < 16:
            # down left revers, don't shorten so it's readable :
            teeth_id = 'DL{}'.format(i - 8 + 1)
        elif i < 24:
            # upper right revers:
            teeth_id = 'UR{}'.format(24 - i)
        elif i < 32:
            # down right:
            teeth_id = 'DR{}'.format(i - 24 + 1)
        if is_present == True:
            t_image = ip.mat2base64(teethImages[i])
            teeth_file = prep_image_file(t_image, teeth_id + "_" + image_name)

            ToothInfo.objects.create(start_x1=x1, start_y1=y1, start_x2=x2, start_y2=y2, is_present=is_present,
                                     teeth_image=teeth_file, teeth_id=teeth_id, pantomogram=panto)
        else:
            ToothInfo.objects.create(start_x1=x1, start_y1=y1, start_x2=x2, start_y2=y2, is_present=is_present,
                                     teeth_id=teeth_id, pantomogram=panto)

    return present_teeth_text
def full_add(image_file, cut_image, output_image, thresh_image, thisToothPossition, bTeeth, teethImages,
             process_images):
    image_name = image_file.name

    output_file = prep_image_file(output_image, image_name)
    thresh_file = prep_image_file(thresh_image, image_name)
    cut_file = prep_image_file(cut_image, image_name)

    process_image_starting_points_file = prep_image_file(process_images[0], "starting_points_" + image_name)
    process_image_laplace_file = prep_image_file(process_images[1], "laplace_" + image_name)
    process_image_gap_file = prep_image_file(process_images[2], "gap_s" + image_name)


    present_teeth_text = ""


    new_panto = PantomogramInfo.objects.create(image_name_text=image_name, present_teeth_text=present_teeth_text,
                                               input_image=cut_file,
                                               output_image=output_file, thresh_image=thresh_file,
                                               process_image_starting_points=process_image_starting_points_file,
                                               process_image_laplace=process_image_laplace_file,
                                               process_image_gap=process_image_gap_file,
                                               pub_date=timezone.now())

    new_panto.present_teeth_text = add_tooth_infos(image_name, thisToothPossition, bTeeth, teethImages, new_panto)
    new_panto.save()


    return new_panto

    # def redo_change(panto, output_image, bTeeth, teethImages):
    #
    #     byteImgIO = io.BytesIO()
    #     output_image.save(byteImgIO, "JPEG")
    #     byteImgIO.seek(0)
    #     byteImg = byteImgIO.read()
    #     output_file = django.core.files.uploadedfile.InMemoryUploadedFile(io.BytesIO(byteImg),
    #                                                                       "input_image", panto.image_name_text,
    #                                                                       panto.input_image.content_type,
    #                                                                       panto.input_image.size,
    #                                                                       None, )
    #     panto.output_image = output_file
    #     panto.present_teeth_text = bTeeth
    #
    #     return
