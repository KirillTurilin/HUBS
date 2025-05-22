from django.shortcuts import render, HttpResponse
from django.views import View
from random import randint
# Create your views here.

class RandomNumber(View):
    def get(self, request):
        answer = request.GET.get("howbig")
        return HttpResponse(randint(0, int(answer)))