import os
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse
from django.core.files.storage import FileSystemStorage

from .models import Board, DiscussionTopic, Post, Comment, DocumentFile, Notification
from .forms import CreateUserForm, FileForm

# Function for serving file to user
def display_images(request, topic_id, post_id, image_name) :
    post = get_object_or_404(Post, pk=post_id)
    # grab directory file is in
    base_url = getattr(settings, "MEDIA_URL", None)
    base_url = '.' + base_url + str(topic_id) + '/' + str(post_id) + '/' + str(post.FK_user_post.id) + '/'

    # open file
    try :
        img = open(os.path.join(base_url, image_name), 'rb')
    except Exception :
        raise Http404("This image does not exist")
    # return file
    return FileResponse(img)

# grabs latest notification from database
# called for every view function because navigation bar needs it
def get_notifications() :
    notification = None

    try :
        notification = Notification.objects.get(pk=1).text
    except :
        notification = ''

    return notification

# checks users authenticity
def login_(request) :
    notification = get_notifications()

    # redirect an authenticated user to index
    if request.user.is_authenticated :
        return redirect('fintech:index')
      
    if request.method == 'POST' :
        username = request.POST.get('username')
        password = request.POST.get('password')

        # verify user
        user = authenticate(request, username=username, password=password)

        #log them in
        if user is not None :
            login(request, user)
            return redirect('fintech:index')
        else :
            messages.info(request, 'Username or password not found')

    context = {
        'notification': notification,
    }
    return render(request, 'fintech/login.html', context)

# allows user to create account
def register(request) :
    notification = get_notifications()

    # redirect authenticated user
    if request.user.is_authenticated :
        return redirect('fintech:index')
    

    if request.method == 'POST' :
        # grab form information
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_validation = request.POST.get('passwordConfirm')

        # ensure passwords match
        if password_validation != password :
            messages.error(request, 'Passwords do not match')
            return redirect('fintech:register')
        
        # add user to database
        user = User.objects.create_user(username=username, password=password)
        messages.success(request, 'Account was successfully registered')
        return redirect('fintech:login')
    context = {
        'notification': notification,
    }
    return render(request, 'fintech/register.html', context)

# home page that displays all topics and 2 of the latest posts from each
def index(request) :
    # grab relevant info from database
    boards = Board.objects.all()
    topics = DiscussionTopic.objects.all()
    some_posts = []
    numposts = Post.objects.all().__len__
    notification = get_notifications()

    i = 0
    for topic in topics :
        tmp = Post.objects.filter(FK_discussiontopic_post=topic)
        n = len(tmp) - 2 if len(tmp) - 2 >= 0 else 0
        some_posts.append(tmp[n:None])
        i += 1

    # zip into one array
    topics = zip(topics, some_posts)
    context = {
        'boards': boards,
        'topics': topics,
        'numposts': numposts,
        'notification' : notification,
    }


    return render(request, 'fintech/index.html', context)

# displays a post
def view_post(request, topic_id, post_id) :
    # grab info from database
    topic = DiscussionTopic.objects.get(id=topic_id)
    post = Post.objects.get(FK_discussiontopic_post=topic, id=post_id)
    comments = Comment.objects.filter(FK_post_comment=post)
    files = DocumentFile.objects.filter(FK_post_document=post)
    notification = get_notifications()

    context = {
        'post': post,
        'comments': comments,
        'topic_id': topic_id,
        'post_id': post_id,
        'files':files,
        'user':request.user,
        'notification':notification,
    }
    # increment the post's view count
    post.views = post.views + 1
    post.save(update_fields=['views'])

    return render(request, 'fintech/post.html', context)

# post a comment under a post
@login_required(login_url='/login')
def post_comment(request, topic_id, post_id) :
    # url for redirect
    url = '/topic/' + str(topic_id) + '/' + str(post_id) + '/'

    if request.method != 'POST' :
        return redirect(url)

    args = {
        # grab info from form
        'content_text': request.POST.get('create_comment'),
        'FK_post_comment' : Post.objects.get(id=post_id),
        'FK_user_comment' : request.user,
    }
    # create new comment
    comment = Comment(**args)
    comment.save()

    context = {}

    return redirect(url)

