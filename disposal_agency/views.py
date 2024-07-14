from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime

from digitalplatformbackend.constants import user_constants, company_constants
from .serializer import DisposalEntriesSerializer, DisposalGetEntriesSerializer
from .models import DisposalEntries
from transporter.serializer import ConsignmentSerializer
from . import models
from .forms import DisposalEntriesForm
from transporter.models import Consignment, Remark
from company.models import Company
from user.models import User
from user.email_feature import send_email
import logging

logger = logging.getLogger(__name__)


class DisposalEntriesViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = models.DisposalEntries.objects.all()
    serializer_class = DisposalEntriesSerializer

    def dispatch(self, request, *args, **kwargs):
        dispatch = super().dispatch(request, *args, **kwargs)
        if not request.user or request.user.is_anonymous:
            logger.warning(f"{request.user.email} is not Authorized")
            return HttpResponse({'error: user is not Authorized'}, status=status.HTTP_403_FORBIDDEN)
        if self.request.user.user_type != user_constants.Disposal_Agent and (
                self.request.user.user_type != user_constants.Admin):
            logger.warning(f"{request.user.email} is not Disposal Agent")
            return HttpResponse({'error : User is not Disposal Agent'}, status=status.HTTP_403_FORBIDDEN)
        if (self.request.user.user_type != user_constants.Admin) and (not self.request.user.approved_by_super_admin):
            logger.warning(f"{request.user.email} is not approved by Super admin")
            return HttpResponse({'error : user is not approved by Super admin'}, status=status.HTTP_403_FORBIDDEN)
        if (self.request.user.user_type != user_constants.Admin) and (not self.request.user.approved_by_company_admin):
            logger.warning(f"{request.user.email} is not approved by company")
            return HttpResponse({'error :user is not approved by company'}, status=status.HTTP_403_FORBIDDEN)
        if self.request.user.user_type == user_constants.Disposal_Agent and self.action in ['put', 'patch', 'delete']:
            logger.warning(f"{request.user.email} is not not allowed")
            return HttpResponse({'error : user is not allowed'}, status=status.HTTP_403_FORBIDDEN)
        return dispatch

    def get_queryset(self):
        if self.request.user.user_type == user_constants.Admin:
            logger.info(f"get All collection Entry for {self.request.user.email} ")
            return models.DisposalEntries.objects.all().order_by('-unloading_date')
        if self.request.user.user_type == user_constants.Disposal_Agent:
            logger.info(f"get Disposal Entry for {self.request.user.email}")
            return models.DisposalEntries.objects.filter(collected_by=self.request.user.id).order_by('-unloading_date')

    def get_serializer_class(self):

        if self.action in ['list', 'GET', 'retrieve']:
            return DisposalGetEntriesSerializer
        else:
            return DisposalEntriesSerializer

    def create(self, request, *args, **kwargs):
        if request.data.get('consignment'):
            if models.DisposalEntries.objects.filter(consignment=request.data.get('consignment')):
                logger.warning(f"entry for this consignment already exist")

                return Response({"error": "entry for consignment already exist"},
                                status=status.HTTP_400_BAD_REQUEST)  # todo: change to 400
            serializer = DisposalEntriesSerializer(data=request.data, context={'user': self.request.user})

            if serializer.is_valid():
                serializer.save()
                logger.info(f"Disposal entry Created Successfully = {serializer.data}")
                email_data = serializer.data
                email_data[
                    'heading'] = 'Thank you!! for choosing Cleantrack at your initiative towards the green planet!'
                email_data['subheading'] = 'Details for disposal are successfully submitted'
                consignment_number = Consignment.objects.get(id=serializer.data['consignment'])
                email_data['consignment_no'] = consignment_number.consignment_id
                email_data['order_number'] = consignment_number.order_number.order_number
                disposal_date = datetime.now()
                converted_time = disposal_date.strftime("%m/%d/%Y  %I:%M %p")
                email_data['unloading_date'] = converted_time

                email_list = []
                disposal_check = False
                collection_check = False
                customer = consignment_number.order_number.customer
                if customer.allow_to_send_mail:
                    email_list.append(customer.email)
                disposal_user = User.objects.get(id=serializer.data['collected_by'])
                if disposal_user.allow_to_send_mail:
                    email_list.append(disposal_user)

                collection_users = User.objects.filter(company_id=consignment_number.order_number.collection_agency_id)
                for collection_user in collection_users:
                    if collection_user.allow_to_send_mail:
                        collection_check = True
                        email_list.append(collection_user.email)
                disposal_users = User.objects.filter(company_id=consignment_number.order_number.disposal_agency_id)
                for disposal_user in disposal_users:
                    if disposal_user.allow_to_send_mail:
                        disposal_check = True
                        email_list.append(disposal_user.email)
                if (disposal_check and collection_check):
                    subject = "Disposal Entry Created"
                    try:
                        send_email(email_list, subject, **email_data)
                        logger.info("email send successfully")
                    except:
                        logger.warning(
                            "smtplib.SMTPDataError: (552, b'User support@cleantrack.in has recently been created/modified, and has exceeded an hourly sending limit. Please wait, and attempt to send your message at a later time.')")
                if not (disposal_check):
                    logger.info(
                        f"email can't be sent because there is no Admin from {consignment_number.order_number.disposal_agency}")
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                logger.error(f"Disposalc entry can't be Created due to {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # todo : change to 400
        else:
            logger.warning(f"disposal can't be created due to wrong Consignment id")
            return Response({'error': 'consignment not selected'}, status=status.HTTP_400_BAD_REQUEST)


@login_required(login_url='login')
def disposals(request):
    context = {}
    if request.user.user_type == user_constants.Admin:
        disposal = models.DisposalEntries.objects.all()
        context = {
            'disposals': disposal
        }
    if request.user.user_type == user_constants.Company_Admin:
        disposal = models.DisposalEntries.objects.filter(company=request.user.company_id)
        context = {
            'disposals': disposal
        }
    if request.user.user_type == user_constants.Verifier:
        disposal = models.DisposalEntries.objects.all()
        context = {
            'disposals': disposal
        }
    logger.info("Disposal Entry List")
    return render(request, 'newadmin/disposals.html', context)  # FIXME: url and file name should be proper // NIKHIL


@login_required(login_url='login')
def add_disposal(request):
    disposal_form = DisposalEntriesForm()
    content = {"disposal_form": disposal_form}
    if request.method == "POST":
        disposal_form = DisposalEntriesForm(request.POST, request.FILES)
        if disposal_form.is_valid():
            try:
                if DisposalEntries.objects.get(consignment__consignment_id=disposal_form.cleaned_data['consignment']):
                    context = {'message': 'Consignment entry already exist.', 'disposal_form': disposal_form}
                    return render(request, 'newadmin/add_disposal_entries.html', context)
            except:
                pass
            disposal_form.save()
            logger.info(f"Disposal Entry Created")
            return redirect("disposals")
        else:
            context = {'message': 'Something went wrong', 'disposal_form': disposal_form}
            logger.warning("Disposal Entry Not Created")
            return render(request, 'newadmin/add_disposal_entries.html', context)
    return render(request, "newadmin/add_disposal_entries.html", content)


@login_required(login_url='login')
def edit_disposal(request, edit_id):
    update_disposal = models.DisposalEntries.objects.get(id=edit_id)
    disposal_instance = DisposalEntriesForm(instance=update_disposal)
    try:
        remark = Remark.objects.get(consignment=update_disposal.consignment)
    except Remark.DoesNotExist:
        remark = ''
    if request.method == 'POST':
        disposal_instance = DisposalEntriesForm(request.POST, request.FILES, instance=update_disposal)
        if disposal_instance.is_valid():
            coll = disposal_instance.save(commit=False)
            coll.unloading_date = request.POST.get('disposal_date')
            coll.save()
            # disposal_instance.save()
            if request.POST.get('remark'):
                if not remark:
                    Remark.objects.create(consignment=update_disposal.consignment, remark=request.POST.get('remark'),
                                          remark_to=company_constants.disposal_agency)
                else:
                    remark = Remark.objects.get(consignment=update_disposal.consignment)
                    remark.remark = request.POST.get('remark')
                    remark.save()
            logger.info(f"Disposal Entry Updated")
            return redirect('disposals')
        else:
            message = {'error': 'Invalid Data'}
            logger.error(f"Disposal Entry Not Updated")
            return render('/', message)
    context = {'disposal_instance': disposal_instance,
               'remark': remark, 'update_disposal': update_disposal,
               'unloading_date': str(update_disposal.unloading_date)}
    return render(request, "newadmin/edit_disposal.html", context)


@login_required(login_url='login')
def delete_disposal(request, del_id):
    del_disposal_entry = models.Consignment.objects.get(consignment_id=del_id)
    del_disposal_entry.delete()
    logger.info(f"Disposal Entry Deleted for Consignment {del_disposal_entry.consignment_id}")
    return redirect('disposals')
