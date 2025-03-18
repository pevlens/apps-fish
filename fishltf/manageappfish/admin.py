from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(UserTg)
class UserTgAdmin(admin.ModelAdmin):
    pass

@admin.register(CacthTg)
class CacthTgAdmin(admin.ModelAdmin):
    pass

@admin.register(TelegramMessage)
class TelegramMessageAdmin(admin.ModelAdmin):
    pass


@admin.register(CacthTgImage)
class CacthTgImageAdmin(admin.ModelAdmin):
    pass
