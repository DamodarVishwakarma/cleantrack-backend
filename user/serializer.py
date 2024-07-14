from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.hashers import make_password
from digitalplatformbackend.constants import company_status_constants

from user.models import User, Otp
from transporter.models import Consignment, CollectionEntries
from disposal_agency.models import DisposalEntries

from transporter import constatnts as collection_constants
from disposal_agency import constants as disposal_constants
from random import randint
from digitalplatformbackend.constants import user_constants
from user.email_feature import send_email
import logging

logger = logging.getLogger(__name__)


class AuthenticationSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        if user.user_type in [2, 3, 4, 5, 6] and user.company:
            # validation for company admin ====
            if user.user_type == 6:
                if not user.approved_by_super_admin:
                    logger.warning(f"{user.email} is not Approved by super admin ")
                    raise serializers.ValidationError({'error': 'Company Admin Should Approved by Super Admin'})
                elif not user.company.company_status == company_status_constants.active:
                    logger.warning(f"{user.email} is not Active ")
                    raise serializers.ValidationError({'error': 'Company is not active'})
            # end of company admin validation

            # Agents of company validation ===
            elif user.user_type in [2, 3]:
                if not user.approved_by_super_admin:
                    logger.warning(f"{user.email} is not Approved by super admin ")
                    raise serializers.ValidationError({'error': 'Agent Must Approved by Super Admin'})
                elif not user.approved_by_company_admin:
                    logger.warning(f"{user.email} is not Active ")
                    raise serializers.ValidationError({'error': 'Agent must have Approval of Company '})
            # Agents of company validation  end ==

            elif not user.approved_by_super_admin:
                logger.warning(f"{user.email} is not Active ")
                raise serializers.ValidationError({'error': 'User is not active'})
        token = super().get_token(user)
        logger.info(f"{user.email}  login succesfully ")
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['id'] = self.user.id
        data['email'] = self.user.email
        data['user_type'] = self.user.user_type
        data['phone'] = self.user.phone
        return data


from company.models import Company


class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    company = serializers.IntegerField(required=True)

    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            # 'password': {'write_only': True},
            'last_login': {'write_only': True},
            'password_hint': {'write_only': True},
            'user_permissions': {'write_only': True},
            'is_superuser': {'write_only': True},
        }

    def validate_company(self, company):
        if not company:
            raise serializers.ValidationError('This field is required.')
        try:
            return Company.objects.get(id=company)
        except Company.DoesNotExist:
            raise serializers.ValidationError('Please enter valid company ID.')

    def validate(self, data):
        args = [""]
        email = data.get('email')
        password = data.get('password')
        phone = data.get('phone')
        fullname = data.get('first_name') + " " + data.get('last_name')
        email_data = {
            "heading": "Thanks for signing up to Cleantrack!",
            "body": "Access your account using following credentials:",
            "user_email": email,
            "password": password,
            "fullname": fullname,
            "phone_no": phone,
            "note": "Do not share your credentials with anyone !!!"

        }
        subject = "Welcome!! to the Green World of Cleantrack"

        if data.get('user_type') == user_constants.Customer:
            data['is_active'] = True
            data['is_staff'] = True
        if data.get('user_type') == user_constants.Company_Admin:
            data['is_active'] = True
            data['is_staff'] = True
        if data.get('user_type') == user_constants.Verifier:
            data['is_active'] = True
            data['is_staff'] = True
        if data.get('user_type') == user_constants.Admin:
            data['is_active'] = False
            data['is_staff'] = True
            data['is_superuser'] = True
        if data.get('password'):
            data['password'] = make_password(data['password'])
        send_email([email], subject, *args, **email_data)
        logger.info("email send successfully")
        return data


class UserGetSerializer(serializers.ModelSerializer):
    # is_active = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = '__all__'


class UserUpdateSerializer(serializers.ModelSerializer):
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ('password', 'is_active', 'approved_by_company_admin', 'approved_by_super_admin')


class ChangePasswordSerializer(serializers.Serializer):
    model = User

    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)


from django.db.models import Q


class OtpSerializer(serializers.ModelSerializer):
    phone_no = serializers.CharField(required=True)

    class Meta:
        model = Otp
        fields = ('phone_no', 'otp',)

    def validate_phone_no(self, phone_no):
        try:
            return User.objects.get(Q(phone=phone_no) | Q(email=phone_no))
        except User.DoesNotExist:
            raise serializers.ValidationError('User with these email or phone number does not exist.')


class ForgotPasswordSerializer(serializers.Serializer):
    phone_no = serializers.CharField()
    otp = serializers.IntegerField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate_otp(self, otp):
        try:
            return Otp.objects.get(phone_no=self.initial_data['phone_no'], otp=otp)
        except Otp.DoesNotExist:
            raise serializers.ValidationError('OTP is not valid.')

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError('Password and Confirm password must be same.')
        return attrs


class UserInfoSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'phone', 'full_name')

    def get_full_name(self, obj):
        return (obj.first_name + ' ' + obj.last_name) if (obj.first_name and obj.last_name) else '-'


class CustomerOrderSerializer(serializers.ModelSerializer):  # todo : needed to push updated code
    collection_entry = serializers.SerializerMethodField()
    disposal_entry = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Consignment
        fields = '__all__'

    def get_collection_entry(self, obj):
        if CollectionEntries.objects.get(consignment=obj):
            status = "Created"
        else:
            status = "Not Created"
        return status

    def get_disposal_entry(self, obj):
        try:
            disposal_entry = DisposalEntries.objects.filter(consignment=obj)
        except:
            pass
        if disposal_entry:
            status = "Created"
        else:
            status = "Not Created"
        return status

    def get_status(self, obj):
        try:
            status_entry = CollectionEntries.objects.get(consignment=obj)
            status_disposal_entry = DisposalEntries.objects.get(consignment=obj)
        except:
            pass
        if status_entry or status_disposal_entry:
            if CollectionEntries.objects.get(consignment=obj).status == collection_constants.Approved:
                if DisposalEntries.objects.get(consignment=obj).status == disposal_constants.Approved:
                    return "Approved"
                else:
                    return "Pending"
            else:
                return "Pending"
            # if CollectionEntries.objects.get(consignment=obj).status == collection_constants.Rejected:
            #     if DisposalEntries.objects.get(consignment=obj).status == disposal_constants.Rejected:
            #         return "Rejected"
            #     else:
            #         return "Pending"
            # else:
            #     return "Pending"
        else:
            return "Not Created yet"
