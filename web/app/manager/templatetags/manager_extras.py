# -*- coding: utf8 -*-
from django import template
from manager.models import Group
import json

register = template.Library()
@register.simple_tag(name='manager_groups')
def manager_options(manager):
    """ Рендерит массив с номерами групп пользователя """
    gids = [group.gid for group in Group.objects.filter(manager=manager)]
    return json.dumps(gids)
