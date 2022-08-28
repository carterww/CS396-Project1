from django.urls import path

from . import views

app_name = 'fintech'

urlpatterns = [
    path('login/', views.login_, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_user, name='logout'),
    path('', views.index, name='index'),
]