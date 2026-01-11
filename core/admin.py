from django.contrib import admin
from .models import RfidCard, EntryLog, CardHolder


@admin.register(CardHolder)
class CardHolderAdmin(admin.ModelAdmin): 
    list_display = ('uid', 'full_name')
    search_fields = ('uid', 'full_name')

@admin.register(RfidCard)
class RfidCardAdmin(admin.ModelAdmin):
    list_display = ('uid', 'expiry_date', 'user', 'valid', 'is_valid_display')
    list_filter = ('valid', 'expiry_date')
    search_fields = ('uid',)

    @admin.display(boolean=True, description='Czy ważna?')
    def is_valid_display(self, obj):
        return obj.is_valid()

@admin.register(EntryLog)
class EntryLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'uid_raw', 'status', 'card')
    list_filter = ('status', 'timestamp')
    search_fields = ('uid_raw',)
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False