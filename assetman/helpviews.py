from .models import *
from .joinedmodels import *

from django.conf import settings

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plot

def expense_SMA(expenses, user):
    data = {}
    for exp in expenses:
        try :
            data[exp.date] = data[exp.date] + exp.amount
        except :
            data[exp.date] = exp.amount

    window = len(data)
    if window >= 300 :
        window = 50
    elif window >= 100 :
        window = 20
    elif window >= 10 :
        window = 5
    else :
        window = 2

    values = pd.Series(data.values(), copy=False)
    values = values.rolling(window=window).mean()
    fig, g = plot.subplots()
    
    g.plot(data.keys(), values, label=f"{window} Day Simple Moving Average", color="red")
    g.set_title(f'Simple Moving Average of {user.username}\'s Expenditures')
    g.set_xlabel('Date')
    g.set_ylabel('Amount ($)')
    g.xaxis.set_major_formatter(mpl.dates.DateFormatter('%b %Y'))
    g.set_xticks(g.get_xticks()[::2])
    g.legend()
    #graph = stock.reset_index().plot(x="Date", y="Close", kind="line")
    #plt.plot(stock["SMA"], label="SMA")
    
    #fig = plt.gcf()
    fig.savefig(settings.MEDIA_ROOT + '/' + user.username  + 'expensesma' + '.png')
    return  '/media/' + user.username  + 'expensesma' + '.png'

def make_income_and_expense_bar_graph(expenses, year_income, user) :
    labels_and_values = {
        'income': year_income,
    }
    running_total = 0
    labelz = []
    colors = ['blue', 'red', 'green', 'yellow', 'cyan', 'black', 'gray', 'purple', 'brown', 'orange', 'olive', 'pink']

    for exp in expenses :
        running_total += exp.amount
    labels_and_values['expenses'] = running_total
    labels_and_values['assets'] = get_total_asset_value(user)

    i = 0
    for key in labels_and_values :
        label = key.capitalize()
        labelz.append(label)
        i += 1
    
    colors = colors[0:i]

    fig, ax = plot.subplots()
    ax.set_title(f'Income, Expenses, and Assets for {user.username}')
    ax.set_ylabel('Total Amount ($)')
    ax.set_xlabel('Category')
    bars = ax.bar(labelz, labels_and_values.values(), color=colors)

    ax.bar_label(bars)
    fig.set_size_inches(12, 7)
    fig.savefig(settings.MEDIA_ROOT + '/' + user.username + 'barchart.png')

    return  '/media/' + user.username + 'barchart.png'

def make_expense_pie_chart(expenses, user) :
    labels_and_values = {}
    running_total = 0
    labelz = []

    for exp in expenses :
        running_total += exp.amount
        try :
            labels_and_values[exp.category.category_name] = labels_and_values[exp.category.category_name] + exp.amount
        except:
            labels_and_values[exp.category.category_name] = exp.amount

    for key in labels_and_values :
        label = key.capitalize()
        label += ' ' + f'(${labels_and_values[key]:,})'
        labelz.append(label)

    for key, value in labels_and_values.items():
        labels_and_values[key] = value / running_total

    fig1, ax1 = plot.subplots()
    wedges, plt_labels, junk = ax1.pie(labels_and_values.values(), labels=labelz, autopct='%1.1f%%', shadow=True)
    ax1.axis('equal')
    ax1.set_title('Expense Breakdown for ' + user.username)

    for w in wedges:
        w.set_linewidth(.5)
        w.set_edgecolor('black')

    fig1.savefig(settings.MEDIA_ROOT + '/' + user.username + 'piechart.png')

    return  '/media/' + user.username + 'piechart.png'


def handle_add_stock(request):
    asset = None
    stock = None

    try :
        stock = Stock.objects.get(ticker=request.POST.get('ticker').upper())
        asset = Asset.objects.get(id=stock.FK_asset_stock.id)
    except :
        stock = None

    assetArgs = {
        'assetName': request.POST.get('name').lower(),
    }

    stockArgs = {
        'ticker': request.POST.get('ticker').upper(),
        # add FK_asset_stock when asset created
    }


    agent = create_agent(request, 'firm')

    tradeArgs = create_trade_args(request, agent, request.POST.get('quantity'))

    if stock is None and asset is None :
        asset = Asset(**assetArgs)
        stockArgs["FK_asset_stock"] = asset
        stock = Stock(**stockArgs)
        asset.save()
        stock.save()
    
    tradeArgs["FK_agent_trade"] = agent
    tradeArgs["FK_asset_trade"] = asset

    trade = Trade(**tradeArgs)
    trade.save()

    holding = CurrentHoldings(FK_trade=trade)
    holding.save()

    userTrade = UserTrade(FK_user=request.user, FK_trade=trade)
    userTrade.save()

    add_user_trades(get_other_users(request), trade)
    



