from django.contrib import admin
from .models import Analytics_event, Notification_Id, Notification
# Register your models here.

admin.site.register(Analytics_event)
admin.site.register(Notification_Id)
admin.site.register(Notification)

