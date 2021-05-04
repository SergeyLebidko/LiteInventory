from rest_framework.authentication import BaseAuthentication

from .models import Token


class CustomTokenAuthentication(BaseAuthentication):

    def authenticate(self, request):
        request_token = request.META.get('HTTP_AUTHORIZATION')
        base_token = Token.objects.filter(token=request_token)
        if base_token:
            return base_token[0].user, base_token[0].token
        return None
