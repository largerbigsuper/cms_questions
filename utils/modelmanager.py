import logging

from django.db.models.manager import Manager
from django.core.cache import cache
from django.db.models import F

class CacheKey:
    pass

class StatsUtils:

    def _update_stats(self, pk, field_name, amount=1):
        if amount > 0:
            value = F(field_name) + amount
        else:
            value = F(field_name) - abs(amount)
        updates = {
            field_name: value
        }
        self.filter(pk=pk).update(**updates)
    
    def increase(self, pk, field_name, amount=1):
        return self._update_stats(pk, field_name, amount)

    def decrease(self, pk, field_name, amount=1):
        amount = ~amount + 1
        return self._update_stats(pk, field_name, amount)


class ModelManager(Manager, CacheKey, StatsUtils):
    cache = cache

    logger = logging.getLogger('model')
