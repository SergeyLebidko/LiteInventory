import uuid
from django.db.models import Q
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status

from main.forms import username_checker

from .models import Token
from .authentication import CustomTokenAuthentication


@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if not user:
        return Response(status=status.HTTP_403_FORBIDDEN)

    token = Token.objects.create(user=user, token=str(uuid.uuid4()))
    return Response({'token': token.token}, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([CustomTokenAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    Token.objects.get(token=request.auth).delete()
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def register(request):
    username = request.data.get('username') or ''
    password = request.data.get('password') or ''
    email = request.data.get('email') or ''
    first_name = request.data.get('first_name') or ''
    last_name = request.data.get('last_name') or ''
    try:
        username_checker(username)
    except ValidationError as ex:
        return Response({'detail': ex.message}, status=status.HTTP_400_BAD_REQUEST)

    try:
        validate_password(password)
    except ValidationError as ex:
        return Response({'detail': ' '.join(ex.messages)}, status=status.HTTP_400_BAD_REQUEST)

    try:
        EmailValidator('Некорректный email')(email)
    except ValidationError as ex:
        return Response({'detail': ex.message}, status=status.HTTP_400_BAD_REQUEST)

    user_exists = User.objects.filter(Q(username=username) | Q(email=email)).exists()
    if user_exists:
        return Response(
            {'detail': 'Пользователь с таким логином или email уже существует'},
            status=status.HTTP_400_BAD_REQUEST
        )

    User.objects.create_user(username, password=password, email=email, first_name=first_name, last_name=last_name)

    return Response(status=status.HTTP_201_CREATED)
