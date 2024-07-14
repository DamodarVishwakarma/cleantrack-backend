from django.db import models
from user.models import User, Company
from transporter.models import Order, Consignment
from django.core.validators import RegexValidator

from digitalplatformbackend.constants import disposal_constants
from digitalplatformbackend.custom_fields import CustomImageField


class DisposalEntries(models.Model):
    consignment = models.ForeignKey(Consignment, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    unloading_date = models.DateTimeField(auto_now_add=True)
    vehicle_number = models.CharField(max_length=15, validators=[
        RegexValidator(r'^[A-Z]{2}[0-9]{1,2}[A-Z]{1,2}[0-9]{1,4}$',
                       message='Invalid vehicle number or it should be in capital')])
    city = models.CharField(max_length=25, blank=False, null=False)
    latitude = models.CharField(max_length=50, null=True, blank=False, validators=[
        RegexValidator(r'^[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?)$',
                       message='Not a valid latitude')])
    longitude = models.CharField(max_length=50, null=True, blank=False, validators=[
        RegexValidator(r'^\s*[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)$',
                       message='Not a valid longitude')])
    loaded_vehicle_img = CustomImageField(upload_to='Images/Disposals')
    vehicle_number_img = CustomImageField(upload_to='Images/Disposals')
    weighment_slip_img = CustomImageField(upload_to='Images/Disposals')
    weight = models.IntegerField(help_text="Weight in kG")
    collected_by = models.ForeignKey(User, on_delete=models.CASCADE)
    license_plate_no = models.CharField(max_length=15, null=True, blank=True)
    manual_entry = models.BooleanField(default=False)
    Status_Choices = (
        (disposal_constants.Approved, 'Approved'),
        (disposal_constants.Rejected, 'Rejected'),
        (disposal_constants.Pending, 'Pending'),
    )
    disposal_status = models.IntegerField(choices=Status_Choices, default=disposal_constants.Pending)

    def __int__(self):
        return self.consignment


class DisposalRevision(models.Model):  # FIXME: change name of class in CamelCase
    consignment = models.ForeignKey(Consignment, on_delete=models.CASCADE)
    disposal_vehicle_number_img = CustomImageField(upload_to="Images/Revisions")
    revision_date = models.DateTimeField(auto_now_add=True)

    def __int__(self):
        return self.consignment

