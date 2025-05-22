from django.urls import path
from .views import RandomNumber

urlpatterns = [
    path("randomnumber/", RandomNumber)
]