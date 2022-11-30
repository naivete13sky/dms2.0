from django.shortcuts import render
from .models import EpcamModule


def show_genres(request):
    return render(request, "EpcamModule.html", {'epcam_module': EpcamModule.objects.all()})