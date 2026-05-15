from django.db.models.signals import post_save
from django.contrib.auth.models import User
from commerce.models import Customer
from django.dispatch import receiver
from django.conf import settings



@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_customer_profile(sender, **kwargs):
    if kwargs['created']:
        Customer.objects.create(user=kwargs['instance'])



