from django.contrib import admin
from django.conf import settings

from .models import *

# Register your models here.
admin.site.register(DiscussionTopic)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Document)

if settings.DEBUG == True :
    admin.site.register(Board)