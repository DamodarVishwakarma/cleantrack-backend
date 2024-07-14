from django.contrib import admin
from disposal_agency.models import DisposalEntries


class DisposalEntriesAdmin(admin.ModelAdmin):
    list_display = ('consignment', 'collected_by', 'company', 'city', 'vehicle_number', 'weight', 'disposal_status')
    list_display_links = ('consignment', 'collected_by')
    list_filter = ('consignment', 'disposal_status', 'company')
    search_fields = ('consignment__consignment_id', 'company__name')


admin.site.register(DisposalEntries, DisposalEntriesAdmin)
