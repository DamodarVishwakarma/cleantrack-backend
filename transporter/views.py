from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime

from .serializer import OrderSerializer, ConsignmentSerializer, CollectionEntriesSerializer, \
    CollectionGetEntriesSerializer, RemarkSerializer, ConsignmentGetSerializer
from . import models
from digitalplatformbackend.constants import user_constants, company_constants
from .forms import OrderForm, ConsignmentForm, CollectionEntriesForm
from transporter.models import Consignment, Order, CollectionEntries, Remark
from user.models import User
from user.email_feature import send_email
import logging

logger = logging.getLogger(__name__)


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = models.Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        params = self.request.query_params
        if 'status' in params:
            return models.Order.objects.filter(status=int(params.get('status'))).order_by('-id')
        if user.user_type == user_constants.Admin:
            logger.info(f"Get All Orders Data for Admin ")
            return models.Order.objects.filter(
                status=int(params.get('status'))).order_by('-id') if 'status' in params else models.Order.objects.all().order_by('-id')
        if user.user_type == user_constants.Collection_Agent or user_constants.Disposal_Agent or user_constants.Customer or user_constants.Company_Admin:
            logger.info(f"Get Order data of  {user.email} ")
            return models.Order.objects.filter(
                status=int(params.get('status')),
                collection_agency=user.company).order_by('-id') if 'status' in params else models.Order.objects.filter(
                collection_agency=user.company).order_by('-id')

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if self.request.user.user_type == user_constants.Admin and serializer.is_valid(raise_exception=True):
            # return models.Order.objects.create()
            super().create(request, *args, **kwargs)
            logger.info(f" Order Created Successfully ")
            return Response({'status': 'Order number created Successfully'})


class ConsignmentViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = models.Consignment.objects.all()
    serializer_class = ConsignmentSerializer

    def get_queryset(self):
        params = self.request.query_params
        if 'order_status' in params:
            consignment = models.Consignment.objects.filter(order_number__status=int(params.get('order_status')))
        else:
            user = User.objects.get(id=self.request.user.id)
            if user.user_type == user_constants.Disposal_Agent:
                collection = CollectionEntries.objects.filter(
                    consignment__order_number__disposal_agency=user.company.id).order_by('-dispatch_date')
                consignment = []
                for disposal_order in collection:
                    consignment.append(models.Consignment.objects.get(consignment_id=disposal_order.consignment))
                return consignment
            elif user.user_type == user_constants.Collection_Agent:
                collection_orders = Order.objects.filter(collection_agency=self.request.user.company_id).order_by('-id')
                consignment = []
                for collection_order in collection_orders:
                    collection_consignment = models.Consignment.objects.filter(order_number=collection_order.id)
                    for single_consignment in collection_consignment:
                        consignment.append(models.Consignment.objects.get(consignment_id=single_consignment))
                return consignment
            else:
                consignment = models.Consignment.objects.all()
                logger.info(f"Get All Consignment Data")
                return consignment

    def get_serializer_class(self):
        if self.action in ['list', 'GET', 'retrieve']:
            logger.info(f"get order Number")

            return ConsignmentGetSerializer
        else:
            logger.info(f"get order Number")
            return ConsignmentSerializer


class CollectionEntriesViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = CollectionEntriesSerializer
    queryset = models.CollectionEntries.objects.all()

    def dispatch(self, request, *args, **kwargs):
        dispatch = super().dispatch(request, *args, **kwargs)
        if not request.user or request.user.is_anonymous:
            logger.error(f"user is not Authorized")
            return HttpResponse({'error: user is not Authorized'}, status=status.HTTP_403_FORBIDDEN)
        if (self.request.user.user_type != user_constants.Collection_Agent) and (
                self.request.user.user_type != user_constants.Admin):
            logger.error(f"{request.user.email} is not Collection Agent or Admin")
            return HttpResponse({'error : User is not Collection Agent'}, status=status.HTTP_403_FORBIDDEN)
        if (self.request.user.user_type != user_constants.Admin) and (not self.request.user.approved_by_super_admin):
            logger.error(f"{request.user.email} is not approved by Super admin")
            return HttpResponse({'error : user is not approved by Super admin'}, status=status.HTTP_403_FORBIDDEN)
        if (self.request.user.user_type != user_constants.Admin) and (not self.request.user.approved_by_company_admin):
            logger.error(f"{request.user.email} is not approved by company")
            return HttpResponse({'error :user is not approved by company'}, status=status.HTTP_403_FORBIDDEN)
        if self.request.user.user_type == user_constants.Disposal_Agent and self.action in ['put', 'patch', 'delete']:
            logger.error(f"{request.user.email} is not not allowed")
            return HttpResponse({'error : user is not allowed'}, status=status.HTTP_403_FORBIDDEN)
        return dispatch

    def get_queryset(self):
        if self.request.user.user_type == user_constants.Admin:
            logger.info(f"get All collection Entry for {self.request.user.email} ")
            return models.CollectionEntries.objects.all().order_by('-dispatch_date')
        if self.request.user.user_type == user_constants.Collection_Agent:
            logger.info(f"get All collection Entry for {self.request.user.email} ")
            return models.CollectionEntries.objects.filter(collected_by=self.request.user.id).order_by('-dispatch_date')

    def get_serializer_class(self):
        if self.action in ['list', 'GET', 'retrieve']:
            logger.info(f"list of collection Entry")

            return CollectionGetEntriesSerializer
        else:
            logger.info(f"list of collection Entry")
            return CollectionEntriesSerializer

    def create(self, request, *args, **kwargs):
        if request.data.get('order_number') and request.data.get('weight'):
            try:
                order = Order.objects.get(id=request.data.get('order_number'))
            except Order.DoesNotExist:
                return Response({'error': 'Invalid order number.'})
            collection_entries = CollectionEntries.objects.filter(
                consignment__order_number=request.data.get('order_number'))
            collection_weight = 0
            for collection_entry in collection_entries:
                collection_weight = int(collection_entry.weight) + int(collection_weight)
            if collection_weight + int(request.data.get('weight')) > int(order.order_weight):
                return Response({
                    "error": f"weight should not exceed to order limit, {int(order.order_weight) - int(collection_weight)} kg"},
                    status=status.HTTP_400_BAD_REQUEST)
        # print(request.user.co)
        serializer = ConsignmentSerializer(data=request.data, context={'company': request.user.company_id})
        if not request.data.get('consignment'):
            if serializer.is_valid():

                serializer.save()
            else:
                logger.error(f"consignment can not be created due to {serializer.errors}")
                cons_id = serializer.data.get('id')
                ser = CollectionEntriesSerializer(data=request.data,
                                                  context={'user': self.request.user, 'consignment': cons_id})
                if ser.is_valid():
                    pass
                else:
                    error = serializer.errors  # adding errors of both consignment and collection
                    error.update(ser.errors)
                    return Response(error, status=status.HTTP_400_BAD_REQUEST)

            cons_id = serializer.data.get('id')
        else:
            try:
                collection_consignment = models.CollectionEntries.objects.get(
                    consignment=request.data.get('consignment'))
            except:
                collection_consignment = None
            if collection_consignment:
                logger.warning(
                    f"collection entry already created for this consignment id = {request.data.get('consignment')}")
                return Response({
                    "error": f"collection entry already created for this consignment id = {request.data.get('consignment')}"},
                    status=status.HTTP_400_BAD_REQUEST)
            consignment_obj = models.Consignment.objects.get(id=request.data.get('consignment'))
            cons_id = consignment_obj.id
        serializer = CollectionEntriesSerializer(data=request.data,
                                                 context={'user': self.request.user, 'consignment': cons_id,
                                                          'company_id': self.request.user.company})
        if serializer.is_valid():
            collection = serializer.save()
            # print(collection.data)
            collection_ser = CollectionEntriesSerializer(collection)
            # print(collection_ser.id)
            collection_user = User.objects.get(id=collection_ser.data['collected_by'])
            email_data = collection_ser.data
            email_data['heading'] = 'Thank you!! for choosing Cleantrack at your initiative towards the Green Planet!'
            email_data['subheading'] = 'Collection details are successfully submitted'

            consignment_number = Consignment.objects.get(id=collection_ser.data['consignment'])

            # email_data['created_by']=created_by.first_name+ " "+created_by.last_name
            email_data['consignment_no'] = consignment_number.consignment_id
            email_data['order_number'] = consignment_number.order_number.order_number
            colection_date = datetime.now()
            converted_time = colection_date.strftime("%d/%m/%Y  %I:%M %p")

            email_data['dispatch_date'] = converted_time
            email_list = []
            disposal_check = False
            collection_check = False
            customer = consignment_number.order_number.customer
            if customer.allow_to_send_mail:
                email_list.append(customer.email)
            if collection_user.allow_to_send_mail:
                email_list.append(collection_user.email)
            disposal_users = User.objects.filter(company_id=consignment_number.order_number.disposal_agency_id)
            for disposal_user in disposal_users:
                if disposal_user.allow_to_send_mail:
                    disposal_check = True
                    email_list.append(disposal_user.email)
            company_users = User.objects.filter(company_id=collection_user.company.id)
            for company_user in company_users:
                if company_user.allow_to_send_mail:
                    collection_check = True
                    email_list.append(company_user.email)
            if (collection_check or disposal_check):
                subject = "Collection Entry Created"
                try:
                    send_email(email_list, subject, **email_data)
                    logger.info("email send successfully")
                except:
                    logger.warning(
                        "smtplib.SMTPDataError: (552, b'User support@cleantrack.in has recently been created/modified, and has exceeded an hourly sending limit. Please wait, and attempt to send your message at a later time.')")
            return Response(collection_ser.data, status=status.HTTP_200_OK)
        else:
            logger.error(f"collection Entry can't Created = {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# send sms to disposal agency


class RemarkViewSet(viewsets.ModelViewSet):
    permission_classes = IsAuthenticated
    queryset = models.Consignment.objects.all()
    serializer_class = RemarkSerializer

    def get_queryset(self):
        if self.request.user.user_type == user_constants.Admin or user_constants.Verifier:
            logger.info(f"get all Remark for {self.request.user.email}")
            return models.Remark.objects.all()


@login_required(login_url='login')
def orders(request):
    context = {}
    if request.user.user_type == user_constants.Admin:
        order = models.Order.objects.all()
        context = {
            'order': order
        }
    # if request.user.user_type == user_constants.Company_Admin:
    #     order = models.Order.objects.filter(company=request.user.company_id)
    #     context = {
    #         'order': order
    #     }
    logger.info(f"Order list")
    return render(request, 'newadmin/orders.html', context)
    # FiXME:change name newadmin to appropriate and related name


@login_required(login_url='login')
def update_order(request, order_id):
    update_order = models.Order.objects.get(id=order_id)
    order_instance = OrderForm(instance=update_order)

    if request.method == 'POST':
        order_instance = OrderForm(request.POST, instance=update_order)
        if order_instance.is_valid():
            order_instance.save()
            logger.info(f"Order Number {order_id} Updated ")
            return redirect('orders')
        else:
            message = {'error': 'Invalid Data'}
            logger.error(f'Invalid data for order number {order_id}')
            return render('/', message)
    context = {
        'update_order': order_instance
    }
    return render(request, 'newadmin/order_no_entry.html', context)


@login_required(login_url='login')
def delete_order(request, del_id):
    del_order = models.Order.objects.get(id=del_id)
    del_order.delete()
    logger.info(f"Order Number {del_order.order_number} Deleted")
    return redirect('orders')


@login_required(login_url='login')
def create_order(request):
    form = OrderForm()
    context = {'form': form}
    collection_admin = None
    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        order_number = request.POST["order_number"]
        order_weight = request.POST["order_weight"]
        form_collection_company = request.POST["collection_agency"]
        form_disposal_company = request.POST["disposal_agency"]
        kwarks = {
            'order_number': order_number,
            # 'order_comment1':'This order number is assigned by disposal agency to collection agency',
            'order_comment2': 'Please directly contact the disposal agency for terms and conditions related to the order number.',
            'subheading': 'This order number is assigned by disposal agency to collection agency.',
        }
        collection_company = int(request.POST["collection_agency"])
        disposal_company = int(request.POST["disposal_agency"])
        collection_users = User.objects.filter(company_id=collection_company)
        disposal_users = User.objects.filter(company_id=disposal_company)
        print(order_form)
        email_list = []
        for collection_user in collection_users:
            if collection_user.allow_to_send_mail:
                email_list.append(collection_user.email)
        for disposal_user in disposal_users:
            if disposal_user.allow_to_send_mail:
                email_list.append(disposal_user.email)
        if order_form.is_valid():
            order_form.save()
            if email_list:
                subject = "New order Created"
                try:
                    send_email(email_list, subject, **kwarks)
                    logger.info(f"email send Successfully ")
                except:
                    logger.warning(
                        "smtplib.SMTPDataError: (552, b'User support@cleantrack.in has recently been created/modified, and has exceeded an hourly sending limit. Please wait, and attempt to send your message at a later time.')")
            else:
                logger.warning(f"Invalid Email")
            logger.info(f"Order Created")
            return redirect('orders')
        else:
            context = {'message': 'Something went wrong','errors':order_form.errors, 'form': form}
            logger.warning(f"Order already exist  ")

    return render(request, 'newadmin/add_order.html', context)


@login_required(login_url='login')
def consignments(request):
    consignment = models.Consignment.objects.all()
    content = {
        'consignment': consignment
    }
    logger.info(f"Consignment List")
    return render(request, 'newadmin/consignments.html', content)


@login_required(login_url='login')
def create_consignment(request):
    form = ConsignmentForm()
    context = {'form': form}
    if request.method == 'POST':
        consignment_form = ConsignmentForm(request.POST)
        if consignment_form.is_valid():
            consignment_form.save()
            logger.info(f"Consignment Created")
            return redirect('consignments')
        else:
            context = {'message': 'Something went wrong', 'errors': consignment_form.errors, 'form': form}
            logger.error(f"Consignment not created")
            return render(request, 'newadmin/add_consignment.html', context)
    return render(request, 'newadmin/add_consignment.html', context)


@login_required(login_url='login')
def update_consignment(request, consignment_id):
    update_consignment = models.Consignment.objects.get(id=consignment_id)
    consignment_instance = ConsignmentForm(instance=update_consignment)
    if request.method == 'POST':
        consignment_instance = ConsignmentForm(request.POST, instance=update_consignment)
        if consignment_instance.is_valid():
            consignment_instance.save()
            logger.info(f"Consignment {consignment_id} Updated ")
            return redirect('consignments')
        else:
            message = {'error': 'Invalid Data'}
            logger.error(f"Error in Updating Consignment {consignment_id}")
            return render('/', message)
    context = {
        'update_consignment': consignment_instance
    }
    return render(request, 'newadmin/consignment_entry.html', context)


@login_required(login_url='login')
def delete_consignment(request, del_id):
    del_consignment = models.Consignment.objects.get(id=del_id)
    del_consignment.delete()
    logger.info(f"Consignment {del_consignment.consignment_id} Deleted")
    return redirect('consignments')


@login_required(login_url='login')
def collections(request):
    context = {}
    if request.user.user_type == user_constants.Admin:
        collection = models.CollectionEntries.objects.all()
        context = {
            'collections': collection
        }
    if request.user.user_type == user_constants.Company_Admin:
        collection = models.CollectionEntries.objects.filter(company=request.user.company_id)
        context = {
            'collections': collection
        }
    if request.user.user_type == user_constants.Verifier:
        collection = models.CollectionEntries.objects.all()
        context = {
            'collections': collection,
        }
    logger.info(f"Collection Entry List")
    return render(request, 'newadmin/collections.html', context)


@login_required(login_url='login')
def create_collection(request):
    collection_form = CollectionEntriesForm()
    content = {"collection_form": collection_form}
    if request.method == "POST":
        collection_form = CollectionEntriesForm(request.POST, request.FILES)
        if collection_form.is_valid():
            collection_form.save()
            logger.info(f"Collection Entry Created")
            return redirect("collections")
        else:
            context = {'message': 'Something went wrong', 'errors': collection_form.errors, 'collection_form': collection_form}
            logger.error("Collection Entry Not Created")
            return render(request, 'newadmin/add_collection_disposal.html', context)
    return render(request, "newadmin/add_collection_disposal.html", content)


@login_required(login_url='login')
def update_collection(request, entry_id):
    update_collection = models.CollectionEntries.objects.get(id=entry_id)
    collection_instance = CollectionEntriesForm(instance=update_collection)
    try:
        remark = Remark.objects.get(consignment=update_collection.consignment)
    except Remark.DoesNotExist:
        remark = ''
    if request.method == 'POST':
        collection_instance = CollectionEntriesForm(request.POST, request.FILES, instance=update_collection)
        if collection_instance.is_valid():
            coll = collection_instance.save(commit=False)
            coll.dispatch_date = request.POST.get('collection_date')
            coll.save()
            if request.POST.get('remark'):
                if not remark:
                    Remark.objects.create(consignment=update_collection.consignment, remark=request.POST.get('remark'),
                                          remark_to=company_constants.collection_agency)
                else:
                    remark = Remark.objects.get(consignment=update_collection.consignment)
                    remark.remark = request.POST.get('remark')
                    remark.save()
            logger.info(f"Collection Entry Updated ")
            return redirect('collections')
        else:
            message = {'error': 'Invalid Data'}
            logger.warning("Collectoin Entry not Updated")
            return render('/', message)
    context = {
        'collection_instance': collection_instance,
        'update_collection': update_collection,
        'remark': remark,
        'dispatch_date':str(update_collection.dispatch_date)
    }
    return render(request, 'newadmin/collection&disposal_entries.html', context)


@login_required(login_url='login')
def delete_collection_entry(request, del_id):
    del_consignment = models.Consignment.objects.get(consignment_id=del_id)
    del_consignment.delete()
    logger.info(f"Collection Entry for Consignment {del_consignment.consignment_id} Deleted ")
    return redirect('collections')
