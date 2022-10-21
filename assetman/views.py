from ctypes import sizeof
from django.shortcuts import render
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .models import *
from .joinedmodels import *

# Create your views here.

# controller for home page of asset management part of site
@login_required(login_url='/login')
def home(request):
    heldStocks, heldProperties, heldBonds, heldMiscAssets = getHoldings(request.user.id)

    context = {
        'stocks': heldStocks,
        'properties': heldProperties,
        'bonds': heldBonds,
        'misc': heldMiscAssets,
    }

    return render(request, 'assetman/home.html', context)
    #return render(request, 'assetman/home.html', context)

@login_required(login_url='/login')
def addAsset(request) :

    if request.method == 'POST':
        a = 0
        # check from form which asset type they want to add
        # once they select type from drop list use JS function to dynamically render the necessary fields for the corresponsing asset
        # create and save asset here

    context = {
        
    }
    return render(request, 'assetman/add_asset.html', context)

# when user "sells" an asset they delete here
# due to scope of system user can either delete the whole quanity, not part of it
# if they would like to buy/sell extra they must edit
@login_required(login_url='/login')
def deleteAsset(request, trade_id):
    currHolding = get_object_or_404(CurrentHoldings, FK_trade=trade_id)
    assetTrade = currHolding.FK_trade

    sellTradeArgs = {
        'action': 'S',
        'assetQuantity': assetTrade.assetQuantity,
        'FK_asset_trade': assetTrade.FK_asset_trade,
        'FK_agent_trade': assetTrade.FK_agent_trade,
    }

    if currHolding is not None :
        currHolding.delete()
    sellTrade = Trade(**sellTradeArgs)
    sellUserTrade = UserTrade(FK_user=request.user, FK_trade=sellTrade)
    sellTrade.save()
    sellUserTrade.save()

    return redirect('/assets/')

# helper function to get all assets user currently holds
def getHoldings(userID) :
    userTrades = UserTrade.objects.filter(FK_user=userID)
    currentHoldings = []
    for trade in userTrades :
        c = None
        try :
            currentHoldings.append(CurrentHoldings.objects.get(FK_trade=trade.FK_trade))
        except :
            continue
    
    heldStocks = []
    heldProperties = []
    heldBonds = []
    heldMiscAssets = []

    for holding in currentHoldings:
        assetId = holding.FK_trade.FK_asset_trade.id
        s = Stock.objects.filter(FK_asset_stock=assetId).first()
        if s is not None :
            heldStocks.append(StockTrade(s, holding.FK_trade))
            continue
        p = Property.objects.filter(FK_asset_property=assetId).first()
        if p is not None :
            heldProperties.append(PropertyTrade(p, holding.FK_trade))
            continue
        b = Bond.objects.filter(FK_asset_bond=assetId).first()
        if b is not None :
            heldBonds.append(BondTrade(b, holding.FK_trade))
            continue
        m = MiscAsset.objects.filter(FK_asset_misc=assetId).first()
        if m is not None :
            heldMiscAssets.append(MiscTrade(m, holding.FK_trade))

    return heldStocks, heldProperties, heldBonds, heldMiscAssets