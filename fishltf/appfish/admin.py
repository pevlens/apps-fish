from django.contrib import admin
from .models import *
# Register your models here.




@admin.register(Fish)
class FishAdmin(admin.ModelAdmin):
    pass

@admin.register(Method)
class MethodAdmin(admin.ModelAdmin):
    pass

@admin.register(Gear)
class GearAdmin(admin.ModelAdmin):
    pass

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass

@admin.register(Catch)
class CatchAdmin(admin.ModelAdmin):
    pass

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    pass