from django.urls import path

from . import views

app_name = 'assetman'

# holds all the urls and views they are associated with
urlpatterns = [
    path('', views.home, name='assets'),
    path('sell/<int:trade_id>/', views.sellAsset, name='deleteAsset'),
    path('addasset/', views.addAsset, name='addAsset'),
    path('editasset/<int:trade_id>/', views.editAsset, name='editAsset'),
    path('findtrades/', views.queryTrades, name='queryTrades'),
    path('delete/<int:trade_id>/', views.deleteTrade, name='deleteAsset'),
    path('agentassets/<int:agent_id>/', views.find_agents_assets, name='queryAgentTradesResult'),
    path('agentassets/', views.get_agent_id, name='queryAgentTrades'),
    path('mortgagerates/', views.mortgagerates, name='mortgageRates'),
]