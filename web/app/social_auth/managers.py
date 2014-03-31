# -*- coding: utf8 -*-

from django.db import models
from django.contrib.auth.models import User

class SocialAuthManager(models.Manager):

    def create_user(self, uid, network, *args, **kwargs):
        """ Создать пользователя """

        user = User.objects.create_user(username='%s_%s'  % (network, uid), *args, **kwargs)
        return self.create(user_ptr=user, uid=uid, network=network)
