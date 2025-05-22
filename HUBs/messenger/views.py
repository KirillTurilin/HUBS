from django.shortcuts import render, HttpResponse
from django.views import View
# Create your views here.
def RandomNumber(request):
    import random
    number = random.randint(0,1000)
    return HttpResponse(number)