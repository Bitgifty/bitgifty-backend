from django.shortcuts import render
from django.http import HttpResponse
import os
# Create your views here.


def environ(request):
    env = os.getenv("DEBUG")
    return HttpResponse(env)
