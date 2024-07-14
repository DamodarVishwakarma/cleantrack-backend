from django.core.validators import RegexValidator
from django.db import models

from company.models import Company
from digitalplatformbackend.constants import consignment_constants, company_constants
from user.models import User
from digitalplatformbackend.custom_fields import CustomImageField


class Order(models.Model):
    order_number = models.CharField(max_length=20, unique=True, null=False, blank=False)
    order_weight = models.CharField(max_length=10, null=False, blank=False)
    collection_agency = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='collection')
    disposal_agency = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='disposal')
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    Status_Choices = (
        (consignment_constants.Ongoing, 'Ongoing'),
        (consignment_constants.Completed, 'Completed'),
    )
    status = models.IntegerField(choices=Status_Choices, null=True, blank=True, default=consignment_constants.Ongoing)

    def __str__(self):
        return self.order_number


class Consignment(models.Model):
    order_number = models.ForeignKey(Order, on_delete=models.CASCADE)
    consignment_id = models.CharField(max_length=25, unique=True, null=False, blank=False)
    vehicle_number = models.CharField(max_length=15)

    def __str__(self):
        return self.consignment_id




class CollectionEntries(models.Model):
    consignment = models.ForeignKey(Consignment, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    collected_by = models.ForeignKey(User, on_delete=models.CASCADE)
    dispatch_date = models.DateTimeField(auto_now_add=True)
    city = models.CharField(max_length=25, blank=False, null=False)
    latitude = models.CharField(max_length=50, null=True, blank=False, validators=[
        RegexValidator(r'^[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?)$',
                       message='Not a valid latitude')])
    longitude = models.CharField(max_length=50, null=True, blank=False, validators=[
        RegexValidator(r'^\s*[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)$',
                       message='Not a valid longitude')])
    vehicle_number = models.CharField(max_length=15, validators=[
        RegexValidator(r'^[A-Z]{2}[0-9]{1,2}[A-Z]{1,2}[0-9]{1,4}$',
                       message='Invalid vehicle number or it should be in capital')])
    empty_vehicle_img = CustomImageField(upload_to='Images/Collection')
    loaded_vehicle_img = CustomImageField(upload_to='Images/Collection')
    lr_copy_img = CustomImageField(upload_to='Images/Collection')
    vehicle_number_img = CustomImageField(upload_to='Images/Collection')
    delivery_challan_img = CustomImageField(upload_to='Images/Collection')
    e_way_bill_img = CustomImageField(upload_to='Images/Collection')
    weighment_slip_img = CustomImageField(upload_to='Images/Collection')
    weight = models.IntegerField(help_text="Weight in kG")
    license_plate_no = models.CharField(max_length=15, null=True, blank=True)
    manual_entry = models.BooleanField(default=False)
    Status_Choices = (
        (consignment_constants.Approved, 'Approved'),
        (consignment_constants.Rejected, 'Rejected'),
        (consignment_constants.Pending, 'Pending'),
    )
    status = models.IntegerField(choices=Status_Choices, default=consignment_constants.Pending)

    def __int__(self):
        return self.consignment

    @property
    def disposal_entry(self):
        from disposal_agency.models import DisposalEntries
        try:
            return DisposalEntries.objects.get(consignment=self.consignment)
        except:
            return None


class Remark(models.Model):
    consignment = models.ForeignKey(Consignment, on_delete=models.CASCADE)
    remark_date = models.DateTimeField(auto_now_add=True)
    remark = models.CharField(max_length=500)
    Type_Choices = (
        (company_constants.collection_agency, 'Collection Agency'),
        (company_constants.disposal_agency, 'Disposal Agency'),
        (company_constants.others, 'Both Agency'),
    )
    remark_to = models.IntegerField(choices=Type_Choices, default=None)

    def __int__(self):
        return self.consignment


# FIXME : Change Name of App form Transporter to collection_agency

class CollectionRevision(models.Model):  # FIXME: change name of class in CamelCase
    consignment = models.ForeignKey(Consignment, on_delete=models.CASCADE)
    vehicle_number_img = CustomImageField(upload_to="Images/Revisions")
    revision_date = models.DateTimeField(auto_now_add=True)

    def __int__(self):
        return self.collection_entry
