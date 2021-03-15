from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


def login_test(request):
    return render(request, 'login_page/index.html')
