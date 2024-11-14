from django.contrib import admin

from .models import Stack, UserStack

admin.site.register(Stack)
admin.site.register(UserStack)
