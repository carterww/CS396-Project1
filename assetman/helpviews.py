from .models import *
from .joinedmodels import *

from django.contrib.auth.models import User

def handle_add_stock(request):
    asset = None
    stock = None
    inDB = False

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

    if request.POST.get('unitnum') != '' :
        addressArgs['unitNum'] = request.POST.get('unitnum')

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

def create_agent(request, type) :
    agent = None
    if request.POST.get('agent') == '' :
        return None
    try :
        if type == 'firm' :
            agent = Agent.objects.get(firmName=request.POST.get('agent'))
        elif type == 'person' :
            agent = Agent.objects.get(name=request.POST.get('agent'))
    except :
        if agent is None :
            if type == 'firm' :
                agent = Agent(firmName=request.POST.get('agent'))
            elif type == 'person' :
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
