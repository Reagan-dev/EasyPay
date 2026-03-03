from django.contrib import admin
from .models import Customer, CustomerStudent

class CustomerStudentInline(admin.TabularInline):
    """Allows adding/removing children directly on the Customer page"""
    model = CustomerStudent
    extra = 1  # Number of empty slots to show for new students
    autocomplete_fields = ['student'] # Makes it easy to search through many students

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'user_phone', 'child_count', 'created_at')
    search_fields = ('user__email', 'user__phone', 'user__first_name')
    inlines = [CustomerStudentInline]

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'

    def user_phone(self, obj):
        return obj.user.phone
    user_phone.short_description = 'Phone'

    def child_count(self, obj):
        return obj.customer_students.count()
    child_count.short_description = 'Children Linked'

@admin.register(CustomerStudent)
class CustomerStudentAdmin(admin.ModelAdmin):
    list_display = ('customer', 'student', 'can_view_transactions', 'can_topup')
    list_filter = ('can_view_transactions', 'can_topup')
    search_fields = ('customer__user__email', 'student__reg_no')