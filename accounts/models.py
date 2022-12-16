from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class Account(AbstractUser):
    country = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255, unique=True)
    country = models.CharField(max_length=255)
    referral_code = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.email
