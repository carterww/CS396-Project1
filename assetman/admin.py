from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Asset)
admin.site.register(Stock)
admin.site.register(Property)
admin.site.register(Address)
admin.site.register(Bond)
admin.site.register(MiscAsset)
admin.site.register(StockSnapshot)
admin.site.register(Agent)
admin.site.register(AgentFee)
admin.site.register(Trade)
admin.site.register(CurrentHoldings)
admin.site.register(UserTrade)
admin.site.register(FintechUser)

