from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['POST'])
def login(request):
    print(request.data)
    print(request.META['HTTP_AUTHORIZATION'])
    return Response('Все хорошо', status=status.HTTP_200_OK)
