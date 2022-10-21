from django.utils.timezone import now
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# super entity to stock, property, bond, and miscasset
class Asset(models.Model):
    assetName = models.CharField(max_length=255, null=False)

# subentity to asset for a stock
class Stock(models.Model):
    ticker = models.CharField(max_length=6, null=False, unique=True)
    yearHigh = models.DecimalField(max_digits=9, decimal_places=2, null=True)
    yearLow = models.DecimalField(max_digits=9, decimal_places=2, null=True)
    FK_asset_stock = models.ForeignKey(Asset, on_delete=models.CASCADE,  null=False, primary_key=True)

# weak entity for stock that is used to keep track of daily stock data
class StockSnapshot(models.Model):
    snapshotDate = models.DateField(null=False, default=now)
    openPrice = models.DecimalField(max_digits=9, decimal_places=2, null=False)
    closePrice = models.DecimalField(max_digits=9, decimal_places=2, null=False)
    volume = models.BigIntegerField(null=False)
    FK_stock_snapshot = models.ForeignKey(Stock, on_delete= models.CASCADE,  null=False)

# entity for an address
class Address(models.Model):
    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(zipCode__lte=100000), name='zipCode_lte_100000'),
            models.UniqueConstraint(fields=['street', 'city', 'state', 'zipCode', 'unitNum'], name='uniqueAddress'),
        ]
    street = models.CharField(max_length=255, null=False)
    zipCode = models.IntegerField()
    state = models.CharField(max_length=2, null=False)
    city = models.CharField(max_length=255, null=False)
    unitNum = models.IntegerField(null=True)

# subentity to asset for a house, office, or building
class Property(models.Model):
    totalfee = models.DecimalField(max_digits=11, decimal_places=2, null=False)
    FK_address_property = models.ForeignKey(Address, on_delete= models.CASCADE,  null=False, unique=True)
    FK_asset_property = models.ForeignKey(Asset, on_delete= models.CASCADE,  null=False, primary_key=True)

# subentity to asset for a bond
class Bond(models.Model):
    maturityDate = models.DateField(null=False)
    interestRate = models.DecimalField(max_digits=5, decimal_places=3, null=False)
    faceValue = models.DecimalField(max_digits=11, decimal_places=2, null=False)
    issuer = models.CharField(max_length=255, null=False)
    rating = models.CharField(max_length=4)
    FK_asset_bond = models.ForeignKey(Asset, on_delete= models.CASCADE,  null=False, primary_key=True)

# subentity to asset to hold all misc assets like furniture, cars, computers, machinery, etc
class MiscAsset(models.Model):
    description = models.CharField(max_length=255)
    FK_asset_misc = models.ForeignKey(Asset, on_delete= models.CASCADE,  null=False, primary_key=True)

# entity to desribe a realestate agent or broker
class Agent(models.Model):
    name = models.CharField(max_length=255, null=True)
    firmName = models.CharField(max_length=255)
    FK_address_agent = models.ForeignKey(Address, on_delete= models.CASCADE,  null=False, unique=True)

# entity to hold all fees for an agent
class AgentFee(models.Model):
    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(feeType='F') | models.Q(feeType='R'), name='feeConstraint'),
        ]
    feeType = models.CharField(max_length=1, null=False)   # F for flat R for rate
    feeRate = models.DecimalField(max_digits=5, decimal_places=3)
    feeFlat = models.DecimalField(max_digits=9, decimal_places=2)
    feeDescription = models.CharField(max_length=255)
    FK_agent_fee = models.ForeignKey(Agent, on_delete=models.CASCADE,  null=False)

# entity to keep a record of a trade of an asset
class Trade(models.Model):
    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(action='B') | models.Q(action='S'), name='actionConstraint'),
        ]
    action = models.CharField(max_length=1, null=False)
    tradeDate = models.DateField(null=False, default=now)
    pricePerAsset = models.DecimalField(max_digits=13, decimal_places=2, null=False, default=1)
    assetQuantity = models.FloatField(null=False, default=1.0)
    FK_asset_trade = models.ForeignKey(Asset, on_delete= models.CASCADE,  null=False)
    FK_agent_trade = models.ForeignKey(Agent, on_delete= models.CASCADE)

# entity used to show current assets the user is holding
# upon "selling" the asset, the row is deleted so will no longer display under current holdings
class CurrentHoldings(models.Model):
    FK_trade = models.ForeignKey(Trade, on_delete=models.CASCADE,  null=False, primary_key=True)

# implements m-n relationship between trade and user
class UserTrade(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['FK_user', 'FK_trade'], name='uniqueUserTrade'),
        ]
    FK_user = models.ForeignKey(User, on_delete= models.CASCADE,  null=False)
    FK_trade = models.ForeignKey(Trade, on_delete= models.CASCADE,  null=False)

# subentity to user for users that sign up for the asset management
# has more personal information
class FintechUser(models.Model):
    age = models.SmallIntegerField(null=False)
    sex = models.CharField(max_length=1, null=False)
    occupation = models.CharField(max_length=255, null=False)
    FK_address_assetUser = models.ForeignKey(Address, on_delete= models.CASCADE)
    FK_user_assetUser = models.ForeignKey(User, on_delete= models.CASCADE,  null=False, primary_key=True)
