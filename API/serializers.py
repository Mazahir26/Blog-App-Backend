from rest_framework import serializers
from rest_framework.fields import ReadOnlyField
from .models import Notification_Id, Analytics_event, Notification

class Notification_IdSerializer(serializers.ModelSerializer):
    class Meta:
         model = Notification_Id
         fields = ["id","key"]

class analytics_eventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analytics_event
        fields = ["name", "time"]
        # read_only_field = ['time', 'id']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["title", "time"]
        # read_only_field = ['time', 'id']