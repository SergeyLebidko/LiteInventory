import uuid
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import send_mail
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status

from main.utils import send_password_reset_code
from .models import Token
from .authentication import CustomTokenAuthentication
from .utils import extract_user_data_from_request, check_user_data


@api_view(['GET'])
@authentication_classes([CustomTokenAuthentication])
@permission_classes([IsAuthenticated])
def account_data(request):
    user = request.user
    return Response({
        'login': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name
    }, status=status.HTTP_200_OK)


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
    username, password, email, first_name, last_name = extract_user_data_from_request(request)

    error = check_user_data(username=username, password=password, email=email)
    if error:
        return Response({'detail': error}, status=status.HTTP_400_BAD_REQUEST)

    User.objects.create_user(username, password=password, email=email, first_name=first_name, last_name=last_name)

    return Response(status=status.HTTP_201_CREATED)


@api_view(['POST'])
@authentication_classes([CustomTokenAuthentication])
@permission_classes([IsAuthenticated])
def edit_account(request):
    username, _, email, first_name, last_name = extract_user_data_from_request(request)

    error = check_user_data(username=username, email=email)
    if error:
        return Response({'detail': error}, status=status.HTTP_400_BAD_REQUEST)

    user = request.user
    user.username = username
    user.email = email
    user.first_name = first_name
    user.last_name = last_name
    user.save()

    return Response(status=status.HTTP_200_OK)


@api_view(['DELETE'])
@authentication_classes([CustomTokenAuthentication])
@permission_classes([IsAuthenticated])
def remove_account(request):
    password = request.data.get('password')
    user = request.user
    if user.check_password(password):
        user.delete()
        return Response(status=status.HTTP_200_OK)

    return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['POST'])
@authentication_classes([CustomTokenAuthentication])
@permission_classes([IsAuthenticated])
def change_password(request):
    password = request.data.get('password')
    next_password = request.data.get('next_password', '')
    user = request.user

    if not user.check_password(password):
        return Response(status=status.HTTP_403_FORBIDDEN)

    error = check_user_data(password=next_password)
    if error:
        return Response({'detail': error}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(next_password)
    user.save()

    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def reset_password(request):
    email = request.data.get('email')
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'detail': 'Пользователь с таким email не обнаружен'}, status=status.HTTP_400_BAD_REQUEST)

    _uuid = send_password_reset_code(user)
    return Response({'uuid': _uuid}, status=status.HTTP_200_OK)
