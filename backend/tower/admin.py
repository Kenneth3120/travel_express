from django.contrib import admin
from .models import TowerConfig

@admin.register(TowerConfig)
class TowerConfigAdmin(admin.ModelAdmin):
    list_display = ('base_url', 'username')