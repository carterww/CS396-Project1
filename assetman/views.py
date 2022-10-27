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
from .helpviews import handle_add_stock, handle_add_property, handle_add_bond, handle_add_misc

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

@login_required(login_url='/login')
def editAsset(request, trade_id) :
    responseCode, currHolding, assetTrade = check_auth_and_grab_trade(request, trade_id)

    assetType, asset = get_asset_type(currHolding)

    context = {}

    if request.method != 'POST' :
        context = {
            'asset': assetTrade.FK_asset_trade,
            'assetType': assetType,
            'asset': asset,
        }

    if responseCode == 401 :
        return HttpResponse("You are not authorized to edit this asset", status=401)

    if request.method == 'POST' :
        0

    return render(request, 'assetman/edit_asset.html', context)

@login_required(login_url='/login')
def addAsset(request) :
    context = {}
    if request.method == 'POST':
        assetType = request.POST.get('assetType')
        if assetType == 's' :
            handle_add_stock(request)
        elif assetType == 'p' :
            handle_add_property(request)
        elif assetType == 'b' :
            handle_add_bond(request)
        elif assetType == 'm' :
            handle_add_misc(request)

        return redirect('/assets/')
    return render(request, 'assetman/add_asset.html', context)

# when user "sells" an asset they delete here
# due to scope of system user can either delete the whole quanity, not part of it
# if they would like to buy/sell extra they must edit
@login_required(login_url='/login')
def deleteAsset(request, trade_id):
    responseCode, currHolding, assetTrade = check_auth_and_grab_trade(request, trade_id)

    if responseCode == 401 :
        return HttpResponse("You are not authorized to delete this asset", status=responseCode)

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

def check_auth_and_grab_trade(request, trade_id) :
    currHolding = get_object_or_404(CurrentHoldings, FK_trade=trade_id)
    assetTrade = currHolding.FK_trade

    userTrade = get_object_or_404(UserTrade, FK_trade=trade_id)

    if userTrade.FK_user != request.user :
        return 401, None, None
    
    return 200, currHolding, assetTrade

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
        assetType, asset = get_asset_type(holding)
        if assetType == 's' :
            heldStocks.append(asset)
        elif assetType == 'p' :
            heldProperties.append(asset)
        elif assetType == 'b' :
            heldBonds.append(asset)
        else :
            heldMiscAssets.append(asset)

    return heldStocks, heldProperties, heldBonds, heldMiscAssets

def get_asset_type(holding) :
    assetId = holding.FK_trade.FK_asset_trade.id
    s = Stock.objects.filter(FK_asset_stock=assetId).first()
    if s is not None :
        return 's', StockTrade(s, holding.FK_trade)
    p = Property.objects.filter(FK_asset_property=assetId).first()
    if p is not None :
        return 'p', PropertyTrade(p, holding.FK_trade)
    b = Bond.objects.filter(FK_asset_bond=assetId).first()
    if b is not None :
        return 'b', BondTrade(b, holding.FK_trade)
    m = MiscAsset.objects.filter(FK_asset_misc=assetId).first()
    
    return 'm', MiscTrade(m, holding.FK_trade)