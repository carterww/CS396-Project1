from django.urls import path

from . import views

app_name = 'fintech'

urlpatterns = [
    path('login/', views.login_, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_user, name='logout'),
    path('', views.index, name='index'),
    path('topic/<int:topic_id>/<int:post_id>/', views.view_post, name='view_post'),
    path('topic/<int:topic_id>/', views.view_topic, name='view_topic'),
    path('media/<str:image_name>/', views.display_images, name='display_images'),
]