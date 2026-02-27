from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    # 1. Clear identification in the list view
    list_display = ('reg_no', 'get_full_name', 'get_phone', 'created_at')
    
    # 2. Search by registration number or user details
    # Note: Using 'user__email' allows searching through the related User model
    search_fields = ('reg_no', 'user__first_name', 'user__last_name', 'user__phone', 'user__email')
    
    # 3. Filter by enrollment date
    list_filter = ('created_at',)
    
    # 4. Read-only fields
    readonly_fields = ('id', 'created_at')

    # --- Custom Display Methods ---

    @admin.display(description='Full Name')
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    @admin.display(description='Phone Number')
    def get_phone(self, obj):
        return obj.user.phone

    # --- Configuration ---
    
    # This is important for the QRToken autocomplete we set up earlier!
    # It allows other admin pages to search for students efficiently.
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        return queryset, use_distinct