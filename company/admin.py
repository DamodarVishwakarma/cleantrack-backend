from django.contrib import admin
from django_admin_listfilter_dropdown.filters import DropdownFilter, ChoiceDropdownFilter

from company.models import Company


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'company_type', 'city', 'state', 'zip_code', 'company_type', 'company_status')
    fields = ('id','name', 'street', 'city', 'state', 'zip_code', 'company_type', 'company_status')
    list_filter = (
        ('name', DropdownFilter),
        ('company_type', ChoiceDropdownFilter),
        ('company_status', DropdownFilter)
    )
    search_fields = ('name', 'company_type', 'city', 'state', 'status')


admin.site.register(Company, CompanyAdmin)
