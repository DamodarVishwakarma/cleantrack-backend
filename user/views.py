from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from .models import User, Otp
from . import serializer as user_serializer
from rest_framework import generics
from datetime import datetime
from .serializer import ChangePasswordSerializer, CustomerOrderSerializer, OtpSerializer, ForgotPasswordSerializer, \
    UserSerializer
from rest_framework.response import Response
from rest_framework import status
from .forms import UserForm, LoginForm
from dateutil.parser import parse
from transporter.models import Order, CollectionEntries, Consignment, Remark
from digitalplatformbackend.constants import user_constants, company_constants, consignment_constants
from disposal_agency.models import DisposalEntries
from company.models import Company
from transporter.forms import CollectionReviewForm, RemarkForm
from disposal_agency.forms import DisposalEntriesForm, DisposalReviewForm
from user.email_feature import send_email
from company.report_generation import generate_customer_reports

import logging

logger = logging.getLogger(__name__)


class Authenticate(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = user_serializer.AuthenticationSerializer


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = user_serializer.UserGetSerializer  # todo : please verify the either we need this serializer or not.
    model = User

    def get_queryset(self):
        if self.request.user.user_type == user_constants.Admin:
            logger.info(f"Get all data for Admin")
            return User.objects.all()
        logger.info(f"Get all data for {self.request.user.email}")
        return User.objects.filter(email=self.request.user.email)

    def get_serializer_class(self):
        if self.action in ['put', 'patch']:
            return user_serializer.UserUpdateSerializer
        elif self.action in ['retrieve', 'list']:
            return user_serializer.UserGetSerializer
        else:
            return user_serializer.UserSerializer


from django.db.models import Q
from random import randint


class OtpView(APIView):
    permission_classes = (AllowAny,)
    serilalizer_class = OtpSerializer

    def post(self, request):
        ser = OtpSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.validated_data.get('phone_no')
        otp, created = Otp.objects.get_or_create(user=user)
        otp.otp = randint(100000, 999999)
        otp.phone_no = ser.initial_data['phone_no']
        otp.save()
        send_email([user.email], 'OTP Generated',
                   **{'phone_no': otp.user.phone, 'otp': otp.otp, 'user_email': otp.user.email})
        return Response(ser.data, status=status.HTTP_200_OK)


class ForgotPassword(APIView):
    permission_classes = (AllowAny,)
    serializer_class = ForgotPasswordSerializer
    model = User

    def post(self, request):
        print(request.data)
        ser = ForgotPasswordSerializer(data=request.data)
        # print(ser.errors)
        ser.is_valid(raise_exception=True)
        otp = ser.validated_data.get("otp")
        # print(otp)
        otp.user.set_password(request.data.get("new_password"))
        otp.user.save()
        subject = "Password Update Successfully "
        email_data = {
            'heading': 'Your password was changed ',
            'user_email': otp.user.email,
            'phone_no': otp.user.phone,
            'password': request.data.get("new_password")
        }
        send_email([otp.user.email], subject, **email_data)
        otp.delete()
        # print(ser.data)
        # print()
        return Response({"success": "password Updated"}, status=status.HTTP_200_OK)


class ChangePasswordView(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        self.object = self.request.user
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                logger.warning(f"Invalid Old password ")
                return Response({"error": "Invalid Old password"}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            new_pass = serializer.data.get("new_password")
            confirm_pass = serializer.data.get("confirm_password")
            if new_pass != confirm_pass:
                logger.warning(f"Password not matched")
                return Response({"error": "Password must matched"}, status=status.HTTP_400_BAD_REQUEST)

            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomersOrder(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = self.request.user

        if user.user_type == user_constants.Admin:
            collection = Consignment.objects.all()
            serializer = CustomerOrderSerializer(collection, many=True)
            return Response(serializer.data)

        if user.user_type != user_constants.Admin:
            customer_order = Order.objects.filter(customer=user.id)
            if customer_order:
                for i in customer_order:
                    order_number = i
                customer_consignment = Consignment.objects.filter(order_number=order_number)
                serializer = CustomerOrderSerializer(customer_consignment, many=True)
                return Response(serializer.data)
            else:
                logger.warning(f"{user.email} have No data")
                return Response({'error': 'User have No data !'})
        return Response({'error': 'something Wrong'}, status=status.HTTP_403_FORBIDDEN)  # FIXME: Update Proper messages


# Create your views here.

@login_required(login_url='login')
def dashboard(request):
    user_count = 0
    order_count = 0
    consignment_count = 0
    if request.user.user_type == user_constants.Admin or request.user.user_type == user_constants.Verifier:
        user_count = User.objects.all().count()
        order_count = Order.objects.all().count()
        consignment_count = Consignment.objects.all().count()
    elif request.user.user_type == user_constants.Company_Admin:
        user_count = User.objects.filter(company=request.user.company).count()
        user_company = Company.objects.get(id=request.user.company.id)
        if user_company.company_type == company_constants.collection_agency:
            order_count = Order.objects.filter(collection_agency=user_company.id).count()
            consignment_count = CollectionEntries.objects.filter(company=user_company.id).count()
        else:
            order_count = Order.objects.filter(disposal_agency=user_company.id).count()
            consignment_count = DisposalEntries.objects.filter(company=user_company.id).count()
    elif request.user.user_type == user_constants.Customer:
        order_count = Order.objects.filter(customer=request.user).count()
        consignment_count = CollectionEntries.objects.filter(consignment__order_number__customer=request.user).count()
    approve = 0
    reject = 0
    bar_chart_data = 0
    collections = CollectionEntries.objects.all()
    disposals = DisposalEntries.objects.all()
    pending = collections.count()
    if (request.user.user_type == user_constants.Admin) or (request.user.user_type == user_constants.Verifier):
        bar_chart_data = collections
        for collection in collections:
            for disposal in disposals:
                if (collection.consignment == disposal.consignment) and \
                        (collection.status == consignment_constants.Rejected or \
                         disposal.disposal_status == consignment_constants.Rejected):
                    reject += 1
                    pending -= 1
                elif (collection.consignment == disposal.consignment) and \
                        (collection.status == consignment_constants.Approved and \
                         disposal.disposal_status == consignment_constants.Approved):
                    approve += 1
                    pending -= 1
    elif request.user.user_type == user_constants.Customer:
        collections = collections.filter(consignment__order_number__customer_id=request.user.id)
        bar_chart_data = collections
        pending = collections.count()
        for collection in collections:
            for disposal in disposals:
                if (collection.consignment == disposal.consignment) and \
                        (collection.status == consignment_constants.Rejected or \
                         disposal.disposal_status == consignment_constants.Rejected):
                    reject += 1
                    pending -= 1
                elif (collection.consignment == disposal.consignment) and \
                        (collection.status == consignment_constants.Approved and \
                         disposal.disposal_status == consignment_constants.Approved):
                    approve += 1
                    pending -= 1

    elif request.user.user_type == user_constants.Company_Admin:
        if request.user.company.company_type == company_constants.collection_agency:
            collections = collections.filter(consignment__order_number__collection_agency_id=request.user.company.id)
            bar_chart_data = collections
        if request.user.company.company_type == company_constants.disposal_agency:
            disposals = disposals.filter(consignment__order_number__disposal_agency_id=request.user.company.id)
            collections = collections.filter(consignment__order_number__disposal_agency_id=request.user.company.id)
            bar_chart_data = disposals
        pending = collections.count()
        for collection in collections:
            for disposal in disposals:
                if (collection.consignment == disposal.consignment) and \
                        (collection.status == consignment_constants.Rejected or \
                         disposal.disposal_status == consignment_constants.Rejected):
                    reject += 1
                    pending -= 1
                elif (collection.consignment == disposal.consignment) and \
                        (collection.status == consignment_constants.Approved and \
                         disposal.disposal_status == consignment_constants.Approved):
                    approve += 1
                    pending -= 1
    total_status = approve + reject + pending
    if total_status:
        approve = round((approve / total_status) * 100, 2)
        reject = round((reject / total_status) * 100, 2)
        pending = round((pending / total_status) * 100, 2)
    context = {
        'approve': approve,
        'reject': reject,
        'pending': pending,
        "bar_chart_data": bar_chart_data,
        'total_orders': order_count,
        'total_consignment': consignment_count,
        'total_users': user_count,
        'total_status': total_status,
    }
    return render(request, 'newadmin/dashboard.html', context)


@login_required(login_url='login')
def user(request):
    content = {}
    if request.user.user_type == user_constants.Admin:
        users = User.objects.all()
        content = {
            'users': users,
        }
        logger.info(f"User list of {request.user.email}")
        return render(request, 'newadmin/alluser.html', content)

    elif request.user.user_type == user_constants.Company_Admin:
        users = User.objects.filter(company_id=request.user.company.id)
        content = {
            'users': users,
        }
        logger.info(f"User list of {request.user.email}")
        return render(request, 'newadmin/alluser.html', content)
    elif request.user.user_type == user_constants.Verifier:
        collections = CollectionEntries.objects.all()
        content = {
            'users': collections,
        }
        logger.info(f"collections list of verifier {request.user.email}")
        return redirect("collections")

    return render(request, 'newadmin/alluser.html', content)  # FIXME: ---||---


@login_required(login_url='login')
def create_user(request):
    form = UserForm()
    user = request.user
    if user.user_type == user_constants.Company_Admin:
        if user.company.company_type == company_constants.collection_agency:
            form.fields['company'].queryset = Company.objects.filter(id=user.company.id)
            form.fields["user_type"].choices = [(2, 'Collection Agent'), (6, 'Company Admin')]
        elif user.company.company_type == company_constants.disposal_agency:
            form.fields['company'].queryset = Company.objects.filter(id=user.company.id)
            form.fields["user_type"].choices = [(3, 'Disposal Agent'), (6, 'Company Admin')]

    context = {'form': form}
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        email = request.POST["email"]
        password = request.POST["password"]
        phone_number = request.POST["phone"]
        full_name = request.POST["first_name"] + " " + request.POST["last_name"]
        email_data = {
            "heading": "Thanks for signing up to Cleantrack!",
            "body": "Access your account using following credentials:",
            "user_email": email,
            "password": password,
            "fullname": full_name,
            "phone_no": phone_number,
            "note": "Do not share your credentials with anyone !!!"
        }
        subject = "Welcome!! to the Green World of Cleantrack"

        if user_form.is_valid():
            user_form.password = make_password(user_form.cleaned_data['password'])
            user_form.save()
            password_hash = User.objects.get(email=user_form.cleaned_data['email'])
            password_hash.password = user_form.password
            password_hash.save()
            logger.info(f"User Created")
            try:
                send_email([email], subject, **email_data)
                logger.info("email send successfully")
            except Exception:
                pass
            return redirect('user')
        else:
            context = {'message': 'Something went wrong', 'errors': user_form.errors, 'form': form}
            logger.error("User not created")
            return render(request, 'newadmin/add_user.html', context)
    return render(request, 'newadmin/add_user.html', context)


@login_required(login_url='login')
def update_user(request, user_id):
    update_user = User.objects.get(id=user_id)
    user_instance = UserForm(instance=update_user)

    if request.method == 'POST':
        user_update = UserForm(request.POST, instance=update_user)
        if user_update.is_valid():

            form_password = user_update.cleaned_data['password']
            user_obj = User.objects.get(id=user_id)
            if form_password != user_obj.password:
                user_updated = user_update.save()
                user_updated.password = make_password(form_password)
                if request.user.user_type == user_constants.Company_Admin:
                    if user_obj.is_active:
                        user_updated.is_active = True
                    if user_obj.approved_by_super_admin:
                        user_updated.approved_by_super_admin = True
                    if user_obj.is_staff:
                        user_updated.is_staff = True
                    if user_obj.is_superuser:
                        user_updated.is_superuser = True
                user_updated.save()
                subject = "Password Update Successfully "
                email_data = {
                    'heading': 'Your password was changed ',
                    'user_email': user_obj.email,
                    'phone_no': user_obj.phone,
                    'password': form_password
                }
                send_email([user_obj.email], subject, **email_data)
                logger.info(f"Email Send Successfully")
            else:
                user_updated = user_update.save()
                if request.user.user_type == user_constants.Company_Admin:
                    if user_obj.is_active:
                        user_updated.is_active = True
                    if user_obj.approved_by_super_admin:
                        user_updated.approved_by_super_admin = True
                    if user_obj.is_staff:
                        user_updated.is_staff = True
                    if user_obj.is_superuser:
                        user_updated.is_superuser = True
                user_updated.save()
            logger.info(f"User updated")
            return redirect('user')
        else:
            message = {'error': 'Invalid Data', 'update_user': user_instance}
            logger.warning(f"Invalid Data")
            return render(request, 'newadmin/edit_user.html', message)
    if request.user.user_type == user_constants.Company_Admin:
        if request.user.company.company_type == company_constants.collection_agency:
            user_instance.fields['company'].queryset = Company.objects.filter(
                company_type=company_constants.collection_agency)
            user_instance.fields["user_type"].choices = [(2, 'Collection Agent'), (6, 'Company Admin')]
        else:
            user_instance.fields['company'].queryset = Company.objects.filter(
                company_type=company_constants.disposal_agency)
            user_instance.fields["user_type"].choices = [(3, 'Disposal Agent'), (6, 'Company Admin')]

    context = {
        'update_user': user_instance
    }
    return render(request, 'newadmin/edit_user.html', context)


@login_required(login_url='login')
def delete_user(request, del_id):
    del_user = User.objects.get(id=del_id)
    del_user.delete()
    logger.info(f"{del_user.email} Deleted Successfully")
    return redirect('user')


@login_required(login_url='login')
def review(request, id):
    try:
        collections = CollectionEntries.objects.get(consignment__consignment_id=id)
    except CollectionEntries.DoesNotExist:
        collections = None
    try:
        disposals = DisposalEntries.objects.get(consignment__consignment_id=id)
    except DisposalEntries.DoesNotExist:
        disposals = None

    if request.user.user_type == user_constants.Company_Admin:
        try:
            remark_instance = Remark.objects.get(consignment__consignment_id=id)
        except Remark.DoesNotExist:
            remark_instance = ''
        context = {'collections': collections, 'disposals': disposals, 'remark_instance': remark_instance}
    else:
        collection_instance = CollectionReviewForm(instance=collections)
        disposal_instance = DisposalReviewForm(instance=disposals)
        try:
            remark_instance = Remark.objects.get(consignment__consignment_id=id)
        except:
            remark_instance = ''

        if request.method == 'POST':
            collection_status = request.POST.get('status')
            disposal_status = request.POST.get('disposal_status')
            remark_data = request.POST.get('remark')

            remark_company = None
            if str(collection_status) == str(consignment_constants.Rejected) and str(disposal_status) != str(
                    consignment_constants.Rejected):
                remark_company = company_constants.collection_agency
            elif str(collection_status) != str(consignment_constants.Rejected) and str(disposal_status) == str(
                    consignment_constants.Rejected):
                remark_company = company_constants.disposal_agency
            elif str(collection_status) == str(consignment_constants.Rejected) and str(disposal_status) == str(
                    consignment_constants.Rejected):
                remark_company = company_constants.Both_Agency
            elif str(collection_status) == str(consignment_constants.Approved) and str(disposal_status) == str(
                    consignment_constants.Approved):
                remark_company = company_constants.Both_Agency
            elif str(collection_status) == str(consignment_constants.Pending) and str(disposal_status) == str(
                    consignment_constants.Pending):
                remark_company = company_constants.Both_Agency
            if not remark_data:
                remark_data = "None"
            remark_obj = Remark.objects.create(consignment=collections.consignment, remark=remark_data,
                                               remark_to=remark_company)
            remark_obj.save()

            collections.status = collection_status
            collections.save()
            disposals.disposal_status = disposal_status
            disposals.save()

            return redirect('collections')
        remark = RemarkForm()
        context = {'collections': collections, 'collection_instance': collection_instance, 'disposals': disposals,
                   'disposal_instance': disposal_instance, 'remark': remark, 'remark_instance': remark_instance}
    return render(request, 'newadmin/review.html', context)


def customer_data(request):
    context = {}
    collections = CollectionEntries.objects.filter(consignment__order_number__customer_id=request.user.id)
    context = {'collections': collections}
    return render(request, 'newadmin/customer.html', context)


@login_required(login_url='login')
def customer_report(request):
    return redirect('report')


def get_user(email):
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return None


def user_login(request):
    form = LoginForm()
    context = {'form': form}
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        username = get_user(email)
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active and user.is_staff:
                if user.user_type == user_constants.Admin:
                    login(request, user)
                    logger.info(f'{user.email} login successfully')
                elif user.approved_by_super_admin and (
                        user.user_type == user_constants.Company_Admin or user_constants.Verifier or user_constants.Customer):
                    login(request, user)
                    logger.info(f'{user.email} login successfully')
                else:
                    context = {'message': 'User Access Denied', 'form': form}
                    logger.warning(f'{user.email} is not allowed to login')
                    return render(request, 'newadmin/login.html', context)

                if user.user_type == user_constants.Customer:
                    return redirect('dashboard')
                if user.user_type == user_constants.Verifier:
                    # return redirect('collections')
                    return redirect('dashboard')

                if user.user_type == user_constants.Admin or user_constants.Company_Admin:
                    return redirect('dashboard')

            else:
                context = {'message': 'User does not have access to this portal', 'form': form}
                logger.info(f"Invalid email or password")
                return render(request, 'newadmin/login.html', context)
        else:
            context = {'message': 'Invalid Email or Password', 'form': form}
            # logger.warning(f"User does not exists {request.user.email}")
            return render(request, 'newadmin/login.html', context)
    return render(request, 'newadmin/login.html', context)


def user_logout(request):
    logout(request)
    logger.info(f"Successfully Logged out")
    return redirect('login')


@login_required(login_url='login')
def report_dashboard(request):
    if request.method == 'POST':
        start_date = request.POST.get('datepicker')
        end_date = request.POST.get('datepicker2')
        if start_date and end_date:
            start_date = parse(start_date)
            end_date = parse(end_date)
            kwarks = {'start_date': start_date, 'end_date': end_date}
            return generate_customer_reports(request, **kwarks)
        else:
            return render(request, 'newadmin/report_download.html', {'error': 'Enter Start Date and End Date'})

    return render(request, 'newadmin/report_download.html')


@api_view(('GET',))
@permission_classes((IsAuthenticated,))
def user_details(request):
    login_response_serializer = user_serializer.UserGetSerializer(request.user)
    return Response(login_response_serializer.data, status=status.HTTP_200_OK)


def reset_otp(request):
    if request.method == 'POST':
        otp_field = request.POST.get('send_otp')
        if otp_field.isnumeric():
            try:
                user = User.objects.get(phone=otp_field)
            except:
                user = None
                logger.warning(f"User phone number not exist {otp_field}")
            if user:
                try:
                    random_otp = get_random_string(length=6, allowed_chars='1234567890')
                    otp_object = Otp.objects.create(phone_no=otp_field, otp=random_otp)
                    otp_object.save()
                    logger.info(f"OTP Created {random_otp}")

                    subject = "OTP Created "
                    email_data = {
                        'heading': 'OTP Created ',
                        'user_email': user.email,
                        'phone_no': user.phone,
                        'otp': random_otp
                    }
                    send_email([user.email], subject, **email_data)
                    logger.info(f"Email Send Succssfully")
                    return redirect('reset_password')
                except:
                    exist_user = Otp.objects.get(phone_no=otp_field)
                    exist_user.delete()
                    random_otp = get_random_string(length=6, allowed_chars='1234567890')
                    otp_object = Otp.objects.create(phone_no=otp_field, otp=random_otp)
                    otp_object.save()
                    logger.info(f"OTP Created {random_otp}")

                    subject = "OTP Created "
                    email_data = {
                        'heading': 'OTP Created ',
                        'user_email': user.email,
                        'phone_no': user.phone,
                        'otp': random_otp
                    }
                    send_email([user.email], subject, **email_data)
                    logger.info(f"Email Send Succssfully")
                    return redirect('reset_password')
        else:
            try:
                user = User.objects.get(email=otp_field)
            except:
                user = None
                logger.warning(f"User email not exist {otp_field}")
            if user:
                try:
                    random_otp = get_random_string(length=6, allowed_chars='1234567890')
                    otp_object = Otp.objects.create(phone_no=user.phone, otp=random_otp)
                    otp_object.save()
                    logger.info(f"OTP Created {random_otp}")

                    subject = "OTP Created"
                    email_data = {
                        'heading': 'OTP Created ',
                        'user_email': user.email,
                        'phone_no': user.phone,
                        'otp': random_otp
                    }
                    send_email([user.email], subject, **email_data)
                    logger.info(f"Email Send Succssfully")
                    return redirect('reset_password')
                except:
                    exist_user = Otp.objects.get(phone_no=user.phone)
                    exist_user.delete()
                    random_otp = get_random_string(length=6, allowed_chars='1234567890')
                    otp_object = Otp.objects.create(phone_no=user.phone, otp=random_otp)
                    otp_object.save()
                    logger.info(f"OTP Created {random_otp}")

                    subject = "OTP created "
                    email_data = {
                        'heading': 'OTP Created ',
                        'user_email': user.email,
                        'phone_no': user.phone,
                        'otp': random_otp
                    }
                    send_email([user.email], subject, **email_data)
                    logger.info(f"Email Send Succssfully")
                    return redirect('reset_password')
    return render(request, 'newadmin/reset_otp.html')


def reset_password(request):
    if request.method == 'POST':
        otp_field = request.POST.get('otp')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        try:
            otp_obj = Otp.objects.get(otp=otp_field)
        except:
            logger.warning(f"Invalid OTP = {otp_field}")
            return render(request, 'newadmin/reset_password.html', {'error': "Invalid OTP"})
        if otp_obj:
            if new_password == confirm_password:
                user = User.objects.get(phone=otp_obj.phone_no)
                user.password = make_password(new_password)
                user.save()
                logger.info(f"Password Created {new_password}")
                subject = "Password Update Successfully "
                email_data = {
                    'heading': 'Password Created ',
                    'user_email': user.email,
                    'phone_no': user.phone,
                    'password': new_password
                }
                send_email([user.email], subject, **email_data)
                logger.info(f"Email Send Succssfully")
                return redirect('login')
            else:
                return render(request, 'newadmin/reset_password.html', {'error': "Password does not match"})

    return render(request, 'newadmin/reset_password.html')


def privacy_policy(request):
    return render(request, 'newadmin/privacy_policy.html')
