from django.contrib.auth.models import PermissionsMixin, User
from django.db import models


class User(User, PermissionsMixin):
    def __str__(self):
        return f"@{self.username}"
