from django.urls import path

from . import views

app_name = 'assetman'

# holds all the urls and views they are associated with
urlpatterns = [
    path('', views.home, name='assets'),
    path('delete/<int:trade_id>/', views.deleteAsset, name='deleteAsset'),
    path('addasset/', views.addAsset, name='addAsset'),
    path('editasset/<int:trade_id>/', views.editAsset, name='editAsset'),
    path('findtrades/', views.queryTrades, name='queryTrades'),
]