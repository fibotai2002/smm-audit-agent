from django.contrib import admin
from .models import User, Audit

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'full_name', 'username', 'tier', 'subscription_expires_at', 'created_at')
    list_filter = ('tier', 'created_at')
    search_fields = ('telegram_id', 'username', 'full_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Personal Info', {
            'fields': ('telegram_id', 'username', 'full_name')
        }),
        ('Subscription', {
            'fields': ('tier', 'subscription_expires_at')
        }),
    )

@admin.register(Audit)
class AuditAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'audit_type', 'status', 'created_at')
    list_filter = ('status', 'audit_type', 'created_at')
    search_fields = ('user__username', 'user__full_name', 'instagram_url', 'telegram_url')
    readonly_fields = ('id', 'created_at', 'collected_data_json', 'report_json')
