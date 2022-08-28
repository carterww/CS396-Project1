from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib import messages

from .forms import CreateUserForm

# Create your views here.


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