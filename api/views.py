import uuid
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status

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
