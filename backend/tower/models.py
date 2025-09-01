from django.db import models
from fernet_fields import EncryptedTextField
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now


class TowerConfig(models.Model):
    """Stores Ansible Tower connection details. Only the first record is used by the proxy view."""
    base_url = models.URLField(default='https://ansible-tower.dev.echonet/')
    username = models.CharField(max_length=128)
    password = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.base_url} ({self.username})"


class Auditlog(models.Model):
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('deleted', 'Deleted'),
    ]

    user = models.CharField(max_length=100)
    action = models.CharField(max_length=100, choices=ACTION_CHOICES)
    object_type = models.CharField(max_length=100)
    object_repr = models.CharField(max_length=255, blank=True)
    object_id = models.IntegerField()
    timestamp = models.DateTimeField(default=now)
    changes = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.timestamp} {self.user} {self.action} {self.object_type} ({self.object_id})"


class TowerInstance(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField()
    username = models.CharField(max_length=100, blank=True)
    password = EncryptedTextField(blank=True, null=True)
    region = models.CharField(max_length=50, blank=True)
    environment = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, default='active')

    def __str__(self):
        return f"{self.name} ({self.region} - {self.environment})"


class Credential(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    tower_instance = models.ForeignKey(
        TowerInstance,
        on_delete=models.CASCADE,
        related_name="credentials"
    )

    def __str__(self):
        return f"{self.name} ({self.type})"


class ExecutionEnvironment(models.Model):
    name = models.CharField(max_length=100)
    image = models.URLField()
    description = models.TextField(blank=True)
    tower_instance = models.ForeignKey(
        TowerInstance,
        on_delete=models.CASCADE,
        related_name="environments"
    )

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('member', 'Member'),
        ('viewer', 'Viewer'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='viewer')

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
