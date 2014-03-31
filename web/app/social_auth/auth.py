# -*- coding: utf8 -*-

from django.contrib.auth.models import User
from social_auth.models import Manager

class SocialAuthBackend:
    """
    Авторизация через социальный аккаунт
    """

    def authenticate(self, uid=None, network=None):
        """
        Авторизуем
        """

        try:
            user = Manager.objects.get(uid=uid, network=network)
        except Manager.DoesNotExist:
            user = Manager.objects.create(username = '%s_%s' % (network, uid), network=network, uid=uid)
            user.is_staff = False
            user.is_superuser = False
            user.save()

        return user

    def get_user(self, username):
        try:
            return Manager.objects.get(pk=username)
        except User.DoesNotExist:
            return None


        

