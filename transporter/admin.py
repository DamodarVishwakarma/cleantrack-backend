from django.contrib import admin
from django_admin_listfilter_dropdown.filters import DropdownFilter, ChoiceDropdownFilter

from transporter.models import Order, Consignment, CollectionEntries, Remark, CollectionRevision


class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'collection_agency', 'disposal_agency', 'customer')
    fields = ('order_number', 'collection_agency', 'disposal_agency', 'customer')
    search_fields = ('order_number', 'collection_agency', 'disposal_agency', 'customer')


class ConsignmentAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'consignment_id', 'vehicle_number')
    fields = ('order_number', 'consignment_id', 'vehicle_number')
    list_display_links = ('order_number', 'consignment_id')
    list_filter = (
        ('order_number', ChoiceDropdownFilter),
        ('consignment_id', DropdownFilter),
        ('vehicle_number', DropdownFilter)
    )
    search_fields = ('consignment_id',)


class CollectionEntriesAdmin(admin.ModelAdmin):
    list_display = ('consignment', 'company', 'collected_by', 'dispatch_date', 'city', 'vehicle_number',
                    'weight', 'status')
    fields = ('consignment', 'company', 'collected_by', 'city', 'latitude', 'longitude',
              'vehicle_number', 'weight', 'status', 'empty_vehicle_img', 'loaded_vehicle_img',
              'lr_copy_img', 'vehicle_number_img', 'delivery_challan_img', 'e_way_bill_img', 'weighment_slip_img','license_plate_no', 'manual_entry')
    list_display_links = ('consignment', 'company', 'collected_by', 'status', )

    list_filter = ('consignment', 'company', 'status', 'dispatch_date')
    search_fields = ('consignment__consignment_id',)


class RemarkAdmin(admin.ModelAdmin):
    list_display = ('consignment', 'remark', 'remark_date', 'remark_to')


admin.site.register(Order, OrderAdmin)
admin.site.register(Consignment, ConsignmentAdmin)
admin.site.register(CollectionEntries, CollectionEntriesAdmin)
admin.site.register(Remark, RemarkAdmin)
admin.site.register(CollectionRevision)
