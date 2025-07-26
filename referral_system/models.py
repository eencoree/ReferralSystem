from datetime import timedelta

from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from rest_framework import exceptions
from django.db import models
import random
import string


def generate_invite_code(max_length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=max_length))


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, **extra_fields):
        if not phone_number:
            raise exceptions.AuthenticationFailed('There is no phone number')

        invite_code = generate_invite_code()
        while User.objects.filter(invite_code=invite_code).exists():
            invite_code = generate_invite_code()

        user = self.model(phone_number=phone_number, invite_code=invite_code, **extra_fields)
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=15, unique=True)
    invite_code = models.CharField(max_length=6, unique=True, blank=False, null=False)
    activated_code = models.CharField(max_length=6, blank=True, null=True)

    USERNAME_FIELD = 'phone_number'

    objects = CustomUserManager()

    def __str__(self):
        return self.phone_number


class UserPhoneCode(models.Model):
    phone_number = models.CharField(max_length=15)
    code = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(hours=1)

    @staticmethod
    def generate_4xcode():
        return str(random.randint(1000, 9999))
