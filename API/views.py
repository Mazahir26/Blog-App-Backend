from .models import Notification_Id, Analytics_event, Notification
from rest_framework import generics, permissions
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.http import JsonResponse
from django.db import IntegrityError
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import Notification_IdSerializer, analytics_eventSerializer, NotificationSerializer
from datetime import date, timedelta
# Expo Notifications stuff

from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushServerError,
    PushTicketError,
)
from requests.exceptions import ConnectionError, HTTPError

def send_push_message(token, message, extra=None):
    try:
        response = PushClient().publish(
            PushMessage(to=token,
                        body=message,
                        data=extra))
    except PushServerError as exc:
        # Encountered some likely formatting/validation error.
        rollbar.report_exc_info(
            extra_data={
                'token': token,
                'message': message,
                'extra': extra,
                'errors': exc.errors,
                'response_data': exc.response_data,
            })
        raise
    except (ConnectionError, HTTPError) as exc:
        # Encountered some Connection or HTTP error - retry a few times in
        # case it is transient.
        rollbar.report_exc_info(
            extra_data={'token': token, 'message': message, 'extra': extra})
        raise self.retry(exc=exc)

    try:
        # We got a response back, but we don't know whether it's an error yet.
        # This call raises errors so we can handle them with normal exception
        # flows.
        response.validate_response()
    except DeviceNotRegisteredError:
        # Mark the push token as inactive
        from notifications.models import PushToken
        PushToken.objects.filter(token=token).update(active=False)
    except PushTicketError as exc:
        # Encountered some other per-notification error.
        rollbar.report_exc_info(
            extra_data={
                'token': token,
                'message': message,
                'extra': extra,
                'push_response': exc.push_response._asdict(),
            })
        raise self.retry(exc=exc)

# End of Expo Push notifications stuff

class Notifications(generics.CreateAPIView):
    serializer_class = Notification_IdSerializer
    permission_classes = [permissions.IsAuthenticated]
    def perform_create(self, serializer):
        obj = serializer.save()


class Call_Notifications(generics.CreateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        for e in Notification_Id.objects.all():
            send_push_message(e.key, self.request.data["title"])
        serializer.save()

class Analytics(generics.ListCreateAPIView):
    serializer_class = analytics_eventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        ok = self.kwargs.get('date')
        type = self.kwargs.get('type')
        if(not type):
            type = "login"
        today = date.today()
        if(ok == 1):
            return Analytics_event.objects.filter(time__day = today.day, name=type)
        elif(ok == 2):
            return Analytics_event.objects.filter(time__month = today.month, name=type)
        else :
            return Analytics_event.objects.all()


    def perform_create(self, serializer):
        obj = serializer.save()


@csrf_exempt
def signup(request):
    if request.method == 'POST':
        try:
            data = JSONParser().parse(request)
            user = User.objects.create_user(data['username'], password=data['password'], email = data['email'])
            user.save()
            token = Token.objects.create(user=user)
            return JsonResponse({'token':str(token)}, status=201)
        except IntegrityError:
            return JsonResponse({'error':'That username has already been taken. Please choose a new username'}, status=400)
    else:
        return JsonResponse({'Error': 'No Get '}, status=400)

@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        user = authenticate(request, username=data['username'], password=data['password'], email = data['email'])
        if user is None:
            return JsonResponse({'error':'Could not login. Please check username and password'}, status=400)
        else:
            try:
                token = Token.objects.get(user=user)
            except:
                token = Token.objects.create(user=user)
            return JsonResponse({'token':str(token)}, status=200)
    else:
        return JsonResponse({'Error': 'No Get'}, status=400)
