from django.shortcuts import render
from django.http import HttpResponse

from django.template import loader
from django.shortcuts import get_object_or_404, render
from .models import PantomogramInfo

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def gallery(request):
    
    pantomograms_list = PantomogramInfo.objects.all()
    template = loader.get_template('imageDisp/gallery.html')
    context = {
        'pantomograms_list': pantomograms_list,
    }
    return HttpResponse(template.render(context, request))

def details(request, imageName, **kwargs):
    tab = kwargs.get('tab','1')

    pantomogram_info = get_object_or_404(PantomogramInfo, pk=imageName)
    return render(request, 'imageDisp/details.html', {'pantomogram_info': pantomogram_info, "tab": tab})