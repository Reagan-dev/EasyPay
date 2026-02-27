from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserRole

class UserRoleInline(admin.TabularInline):
    """Allows managing user roles directly on the User edit page"""
    model = UserRole
    extra = 1

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # 1. Define how users are listed in the admin index
    list_display = ('email', 'first_name', 'last_name', 'phone', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email', 'phone', 'first_name', 'last_name')
    ordering = ('email',)
    
    # 2. Add the Inline roles so you don't have to go to a different page to assign roles
    inlines = [UserRoleInline]

    # 3. Fieldsets: Organizes the User detail page
    # We must redefine these because we are using a custom model
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

    # 4. Add fields for the "Create User" form in Admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone', 'password'),
        }),
    )

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
    search_fields = ('user__email', 'user__phone')
