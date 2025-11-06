from django.contrib import admin
from .models import Location

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('get_user', 'latitude', 'longitude', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('device__user__email',)

    def get_user(self, obj):
        return obj.device.user
    get_user.short_description = 'User'
    readonly_fields = ('timestamp',)