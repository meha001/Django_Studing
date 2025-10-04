from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("Страница Women")

def categories(request):
    return HttpResponse("<h1>Стфтя по катигория </h1>")