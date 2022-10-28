from .models import *
from .joinedmodels import *

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

def handle_add_stock(request):
    asset = None
    stock = None

    try :
        stock = Stock.objects.get(ticker=request.POST.get('ticker'))
        asset = Asset.objects.get(id=stock.FK_asset_stock.id)
    except :
        stock = None

    assetArgs = {
        'assetName': request.POST.get('name'),
    }

    stockArgs = {
        'ticker': request.POST.get('ticker'),
        # add FK_asset_stock when asset created
    }


    agent = create_agent(request, 'firm')

    tradeArgs = create_trade_args(request, agent, request.POST.get('quantity'))

    otherUserIDs = get_other_users(request)

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

    add_user_trades(otherUserIDs, trade)
    



def handle_add_property(request):
    addressArgs = {
        'street': request.POST.get('street'),
        'zipCode': request.POST.get('zip'),
        'state': request.POST.get('state'),
        'city': request.POST.get('city'),
    }

    if request.POST.get('unit') != '' :
        addressArgs['unitNum'] = request.POST.get('unit')

    try :
        address = Address.objects.get(**addressArgs)
        return
    except :
        address = Address(**addressArgs)
        address.save()
    
    assetArgs = {
        'assetName': request.POST.get('name')
    }

    asset = Asset(**assetArgs)
    asset.save()

    propertyArgs = {
        'totalfee': request.POST.get('fee'),
        'FK_address_property': address,
        'FK_asset_property': asset,
    }

    property_ = Property(**propertyArgs)
    property_.save()

    agent = create_agent(request, "person")

    tradeArgs = create_trade_args(request, agent, 1)
    tradeArgs["FK_asset_trade"] = asset

    trade = Trade(**tradeArgs)
    trade.save()

    holding = CurrentHoldings(FK_trade=trade)
    holding.save()

    userTrade = UserTrade(FK_user=request.user, FK_trade=trade)
    userTrade.save()

    otherUserIDs = get_other_users(request)

    add_user_trades(otherUserIDs, trade)
    

def handle_add_bond(request):
    asset = Asset(assetName=request.POST.get('name'))
    asset.save()

    bondArgs = {
        'maturityDate': request.POST.get('maturity'),
        'interestRate': request.POST.get('rate'),
        'faceValue': request.POST.get('face'),
        'issuer': request.POST.get('issuer'),
        'rating': request.POST.get('rating'),
        'FK_asset_bond': asset,
    }
    
    agent = create_agent(request, "firm")

    tradeArgs = create_trade_args(request, agent, request.POST.get('quantity'))
    tradeArgs['FK_asset_trade'] = asset

    bond = Bond(**bondArgs)
    bond.save()
    trade = Trade(**tradeArgs)
    trade.save()

    holding = CurrentHoldings(FK_trade=trade)
    holding.save()

    userTrade = UserTrade(FK_user=request.user, FK_trade=trade)
    userTrade.save()

    add_user_trades(get_other_users(request), trade)

def handle_add_misc(request):
    asset = Asset(assetName=request.POST.get('name'))
    asset.save()

    miscArgs = {
        'description': request.POST.get('description'),
        'FK_asset_misc': asset
    }

    agent = create_agent(request, "person")

    misc = MiscAsset(**miscArgs)
    misc.save()

    tradeArgs = create_trade_args(request, agent, request.POST.get('quantity'))
    tradeArgs['FK_asset_trade'] = asset
    trade = Trade(**tradeArgs)
    trade.save()

    holding = CurrentHoldings(FK_trade=trade)
    holding.save()

    userTrade = UserTrade(FK_user=request.user, FK_trade=trade)
    userTrade.save()

    add_user_trades(get_other_users(request), trade)


def handle_edit_stock(request, trade_id) :
    asset = None
    stock = None

    try :
        stock = Stock.objects.get(ticker=request.POST.get('ticker'))
        asset = Asset.objects.get(id=stock.FK_asset_stock.id)
    except :
        stock = None

    if stock is None and asset is None :
        assetArgs = {
            'assetName': request.POST.get('name'),
        }
        stockArgs = {
            'ticker': request.POST.get('ticker'),
            # add FK_asset_stock when asset created
        }
        asset = Asset(**assetArgs)
        asset.save()
        stockArgs['FK_asset_stock'] = asset
        stock = Stock(**stockArgs)
        stock.save()

    trade = get_object_or_404(Trade, pk=trade_id)
    update_trade(request, trade, "firm", asset)

