from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = 'customer', 'Customer'
        AGENT = 'agent', 'Agent'
        ADMIN = 'admin', 'Admin'

    role = models.CharField(max_length=20, choices=Role, default=Role.CUSTOMER)

    @property
    def is_agent(self):
        return self.role in (self.Role.AGENT, self.Role.ADMIN)

    def __str__(self):
        return f"{self.username} ({self.role})"
