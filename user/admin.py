from django.contrib import admin
from user.models import User,Otp

from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedDropdownFilter

# admin.site.site_header = 'Digital Platform Admin Panel'


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'phone','company', 'user_type')
    list_display_links = ('email',)
    list_filter = (
        ('company', RelatedDropdownFilter),
        ('user_type', DropdownFilter),
    )


admin.site.register(User, UserAdmin)
admin.site.register(Otp)