def handle_edit_property(request, trade_id) :
    trade = get_object_or_404(Trade, pk=trade_id)
    prop = get_object_or_404(Property, pk=trade.FK_asset_trade.id)

    prop.totalfee = request.POST.get('fee')
    prop.FK_address_property.street = request.POST.get('street')
    prop.FK_address_property.city = request.POST.get('city')
    prop.FK_address_property.state = request.POST.get('state')
    prop.FK_address_property.zipCode = request.POST.get('zip')

    if request.POST.get('unit') != '':
        prop.FK_address_property.unitNum = request.POST.get('unit')
    else :
        prop.FK_address_property.unitNum = None

    prop.FK_asset_property.assetName = request.POST.get('name')

    prop.save()
    prop.FK_address_property.save()
    prop.FK_asset_property.save()

    update_trade(request, trade, "person", None)

def handle_edit_bond(request, trade_id):
    trade = get_object_or_404(Trade, pk=trade_id)
    bond = get_object_or_404(Bond, pk=trade.FK_asset_trade.id)

    bond.maturityDate = request.POST.get('maturity')
    bond.interestRate = request.POST.get('rate')
    bond.faceValue = request.POST.get('face')
    bond.issuer = request.POST.get('issuer')
    bond.rating = request.POST.get('rating')
    bond.FK_asset_bond.assetName = request.POST.get('name')

    bond.save()
    bond.FK_asset_bond.save()

    update_trade(request, trade, "firm", None)

def handle_edit_misc(request, trade_id) :
    trade = get_object_or_404(Trade, pk=trade_id)
    misc = get_object_or_404(MiscAsset, pk=trade.FK_asset_trade.id)

    misc.description = request.POST.get('description')
    misc.FK_asset_misc.assetName = request.POST.get('name')

    misc.save()
    misc.FK_asset_misc.save()

    update_trade(request, trade, "person", None)


def update_trade(request, trade, agent_type, new_asset) :
    new_broker = create_agent(request, agent_type)

    trade.tradeDate = request.POST.get('date')
    trade.pricePerAsset = request.POST.get('price')
    if request.POST.get('quantity') is not None :
        trade.assetQuantity = request.POST.get('quantity')
    if new_broker is not None :
        trade.FK_agent_trade = new_broker
    if new_asset is not None :
        trade.FK_asset_trade = new_asset
    
    trade.save(update_fields=['tradeDate', 'pricePerAsset', 'assetQuantity', 'FK_agent_trade', 'FK_asset_trade'])


def create_trade_args(request, agent, quantity) :
    tradeArgs = {
        'action': 'B',
        'tradeDate': request.POST.get('date'),
        'pricePerAsset': request.POST.get('price'),
        'assetQuantity': quantity,
        # add FK_asset_trade when asset created
    }
    if agent is not None :
        tradeArgs['FK_agent_trade'] = agent

    return tradeArgs

def create_agent(request, type_) :
    agent = None
    if request.POST.get('agent') == '' :
        return None
    try :
        if type_ == 'firm' :
            agent = Agent.objects.get(firmName=request.POST.get('agent'))
        elif type_ == 'person' :
            agent = Agent.objects.get(name=request.POST.get('agent'))
    except :
        if agent is None :
            if type_ == 'firm' :
                agent = Agent(firmName=request.POST.get('agent'))
                agent.save()
            elif type_ == 'person' :
                agent = Agent(name=request.POST.get('agent'))
                agent.save()

    return agent

def get_other_users(request) :
    numUsers = int(request.POST.get('numusers'))
    otherUserIDs = {}
    if numUsers > 0 :
        i = 1
        while i <= numUsers :
            username = request.POST.get('user' + str(i))
            if username is not None or username != '' :
                user = None
                try :
                    user = User.objects.get(username=username)
                except :
                    continue

                if user is not None :
                    otherUserIDs.append(user.id)


    return otherUserIDs

def add_user_trades(otherUserIDs, trade) :
    for user in otherUserIDs :
        userTradeOtherArgs = {
            'FK_user': user,
            'FK_trade': trade,
        }
        userTradeOther = UserTrade(**userTradeOtherArgs)
        userTradeOther.save()
