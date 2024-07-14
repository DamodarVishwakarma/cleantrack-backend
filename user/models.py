from django.contrib.auth.models import AbstractUser
from django.db import models

from digitalplatformbackend.constants import user_constants
from company.models import Company


class User(AbstractUser):
    username = None  # Disregard built-in username field
    # name = models.CharField(max_length=50, blank=True, null=True)
    password_hint = models.CharField(max_length=255, blank=True, null=True)
    # password = models.CharField(max_length=32, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    zip_code = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(max_length=255, unique=True, blank=False, null=False)
    Type_Choices = (
        (user_constants.Admin, 'Admin'),
        (user_constants.Collection_Agent, 'Collection Agent'),
        (user_constants.Disposal_Agent, 'Disposal Agent'),
        (user_constants.Verifier, 'Verifier'),
        (user_constants.Customer, 'Customer'),
        (user_constants.Company_Admin, 'Company Admin'),
    )
    user_type = models.IntegerField(choices=Type_Choices, default=user_constants.Customer)
    approved_by_company_admin = models.BooleanField(default=False)
    approved_by_super_admin = models.BooleanField(default=False)
    allow_to_send_mail = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class Otp(models.Model):
    phone_no = models.CharField(max_length=105, unique=True, blank=False, null=False)
    otp = models.IntegerField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __int__(self):
        return self.phone_no
