import io
import sys

import django.core.files.uploadedfile
from PIL import Image
from django.core.files import File
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django.template import loader
from django.utils import timezone
import json
import numpy as np
from Segmentation import ImageProcessing as ip
from .forms import PantomogramInfoForm
from .models import PantomogramInfo, ToothInfo, full_add


def gallery(request):
    pantomograms_list = PantomogramInfo.objects.all()
    template = loader.get_template('imageDisp/gallery.html')
    context = {
        'pantomograms_list': pantomograms_list,
    }
    return HttpResponse(template.render(context, request))


def teeth_view(request, imageName):
    pantomogram_info = get_object_or_404(PantomogramInfo, pk=imageName)
    tooth_infos_ul = ToothInfo.objects.filter(pantomogram=imageName, teeth_id__startswith='UL')
    tooth_infos_ur = ToothInfo.objects.filter(pantomogram=imageName, teeth_id__startswith='UR')
    tooth_infos_dl = ToothInfo.objects.filter(pantomogram=imageName, teeth_id__startswith='DL')
    tooth_infos_dr = ToothInfo.objects.filter(pantomogram=imageName, teeth_id__startswith='DR')
    if len(tooth_infos_ul) != 8 or len(tooth_infos_ur) != 8 or len(tooth_infos_dl) != 8 or len(tooth_infos_dr) != 8:
        raise Http404(
            "Pantomogram doesn't have 32 teeth. Details: {} {} {} {}".format(len(tooth_infos_ul), len(tooth_infos_ur),
                                                                             len(tooth_infos_dl), len(tooth_infos_dr)))
    # prefix = ['UL', 'UR', 'DL', 'DR']
    context = {
        'tooth_infos_ul': tooth_infos_ul,
        'tooth_infos_ur': tooth_infos_ur,
        'tooth_infos_dl': tooth_infos_dl,
        'tooth_infos_dr': tooth_infos_dr,
    }
    return render(request, 'imageDisp/teeth.html', context)


def details(request, imageName, **kwargs):
    tab = kwargs.get('tab', '1')
    pantomogram_info = get_object_or_404(PantomogramInfo, pk=imageName)
    return render(request, 'imageDisp/details.html', {'pantomogram_info': pantomogram_info, "tab": tab})


def addTooth_Info(panto, id, is_present, x1, y1, x2, y2, image):

    if is_present == True:
        t_image = ip.mat2base64(image)
        byteImgIO3 = io.BytesIO()
        t_image.save(byteImgIO3, "JPEG")
        byteImgIO3.seek(0)
        teeth_image = byteImgIO3.read()
        teeth_file = django.core.files.uploadedfile.InMemoryUploadedFile(io.BytesIO(teeth_image),
                                                                         "input_image", id + "_" + panto.image_name_text,
                                                                         'image/jpeg',
                                                                         sys.getsizeof(teeth_image),
                                                                         None, )
        ToothInfo.objects.create(start_x1=x1, start_y1=y1, start_x2=x2, start_y2=y2, is_present=is_present,
                                 teeth_image=teeth_file, teeth_id=id, pantomogram=panto)
    else:
        ToothInfo.objects.create(start_x1=x1, start_y1=y1, start_x2=x2, start_y2=y2, is_present=is_present,
                                 teeth_id=id, pantomogram=panto)


