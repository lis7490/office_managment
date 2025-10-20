from django.shortcuts import render, redirect
from django.http import HttpResponse


# Create your views here.
def response(request):
    return HttpResponse('response')

def redir(request):
    return redirect('/workplace/red/')


def red(request):
    return HttpResponse('Привет, redirect!')


def render_html(request):
    make_html = """<html>
    <head><title>Название</title>
    <body><h1>Привет HTML!</h1></body>
    </head>"""
    return HttpResponse(make_html)

def render_template(request):
    return render(request, 'main.html')