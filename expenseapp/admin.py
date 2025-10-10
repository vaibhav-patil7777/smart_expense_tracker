from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Expense, Budget

# ✅ Custom admin for CustomUser
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'phone', 'is_admin', 'is_approved', 'is_blocked', 'is_staff', 'is_superuser')
    list_filter = ('is_admin', 'is_approved', 'is_blocked', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    ordering = ('username',)
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone', 'is_approved', 'is_admin', 'is_blocked')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('phone', 'is_approved', 'is_admin', 'is_blocked')}),
    )

# ✅ Basic BudgetAdmin (remove broken fields)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('id', 'amount')  # only existing fields
    search_fields = ('id',)
    ordering = ('id',)

# ✅ Register models
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Expense)
admin.site.register(Budget, BudgetAdmin)
