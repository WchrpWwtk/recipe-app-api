"""
Database models.
"""

from django.contrib.auth.models import (
    PermissionsMixin,
    BaseUserManager,
    AbstractBaseUser,
)
from django.db import models

import os
import uuid


def recipe_image_file_path(instance, filename):
    """
    Generate a file path for new recipe image.
    :param instance:
    :param filename:
    :return:
    """
    ext = os.path.splitext(filename)[1]
    filename = f"{uuid.uuid4()}{ext}"

    return os.path.join("uploads", "recipe", filename)


class UserManager(BaseUserManager):
    """
    Manager for users.
    """

    def create_user(self, email: str, password: str = None, **extra_fields):
        """
        Create, save and return a new user.
        :param email:
        :param password:
        :param extra_fields:
        :return:
        """
        if not email:
            raise ValueError("User must have an email address.")

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email: str, password: str):
        """
        Create and return a new superuser.
        :param email:
        :param password:
        :return:
        """
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    User in the system.
    """

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
