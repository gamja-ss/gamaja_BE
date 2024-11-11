from django.db import models
from users.models import User


class Stack(models.Model):
    name = models.CharField(max_length=255, null=False)

    def __str__(self):
        return self.name


class UserStack(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_stacks")
    stack = models.ForeignKey(
        Stack, on_delete=models.CASCADE, related_name="stack_users"
    )

    def __str__(self):
        return f"{self.user.username} - {self.stack.name}"