def handle_add_property(request):
    addressArgs = {
        'street': request.POST.get('street').lower(),
        'zipCode': request.POST.get('zip'),
        'state': request.POST.get('state').lower(),
        'city': request.POST.get('city').lower(),
    }

    if request.POST.get('unit') != '' :
        addressArgs['unitNum'] = request.POST.get('unit')

    address = update_model(Address(), addressArgs)
    
    assetArgs = {
        'assetName': request.POST.get('name')
    }

    asset = update_model(Asset(), assetArgs)

    propertyArgs = {
        'totalfee': request.POST.get('fee'),
        'FK_address_property': address,
        'FK_asset_property': asset,
    }

    update_model(Property(), propertyArgs)

    agent = create_agent(request, "person")

    tradeArgs = create_trade_args(request, agent, 1)
    tradeArgs["FK_asset_trade"] = asset

    trade = Trade(**tradeArgs)
    trade.save()

    holding = CurrentHoldings(FK_trade=trade)
    holding.save()

    userTrade = UserTrade(FK_user=request.user, FK_trade=trade)
    userTrade.save()

    add_user_trades(get_other_users(request), trade)
    

def handle_add_bond(request):
    asset = Asset(assetName=request.POST.get('name').lower())
    asset.save()

    bondArgs = {
        'maturityDate': request.POST.get('maturity'),
        'interestRate': request.POST.get('rate'),
        'faceValue': request.POST.get('face'),
        'issuer': request.POST.get('issuer').lower(),
        'rating': request.POST.get('rating'),
        'FK_asset_bond': asset,
    }
    
    agent = create_agent(request, "firm")

    tradeArgs = create_trade_args(request, agent, request.POST.get('quantity'))
    tradeArgs['FK_asset_trade'] = asset

    bond = update_model(Bond(), bondArgs)
    trade = update_model(Trade(), tradeArgs)

    holding = CurrentHoldings(FK_trade=trade)
    holding.save()

    userTrade = UserTrade(FK_user=request.user, FK_trade=trade)
    userTrade.save()

    add_user_trades(get_other_users(request), trade)

def handle_add_misc(request):
    asset = Asset(assetName=request.POST.get('name').lower())
    asset.save()

    miscArgs = {
        'description': request.POST.get('description').lower(),
        'FK_asset_misc': asset
    }

    agent = create_agent(request, "person")

    update_model(MiscAsset(), miscArgs)

    tradeArgs = create_trade_args(request, agent, request.POST.get('quantity'))
    tradeArgs['FK_asset_trade'] = asset
    trade = update_model(Trade(), tradeArgs)

    holding = CurrentHoldings(FK_trade=trade)
    holding.save()

    userTrade = UserTrade(FK_user=request.user, FK_trade=trade)
    userTrade.save()

    add_user_trades(get_other_users(request), trade)


def handle_edit_stock(request, trade_id) :
    asset = None
    stock = None

    try :
        stock = Stock.objects.get(ticker=request.POST.get('ticker').upper())
        asset = Asset.objects.get(id=stock.FK_asset_stock.id)
    except :
        stock = None

    if stock is None and asset is None :
        assetArgs = {
            'assetName': request.POST.get('name').lower(),
        }
        stockArgs = {
            'ticker': request.POST.get('ticker').upper(),
            # add FK_asset_stock when asset created
        }
        asset = update_model(Asset(), assetArgs)
        stockArgs['FK_asset_stock'] = asset
        stock = update_model(Stock(), stockArgs)

    trade = get_object_or_404(Trade, pk=trade_id)
    update_trade(request, trade, "firm", asset)

def handle_edit_property(request, trade_id) :
    trade = get_object_or_404(Trade, pk=trade_id)
    prop = get_object_or_404(Property, pk=trade.FK_asset_trade.id)

    propArgs = {
        'totalfee': request.POST.get('fee')
    }
    addressArgs = {
        'street': request.POST.get('street').lower(),
        'city': request.POST.get('city').lower(),
        'state': request.POST.get('state').lower(),
        'zip': request.POST.get('zip'),
    }

    if request.POST.get('unit') != '':
        addressArgs['unitNum'] = request.POST.get('unit')
    else :
        addressArgs['unitNum'] = None

    assetArgs = {
        'assetName': request.POST.get('name').lower()
    }

    update_model(prop, propArgs)
    update_model(prop.FK_address_property, addressArgs)
    update_model(prop.FK_asset_property, assetArgs)
    update_trade(request, trade, "person", None)

def handle_edit_bond(request, trade_id):
    trade = get_object_or_404(Trade, pk=trade_id)
    bond = get_object_or_404(Bond, pk=trade.FK_asset_trade.id)

    bondFields = {
        'maturityDate': request.POST.get('maturity'),
        'interestRate': request.POST.get('rate'),
        'faceValue': request.POST.get('face'),
        'issuer': request.POST.get('issuer').lower(),
        'rating': request.POST.get('rating')
    }

    assetFields = {
        'assetName': request.POST.get('name').lower()
    }

    update_model(bond, bondFields)
    update_model(bond.FK_asset_bond, assetFields)
    update_trade(request, trade, "firm", None)

