import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib import messages
from django.http import FileResponse

from .forms import CreateUserForm

# Create your views here.

# TODO view for testing that displays image from media folder
def display_images(request, image_name) :
    base_url = getattr(settings, "MEDIA_URL", None)
    base_url = '.' + base_url
    try :
        img = open(os.path.join(base_url, image_name), 'rb')
    except Exception :
        raise Http404("This image does not exist")
    return FileResponse(img)


def login_(request) :
    if request.user.is_authenticated :
        return redirect('fintech:index')
      
    if request.method == 'POST' :
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None :
            login(request, user)
            return redirect('fintech:index')
        else :
            messages.info(request, 'Username or password not found')

    context = {}
    return render(request, 'fintech/login.html', context)

def register(request) :
    if request.user.is_authenticated :
        return redirect('fintech:index')

    form = CreateUserForm()

    if request.method == 'POST' :
        form = CreateUserForm(request.POST)
        if form.is_valid() :
            form.save()
            messages.success(request, 'Account was successfully registered')
            return redirect('fintech:login')

    context = {'form':form}
    return render(request, 'fintech/register.html', context)

def index(request) :
    return render(request, 'fintech/index.html', {})

def logout_user(request) :
    logout(request)

    return redirect('fintech:login')