def edit(request, imageName):
    if request.method == "POST":
        thisToothPossition = np.empty((4, 32), dtype=int)

        try:
            for i in range(1, 9):
                thisToothPossition[0, i - 1] = int(request.POST["UL{}X1".format(i)])
                thisToothPossition[1, i - 1] = int(request.POST["UL{}Y1".format(i)])
                thisToothPossition[2, i - 1] = int(request.POST["UL{}X2".format(i)])
                thisToothPossition[3, i - 1] = int(request.POST["UL{}Y2".format(i)])

                thisToothPossition[0, i - 1 + 8] = int(request.POST["UR{}X1".format(i)])
                thisToothPossition[1, i - 1 + 8] = int(request.POST["UR{}Y1".format(i)])
                thisToothPossition[2, i - 1 + 8] = int(request.POST["UR{}X2".format(i)])
                thisToothPossition[3, i - 1 + 8] = int(request.POST["UR{}Y2".format(i)])

                thisToothPossition[0, i - 1 + 16] = int(request.POST["DR{}X1".format(i)])
                thisToothPossition[1, i - 1 + 16] = int(request.POST["DR{}Y1".format(i)])
                thisToothPossition[2, i - 1 + 16] = int(request.POST["DR{}X2".format(i)])
                thisToothPossition[3, i - 1 + 16] = int(request.POST["DR{}Y2".format(i)])

                thisToothPossition[0, i - 1 + 24] = int(request.POST["DL{}X1".format(i)])
                thisToothPossition[1, i - 1 + 24] = int(request.POST["DL{}Y1".format(i)])
                thisToothPossition[2, i - 1 + 24] = int(request.POST["DL{}X2".format(i)])
                thisToothPossition[3, i - 1 + 24] = int(request.POST["DL{}Y2".format(i)])


        except KeyError:
            raise Http404("Something went wrong.")
        # except ValueError:
        #     raise Http404("It seems like somebody is messing with our form.")


        panto = get_object_or_404(PantomogramInfo, pk=imageName)

        input_image = Image.open(panto.input_image)

        thresh_image = Image.open(panto.thresh_image)

        output_image, bTeeth, teethImages = ip.redoWatershed(input_image, thresh_image, thisToothPossition)

        byteImgIO = io.BytesIO()
        output_image.save(byteImgIO, "JPEG")
        byteImgIO.seek(0)
        byteImg = byteImgIO.read()
        output_file = django.core.files.uploadedfile.InMemoryUploadedFile(io.BytesIO(byteImg),
                                                                          "input_image", panto.image_name_text,
                                                                          'image/jpeg',
                                                                          panto.input_image.size,
                                                                          None, )
        panto.output_image = output_file
        panto.present_teeth_text = bTeeth
        panto.save()

        ToothInfo.objects.filter(pantomogram=imageName).delete()
        for i in range(0, 8):
            addTooth_Info(panto, "UL{}".format(i + 1), bTeeth[i], thisToothPossition[0, i],
                          thisToothPossition[1, i],
                          thisToothPossition[2, i], thisToothPossition[3, i], teethImages[i])
            addTooth_Info(panto, "UR{}".format(i + 1), bTeeth[i], thisToothPossition[0, i + 8],
                          thisToothPossition[1, i + 8],
                          thisToothPossition[2, i + 8], thisToothPossition[3, i + 8], teethImages[i])
            addTooth_Info(panto, "DR{}".format(i + 1), bTeeth[i], thisToothPossition[0, i + 16],
                          thisToothPossition[1, i + 16],
                          thisToothPossition[2, i + 16], thisToothPossition[3, i + 16], teethImages[i])
            addTooth_Info(panto, "DL{}".format(i + 1), bTeeth[i], thisToothPossition[0, i + 24],
                          thisToothPossition[1, i + 24],
                          thisToothPossition[2, i + 24], thisToothPossition[3, i + 24], teethImages[i])
        return redirect('edit', imageName=panto.pk)
    else:
        pantomogram_info = get_object_or_404(PantomogramInfo, pk=imageName)
        tooth_infos = ToothInfo.objects.filter(pantomogram=imageName)
        if len(tooth_infos) != 32:
            raise Http404("Incorrect number of teeth found: instead of 32, {} were found.".format(len(tooth_infos)))

        teeth_dict = {t.teeth_id: {'x1': t.start_x1, 'y1': t.start_y1, 'x2': t.start_x2, 'y2': t.start_y2} for t in
                      tooth_infos}
        js_data = json.dumps(teeth_dict)
        return render(request, 'imageDisp/edit.html', {'pantomogram_info': pantomogram_info, 'js_data': js_data})


def add(request):
    if request.method == "POST":
        form = PantomogramInfoForm(request.POST, request.FILES)

        if form.is_valid():
            image_file = request.FILES['input_image']
            input_image = Image.open(image_file)
            cut_image, output_image, thresh_image, thisToothPossition, bTeeth, teethImages = ip.processImage(
                input_image)
            new_panto = full_add(image_file, cut_image, output_image, thresh_image, thisToothPossition, bTeeth,
                                 teethImages)

            return redirect('details', imageName=new_panto.pk)

        else:
            raise Http404("Form is not valid.")
    else:

        form = PantomogramInfoForm()
    return render(request, 'imageDisp/add.html', {'form': form})

# def makeImage(path):
