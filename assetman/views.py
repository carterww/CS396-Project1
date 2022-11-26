from ctypes import sizeof
import datetime
import yfinance as yf
import schedule
from django.shortcuts import render
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.http import FileResponse
from django.core.files.storage import FileSystemStorage


from .models import *
from .joinedmodels import *
from .helpviews import *
import os

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

    if responseCode == 401 :
        return HttpResponse("You are not authorized to edit this asset", status=401)


    assetType, asset = get_asset_type(currHolding)

    context = {}

    if request.method != 'POST' :
        context = {
            'asset': assetTrade.FK_asset_trade,
            'assetType': assetType,
            'asset': asset,
        }

    if request.method == 'POST' :
        if assetType == 's' :
            handle_edit_stock(request, trade_id)
        elif assetType == 'p' :
            handle_edit_property(request, trade_id)
        elif assetType == 'b' :
            handle_edit_bond(request, trade_id)
        elif assetType == 'm' :
            handle_edit_misc(request, trade_id)
        return redirect('/assets/')

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
def sellAsset(request, trade_id):
    if request.method == 'POST' :
        responseCode, currHolding, assetTrade = check_auth_and_grab_trade(request, trade_id)

        if responseCode == 401 :
            return HttpResponse("You are not authorized to delete this asset", status=responseCode)

        sellTradeArgs = {
            'action': 'S',
            'assetQuantity': assetTrade.assetQuantity,
            'FK_asset_trade': assetTrade.FK_asset_trade,
            'FK_agent_trade': assetTrade.FK_agent_trade,
            'pricePerAsset': request.POST.get('price'),
            'tradeDate': request.POST.get('date'),
            'FK_trade': assetTrade
        }

        otherUsers = UserTrade.objects.filter(FK_trade=currHolding.FK_trade)

        if currHolding is not None :
            currHolding.delete()
        sellTrade = Trade(**sellTradeArgs)
        sellTrade.save()

        for user in otherUsers :
            UserTrade(FK_trade=sellTrade, FK_user=user.FK_user).save()

        return redirect('/assets/')

    return render(request, 'assetman/sell_asset.html', {})

@login_required(login_url='/login')
def deleteTrade(request, trade_id) :
    trade = get_object_or_404(Trade, pk=trade_id)
    trade.delete()

    return redirect('/assets/')

@login_required(login_url='/login')
def queryTrades(request): 

    context = {}

    if request.method == 'POST' :
        trades = Trade.objects.filter(tradeDate=request.POST.get('date'))
        trades2 = []

        for trade in trades :
            try :
                UserTrade.objects.get(FK_trade=trade, FK_user=request.user)
                trades2.append(trade)
            except :
                0

        context['trades'] = trades2

        return render(request, 'assetman/showtrade.html', context)

    return render(request, 'assetman/querytrade.html', context)

@login_required(login_url='/login')
def find_agents_assets(request, agent_id) :
    agent_trades = Trade.objects.filter(FK_agent_trade=agent_id)
    context = {}
    assetNames = {}

    for trade in agent_trades :
        try :
            holding = CurrentHoldings.objects.get(FK_trade=trade)
        except :
            continue

        assetType, asset = get_asset_type(holding)

        if assetType == 's' :
            assetNames[asset.Stock.ticker] = 'Stock: '
        elif assetType == 'p' :
            assetNames[asset.Property.FK_address_property.city] = 'At least one Property in '
        elif assetType == 'b' :
            assetNames[asset.Bond.issuer] = 'Bond from '
        elif assetType == 'm' :
            assetNames[asset.Misc.FK_asset_misc.assetName + asset.Misc.description[0:5] + '...'] = 'Misc'

        context['assets'] = assetNames

    return render(request, 'assetman/agent_trades.html', context)

