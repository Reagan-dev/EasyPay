from django.contrib import admin
from .models import Business, BusinessTerminal

class BusinessTerminalInline(admin.TabularInline):
    """Allows managing multiple devices per canteen serving point"""
    model = BusinessTerminal
    extra = 1
    readonly_fields = ('created_at',)

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    # 1. Dashboard view for quick verification
    list_display = (
        'name', 
        'user_email', 
        'mpesa_till_number', 
        'category_code', 
        'is_active', 
        'terminal_count'
    )
    
    # 2. Filters to find active vs inactive canteens
    list_filter = ('is_active', 'category_code', 'created_at')
    
    # 3. Search by Name or Till Number (essential for support)
    search_fields = ('name', 'mpesa_till_number', 'user__email', 'user__phone')
    
    # 4. Inlines: Manage terminals without leaving the page
    inlines = [BusinessTerminalInline]

    # Custom helper methods for the list view
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "Owner Email"

    def terminal_count(self, obj):
        return obj.terminals.count()
    terminal_count.short_description = "Active Terminals"

@admin.register(BusinessTerminal)
class BusinessTerminalAdmin(admin.ModelAdmin):
    list_display = ('device_id', 'business', 'location', 'is_online', 'created_at')
    list_filter = ('is_online', 'business')
    search_fields = ('device_id', 'location', 'business__name')
