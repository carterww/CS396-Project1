from .models import Stock, Trade, StockSnapshot

class StockTrade :
    def __init__(self, stock, trade):
        self.Stock = stock
        self.Trade = trade
        self.gain = calculateGain(stock, trade)

class PropertyTrade :
    def __init__(self, property, trade):
        self.Property = property
        self.Trade = trade

class BondTrade :
    def __init__(self, bond, trade):
        self.Bond = bond
        self.Trade = trade

class MiscTrade :
    def __init__(self, misc, trade):
        self.Misc = misc
        self.Trade = trade


def calculateGain(stock, trade):
    snapshot = StockSnapshot.objects.filter(FK_stock_snapshot=stock).last()
    if snapshot is not None:
        latestPrice = snapshot.closePrice
        purchasePrice = trade.pricePerAsset
        return round((latestPrice - purchasePrice) / purchasePrice * 100, 2)
    else :
        return "Error"
