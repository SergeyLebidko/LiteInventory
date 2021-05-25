import uuid
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status

from main.utils import send_password_reset_code, create_default_equipment_types, get_stat, check_username
from main.models import ResetPasswordCode, Group, EquipmentCard, EquipmentType, EquipmentFeature
from .models import Token
from .authentication import CustomTokenAuthentication
from .utils import check_password, check_email
from .serializers import GroupSerializer, EquipmentCardSerializer, EquipmentTypeSerializer, EquipmentFeatureSerializer


@api_view(['GET'])
@authentication_classes([CustomTokenAuthentication])
@permission_classes([IsAuthenticated])
def account_data(request):
    user = request.user
    return Response({
        'username': user.username,
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
    username = request.data.get('username', '')
    password = request.data.get('password', '')
    email = request.data.get('email', '')
    first_name = request.data.get('first_name', '')
    last_name = request.data.get('last_name', '')

    error = check_username(username) or check_password(password) or check_email(email)
    if error:
        return Response({'detail': error}, status=status.HTTP_400_BAD_REQUEST)
    user_exist = User.objects.filter(Q(username=username) | Q(email=email))
    if user_exist:
        return Response(
            {
                'detail': 'Пользователь с таким логином или email уже существует'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.create_user(
        username,
        password=password,
        email=email,
        first_name=first_name,
        last_name=last_name
    )
    create_default_equipment_types(user)

    return Response(status=status.HTTP_201_CREATED)


@api_view(['PATCH'])
@authentication_classes([CustomTokenAuthentication])
@permission_classes([IsAuthenticated])
def edit_account(request):
    user = request.user
    if user.is_superuser or user.is_staff:
        return Response(
            {'detail': 'Редактирование аккаунтов персонала производится через административную панель Django'},
            status=status.HTTP_403_FORBIDDEN
        )

    username = request.data.get('username')
    email = request.data.get('email')

    if username is not None or email is None:
        error = None
        if email:
            error = check_email(email)
        if username:
            error = check_username(username)
        user_exist = User.objects.filter((Q(username=username) | Q(email=email)) & ~Q(pk=user.pk)).exists()
        if user_exist:
            error = 'Пользователь с таким логином или email уже существует'
        if error:
            return Response({'detail': error}, status=status.HTTP_400_BAD_REQUEST)

        user.username = username or user.username
        user.email = email or user.email

    if 'first_name' in request.data:
        user.first_name = request.data.get('first_name')
    if 'last_name' in request.data:
        user.last_name = request.data.get('last_name')

    user.save()

    return Response(status=status.HTTP_200_OK)


@api_view(['DELETE'])
@authentication_classes([CustomTokenAuthentication])
@permission_classes([IsAuthenticated])
def remove_account(request):
    user = request.user
    if user.is_superuser or user.is_staff:
        return Response(
            {'detail': 'Удаление аккаунтов персонала производится через административную панель Django'},
            status=status.HTTP_403_FORBIDDEN
        )

    password = request.data.get('password')
    if user.check_password(password):
        user.delete()
        return Response(status=status.HTTP_200_OK)

    return Response({'detail': 'Некорректный пароль'}, status=status.HTTP_403_FORBIDDEN)


@api_view(['POST'])
@authentication_classes([CustomTokenAuthentication])
@permission_classes([IsAuthenticated])
def change_password(request):
    password = request.data.get('password')
    next_password = request.data.get('next_password', '')
    user = request.user

    if user.is_superuser or user.is_staff:
        return Response(
            {'detail': 'Смена аккаунтов персонала производится через административную панель Django'},
            status=status.HTTP_403_FORBIDDEN
        )

    if not user.check_password(password):
        return Response({'detail': 'Неверный текущий пароль'}, status=status.HTTP_403_FORBIDDEN)

    error = check_password(next_password)
    if error:
        return Response({'detail': error}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(next_password)
    user.save()

    # При смене пароля удаляем токен, с которым была выполнена смена
    token = request.auth
    Token.objects.get(token=token).delete()

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


@api_view(['POST'])
def reset_password_confirm(request, _uuid):
    try:
        reset_password_code = ResetPasswordCode.objects.get(uuid=_uuid)
    except ResetPasswordCode.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    code = request.data.get('code')
    if code != reset_password_code.code:
        return Response({'detail': 'Неверный код сброса пароля'}, status=status.HTTP_403_FORBIDDEN)

    password = request.data.get('password')
    error = check_password(password)
    if error:
        return Response({'detail': error}, status=status.HTTP_400_BAD_REQUEST)

    user = reset_password_code.user
    user.set_password(password)
    user.save()

    return Response(status=status.HTTP_200_OK)


class GroupViwSet(ModelViewSet):
    serializer_class = GroupSerializer
    authentication_classes = [SessionAuthentication, CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        user = self.request.user
        queryset = Group.objects.filter(user=user)
        return queryset


class EquipmentCardViewSet(ModelViewSet):
    serializer_class = EquipmentCardSerializer
    authentication_classes = [SessionAuthentication, CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = EquipmentCard.objects.all()
        group = self.request.query_params.get('group')
        if group:
            queryset = queryset.filter(group=group)
        return queryset


class EquipmentTypeViewSet(ModelViewSet):
    serializer_class = EquipmentTypeSerializer
    authentication_classes = [SessionAuthentication, CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        user = self.request.user
        queryset = EquipmentType.objects.filter(user=user)
        return queryset


class EquipmentFeatureViewSet(ModelViewSet):
    serializer_class = EquipmentFeatureSerializer
    authentication_classes = [SessionAuthentication, CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = EquipmentFeature.objects.all()
        card_id = self.request.query_params.get('card')
        if card_id:
            queryset = queryset.filter(equipment_card=card_id)
        return queryset


@api_view(['GET'])
@authentication_classes([SessionAuthentication, CustomTokenAuthentication])
@permission_classes([IsAuthenticated])
def stat(request):
    user = request.user
    result = get_stat(user)
    return Response(result, status=status.HTTP_200_OK)