@login_required(login_url='/login')
def account_settings(request) :
    context = {}
    fintechUser = None

    try :
        fintechUser = FintechUser.objects.get(pk=request.user)
        context['age'] = fintechUser.age
        context['sex'] = fintechUser.sex
        context['occupation'] = fintechUser.occupation
        context['income'] = fintechUser.yearly_income
    except :
        fintechUser = FintechUser()
        context['age'] = ''
        context['sex'] = ''
        context['occupation'] = ''
        context['income'] = None

    if request.method == 'POST':
        fintechUser.age = request.POST.get('age')
        fintechUser.sex = request.POST.get('sex').lower()
        fintechUser.occupation = request.POST.get('occupation').lower()
        fintechUser.yearly_income = request.POST.get('yearly_income')

        fintechUser.save()

        return redirect('/assets/')

    return render(request, 'assetman/accountsettings.html', context)

@login_required(login_url='/login')
def get_gain(request):
    if request.method == 'POST':
        date_begin = datetime.datetime.strptime(request.POST.get('begin'), '%Y-%m-%d').date()
        date_end = datetime.datetime.strptime(request.POST.get('end'), '%Y-%m-%d').date()

        gainD, gainP = calculate_gain(request.user, date_begin, date_end)

        context = {
            'gainD': gainD,
            'gainP': gainP,
            'begin': request.POST.get('begin'),
            'end': request.POST.get('end'),
        }

        return render(request, 'assetman/gain.html', context)
    
    return render(request, 'assetman/gainform.html', {})

def display_images(request, image_url) :
    # open file
    try :
        img = open(image_url, 'rb')
    except Exception :
        raise Http404("This image does not exist")
    # return file
    return FileResponse(img)

# handle expenses view and form page
@login_required(login_url='/login')
def expenses(request) :
    context = {
        'categories': ExpenseCategory.objects.all(),
        'today': datetime.datetime.today
    }


    if request.method == 'GET':
        expenses = Expense.objects.filter(FK_user_expense=request.user)

        if request.GET.get('filter_year') is not None:
            if request.GET.get('filter_year') != '':
                expenses = expenses.filter(date__year=request.GET.get('filter_year'))
        if request.GET.get('filter_month') is not None:
            if request.GET.get('filter_month') != '':
                expenses = expenses.filter(date__month=request.GET.get('filter_month'))
        if request.GET.get('filter_day') is not None:
            if request.GET.get('filter_day') != '':
                expenses = expenses.filter(date__day=request.GET.get('filter_day'))

        context['expenses'] = expenses.order_by('-date')

        total = 0
        for exp in expenses:
            total += exp.amount
        
        context['total'] = total

        context['image'] = make_expense_pie_chart(context['expenses'], request.user)

    if request.method == 'POST':
        expenseArgs= {
            'FK_user_expense': request.user,
            'amount': request.POST.get('amount'),
            'category': ExpenseCategory.objects.get(pk=request.POST.get('category')),
            'date': request.POST.get('date'),
            'description': request.POST.get('description')
        }
        update_model(Expense(), expenseArgs)

        return redirect('/assets/expense')

    return render(request, 'assetman/expense.html', context)

def get_agent_id(request) :
    
    if request.method == 'POST':
        agentName = request.POST.get('name').lower()

        agents = Agent.objects.filter(name=agentName)
        agents2 = Agent.objects.filter(firmName=agentName)

        for agent in agents :
            return redirect('/assets/agentassets/' + str(agent.id) + '/')

        for agent in agents2 :
            return redirect('/assets/agentassets/' + str(agent.id) + '/')



    return render(request, 'assetman/queryagent.html', {})

def mortgagerates(request) :
    rates = MortgageRate.objects.all().order_by('interestRate').values()

    return render(request, 'assetman/mortgagerates.html', {'rates': rates })

def get_stock(request) :
    context = {}

    if request.method == 'POST':
        stock = None
        snapShot = None
        try :
            stock = Stock.objects.get(ticker=request.POST.get('ticker').upper())
            snapShot = StockSnapshot.objects.get(FK_stock_snapshot=stock, snapshotDate=request.POST.get('date'))
            context['stock'] = stock
            context['snapShot'] = snapShot
        except :
            0
        context['date'] = request.POST.get('date')
        return render(request, 'assetman/stock.html', context)

    return render(request, 'assetman/stockform.html', context)


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