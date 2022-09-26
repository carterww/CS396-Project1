from django.urls import path

from . import views

app_name = 'fintech'

# holds all the urls and views they are associated with
urlpatterns = [
    path('login/', views.login_, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_user, name='logout'),
    path('', views.index, name='index'),
    path('topic/<int:topic_id>/<int:post_id>/editpost/deletepost/', views.delete_post, name='delete_post'),
    path('topic/<int:topic_id>/<int:post_id>/', views.view_post, name='view_post'),
    path('topic/<int:topic_id>/<int:post_id>/editpost/', views.edit_post, name='edit_post'),
    path('topic/<int:topic_id>/createpost/', views.create_post, name="create_post"),
    path('topic/<int:topic_id>/', views.view_topic, name='view_topic'),
    path('topic/<int:topic_id>/<int:post_id>/media/<str:image_name>/', views.display_images, name='display_images'),
    path('topic/<int:topic_id>/<int:post_id>/postcomment/', views.post_comment, name="post_comment"),
]