# add a post to database
@login_required(login_url='/login')
def create_post(request, topic_id) :
    # grab info from db
    topic = DiscussionTopic.objects.get(id=topic_id)
    notification_old = get_notifications()
        
    if request.method == 'POST' :
        # grab info from form
        post_title = request.POST.get('post_title')
        content = request.POST.get('post_content')
        user = request.user
        files = request.FILES.getlist('content')

        args = {
            'title': post_title,
            'content_text': content,
            'FK_user_post': user,
            'FK_discussiontopic_post': topic,
        }
        # create new post and save to db
        new_post = Post(**args)
        new_post.save()

        # update notification
        notification = get_object_or_404(Notification, pk=1)
        notification.text = 'New post by ' + user.username + ' under the topic: ' + topic.topic_name
        notification.save(update_fields=['text'])

        # save file to project's file system
        for f in files :
            handle_uploaded_file(f, str(topic_id), str(new_post.id), str(user.id))

        # save file info to database
        for f in files :
            new_document = DocumentFile(content=f.name,
            FK_user_document=user,
            FK_post_document=new_post,
            path_to_file='./media/' + str(topic_id) + '/' + str(new_post.id) + '/' + str(user.id)
            )
            new_document.save()

        return redirect('/topic/' + str(topic_id) + "/" + str(new_post.id) + "/")
    context= {
        'form' : FileForm(request.POST, request.FILES),
        'topic': topic,
        'notification': notification_old,
    }

    return render(request, 'fintech/create_post.html', context)

# returns false if user is post's user or superuser
def authenticate_for_update(request, user) :
    if not(request.user == user or request.user.is_superuser) :
        return True
    return False

# finds all a post's associated files
def return_post_files(user, post) :
    files = None
    
    try :
        files = DocumentFile.objects.filter(FK_user_document=user, FK_post_document=post)
    except :
        files = []
    return files

# handles when user wants to edit a post
@login_required(login_url='/login')
def edit_post(request, topic_id, post_id) :
    # grab info from database
    topic = get_object_or_404(DiscussionTopic, pk=topic_id)
    post = get_object_or_404(Post, pk=post_id, FK_discussiontopic_post=topic)
    user = post.FK_user_post
    notification = get_notifications()

    # authenticate user
    if authenticate_for_update(request, user):
        return redirect('/topic/' + str(topic_id) + '/' + str(post_id))
    
    # find all files
    files = return_post_files(user, post)

    if post is not None and request.method == 'POST' :
        # grab info from form
        new_title = request.POST.get('post_title')
        new_text = request.POST.get('post_content')
        new_files = request.FILES.getlist('content')

        # deletes file if radio button is checked
        radio = request.POST.get('deletefiles', False)
        if radio == 'on' :
            for f in files :
                f.delete()

        # update post
        post.title = new_title
        post.content_text = new_text
        post.save(update_fields=['title', 'content_text'])

        # save new files to file system
        for f in new_files :
            handle_uploaded_file(f, str(topic_id), str(post.id), str(user.id))

        # save file info to db
        for f in new_files :
            new_document = DocumentFile(content=f.name,
            FK_user_document=user,
            FK_post_document=post,
            path_to_file='./media/' + str(topic_id) + '/' + str(post.id) + '/' + str(user.id)
            )
            new_document.save()
        return redirect('/topic/' + str(topic_id) + '/' + str(post_id) + '/')

    context = {
        'post': post,
        'topic': topic,
        'files': files,
        'notification':notification,
    }
    return render(request, 'fintech/edit_post.html', context)

# deletes a post  
@login_required(login_url='/login')
def delete_post(request, topic_id, post_id) :
    # grab relevant info from db
    topic = get_object_or_404(DiscussionTopic, pk=topic_id)
    post = get_object_or_404(Post, pk=post_id, FK_discussiontopic_post=topic)
    user = post.FK_user_post

    #authenticate user
    if authenticate_for_update(request, user) :
        return redirect('/topic/' + str(topic_id) + '/' + str(post_id))

    post.delete()

    return redirect('/topic/' + str(topic_id) + '/')

# finds correct directory for file f and saves it
def handle_uploaded_file(f, topic_id, post_id, user_id):  
    fs = FileSystemStorage('media/' + topic_id + '/' + post_id + '/' + user_id + '/')
    filename = fs.save(f.name, f)

# displays topic
def view_topic(request, topic_id) :
    # grab info related to topic
    topic = DiscussionTopic.objects.get(id=topic_id)
    posts = Post.objects.filter(FK_discussiontopic_post=topic)
    notification = get_notifications()

    context = {
        'topic': topic,
        'posts':posts,
        'notification': notification,
    }

    return render(request, 'fintech/topic.html', context)

# logs user out
def logout_user(request) :
    logout(request)  # django handles this

    return redirect('fintech:login')