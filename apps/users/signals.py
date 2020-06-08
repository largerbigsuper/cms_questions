from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import User, mm_User

@receiver(post_save, sender=User)
def user_post_save(instance, raw, created, using, update_fields, **kwargs):
    """用户保存后操作
    """
    if created:
        pass
