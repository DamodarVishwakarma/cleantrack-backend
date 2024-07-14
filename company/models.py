from django.db import models
from digitalplatformbackend.constants import company_constants, company_status_constants


class Company(models.Model):
    id = models.BigIntegerField(primary_key=True,default=None)
    name = models.CharField(max_length=225)
    street = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    zip_code = models.CharField(max_length=255, blank=True, null=True)
    Type_Choices = (
        (company_constants.collection_agency, 'Collection Agency'),
        (company_constants.disposal_agency, 'Disposal Agency'),
        (company_constants.others, 'Others'),
    )
    company_type = models.IntegerField(choices=Type_Choices, blank=True, null=True)
    Status_Choices = (
        (company_status_constants.active, "Active"),
        (company_status_constants.deactive, "Deactive"),
    )
    company_status = models.IntegerField(choices=Status_Choices, default=company_status_constants.deactive)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Companies"