def handle_edit_misc(request, trade_id) :
    trade = get_object_or_404(Trade, pk=trade_id)
    misc = get_object_or_404(MiscAsset, pk=trade.FK_asset_trade.id)

    misc.description = request.POST.get('description').lower()
    misc.FK_asset_misc.assetName = request.POST.get('name').lower()

    misc.save()
    misc.FK_asset_misc.save()

    update_trade(request, trade, "person", None)

def update_trade(request, trade, agent_type, new_asset) :
    new_broker = create_agent(request, agent_type)

    fields = create_trade_args(request, new_broker, request.POST.get('quantity'))
    if new_asset is not None :
        fields['FK_asset_trade'] = new_asset
    
    update_model(trade, fields)


def create_trade_args(request, agent, quantity) :
    tradeArgs = {
        'action': 'B',
        'tradeDate': request.POST.get('date'),
        'pricePerAsset': request.POST.get('price'),
        # add FK_asset_trade when asset created
    }
    if quantity is not None :
        tradeArgs['assetQuantity'] = quantity
    if agent is not None :
        tradeArgs['FK_agent_trade'] = agent

    return tradeArgs

def create_agent(request, type_) :
    agent = None
    if request.POST.get('agent') == '' :
        return None
    try :
        if type_ == 'firm' :
            agent = Agent.objects.get(firmName=request.POST.get('agent').lower())
        elif type_ == 'person' :
            agent = Agent.objects.get(name=request.POST.get('agent').lower())
    except :
        if agent is None :
            if type_ == 'firm' :
                agent = Agent(firmName=request.POST.get('agent').lower())
                agent.save()
            elif type_ == 'person' :
                agent = Agent(name=request.POST.get('agent').lower())
                agent.save()

    return agent

def get_other_users(request) :
    numUsers = int(request.POST.get('numusers'))
    otherUserIDs = []
    if numUsers > 0 :
        i = 1
        while i <= numUsers + 1 :
            username = request.POST.get('user' + str(i))
            if username is not None or username != '' :
                user = None
                try :
                    user = User.objects.get(username=username)
                    if user == request.user :
                        i += 1
                        continue
                except :
                    i += 1
                    continue

                if user is not None :
                    otherUserIDs.append(user.id)
            i += 1


    return otherUserIDs

def add_user_trades(otherUserIDs, trade) :
    for user in otherUserIDs :
        userTradeOtherArgs = {
            'FK_user': User.objects.get(pk=user),
            'FK_trade': trade,
        }
        update_model(UserTrade(), userTradeOtherArgs)

# updates and creates a model instance
def update_model(model, diction) :
    """
    Pass in a model to be added to db updated with dictionary of model attribute mapped to new value.
    If you are creating a new instance of a model, pass in an empty one. If you are updating a model, pass
    the existing model to be updated with a dictionary of changed model attributes. Returns the model in case
    the user needs it to complete others.
    """
    for key, value in diction.items() :
        setattr(model, key, value)
    model.save()

    return model

def calculate_gain(user, date_begin, date_end) :
    userTrades = UserTrade.objects.filter(FK_user=user)

    gain = 0
    purchase_price = 0


    buys = {}

    for ut in userTrades :
        if (ut.FK_trade.tradeDate <= date_end and ut.FK_trade.tradeDate >= date_begin) :
            if (ut.FK_trade.action == 'B') :
                buys[ut.FK_trade.id] = ut.FK_trade
                continue
            else :
                try :
                    trade = buys[ut.FK_trade.FK_trade.id]
                except:
                    continue
                if (trade.id == ut.FK_trade.FK_trade.id) :
                    purchase_price += trade.assetQuantity * float(trade.pricePerAsset)
                    gain += (ut.FK_trade.assetQuantity * float(ut.FK_trade.pricePerAsset)) - (trade.assetQuantity * float(trade.pricePerAsset))
                del buys[ut.FK_trade.FK_trade.id]
    if purchase_price == 0 :
        return 0, 0
    return gain, (gain / purchase_price * 100)


def get_total_asset_value(user):
    userTrades = UserTrade.objects.filter(FK_user=user)

    buys = {}
    amount = 0

    for ut in userTrades :
        if (ut.FK_trade.action == 'B') :
            buys[ut.FK_trade.id] = ut.FK_trade
            continue
        else :
            try :
                trade = buys[ut.FK_trade.FK_trade.id]
            except:
                continue
            if (trade.id == ut.FK_trade.FK_trade.id) :
                del buys[ut.FK_trade.FK_trade.id]
    
    for key, value in buys.items() :
        amount += (float((value.pricePerAsset)) * float((value.assetQuantity)))

    return float(amount)
