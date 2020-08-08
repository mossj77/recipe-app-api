from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,\
                                       PermissionsMixin

from django.conf import settings


class UserManager(BaseUserManager):
    """ our custom user manager class. """

    def create_user(self, email, password, **extra_fields):
        """ create and save new custom users. """
        if not email:
            raise ValueError("Users most have a email address. ")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password):
        """ create and save a super user. """
        if not email:
            raise ValueError("Users most have a email address. ")

        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """ our custom user model that use email to username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Tag(models.Model):
    """ tag of recipe """
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name
