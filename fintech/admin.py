from django.contrib import admin
from django.conf import settings

from .models import *

# Register models so ./admin/ can edit and delete them
admin.site.register(DiscussionTopic)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(DocumentFile)

if settings.DEBUG == True :
    admin.site.register(Board)