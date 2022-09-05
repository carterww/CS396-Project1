import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib import messages
from django.http import FileResponse

from .models import Board, DiscussionTopic, Post, Comment
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
    boards = Board.objects.all()
    topics = DiscussionTopic.objects.all()

    context = {
        'boards': boards,
        'topics': topics,
    }


    return render(request, 'fintech/index.html', context)

def view_post(request, topic_id, post_id) :
    topic = DiscussionTopic.objects.get(id=topic_id)
    post = Post.objects.get(FK_discussiontopic_post=topic, id=post_id)
    comments = Comment.objects.filter(FK_post_comment=post)

    context = {
        'post': post,
        'comments': comments,
        'topic_id': topic_id,
        'post_id': post_id,
    }

    return render(request, 'fintech/post.html', context)

def post_comment(request, topic_id, post_id) :
    url = '/topic/' + str(topic_id) + '/' + str(post_id) + '/'

    if request.method != 'POST' :
        return redirect(url)

    args = {
        'content_text': request.POST.get('create_comment'),
        'FK_post_comment' : Post.objects.get(id=post_id),
        'FK_user_comment' : request.user,
    }
    comment = Comment(**args)
    comment.save()

    context = {

    }

    return redirect(url)

def create_post(request, topic_id) :
    if request.method == 'POST' :
        post_title = request.POST.get('post_title')
        content = request.POST.get('post_content')
        user = request.user
        topic = DiscussionTopic.objects.get(id=topic_id)

        args = {
            'title': post_title,
            'content_text': content,
            'FK_user_post': user,
            'FK_discussiontopic_post': topic,
        }
        new_post = Post(**args)
        new_post.save()

        return redirect('/topic/' + str(topic_id) + "/" + str(new_post.id) + "/")

    context= {

    }

    return render(request, 'fintech/create_post.html', context)

def view_topic(request, topic_id) :
    topic = DiscussionTopic.objects.get(id=topic_id)
    posts = Post.objects.filter(FK_discussiontopic_post=topic)

    context = {
        'topic': topic,
        'posts':posts,
    }

    return render(request, 'fintech/topic.html', context)

def logout_user(request) :
    logout(request)

    return redirect('fintech:login')