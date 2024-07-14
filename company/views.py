from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

import random
import datetime
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework import status

from digitalplatformbackend.constants import user_constants, company_constants, company_status_constants
from .serializer import CompanySerializer
from . import models
from .forms import CompanyForm

import logging

logger = logging.getLogger(__name__)


class CompanyViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = models.Company.objects.all()
    serializer_class = CompanySerializer
    http_method_names = ['get']

    def get_queryset(self):
        # if self.request.user.user_type == user_constants.Admin or user_constants.Company_Admin:
        logger.info(f"Get All Company ")
        return models.Company.objects.all()

    # def create(self, request, *args, **kwargs):
    # #     super().create(request, *args, **kwargs)
    # #     serializer = self.serializer_class(data=request.data)
    # #     serializer.is_valid(raise_exception=True)
    # #     if self.request.user.approved_by_company_admin or self.request.user.approved_by_super_admin == False:
    # #         logger.warning(f"{self.request.user.email} is not Approve")
    # #         return Response({"error : User is not approved"}, status=status.HTTP_403_FORBIDDEN)
    #     return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@login_required(login_url='login')
def companies(request):
    context = {}
    if request.user.user_type == user_constants.Admin:
        company = models.Company.objects.all()
        context = {
            'companies': company
        }
    if request.user.user_type == user_constants.Company_Admin:
        company = models.Company.objects.filter(id=request.user.company_id)
        context = {
            'companies': company
        }
    logger.info("Company List")
    return render(request, 'newadmin/company.html', context)


@login_required(login_url='login')
def create_company(request):
    forms = CompanyForm()
    context = {'forms': forms}
    if request.method == 'POST':
        company_form = CompanyForm(request.POST)
        if company_form.is_valid():
            uniqe_id=company_form.save(commit=False)
            rand = random.randint(1000, 9999)
            datetime_var = datetime.datetime.now()
            complex_num =  datetime_var.strftime("%S")+str(int(datetime_var.strftime("%Y"))+rand)+datetime_var.strftime("%d")+str(int(datetime_var.strftime("%m"))+int(datetime_var.strftime("%H")))
            uniqe_id.id=int(complex_num)
            uniqe_id.save()
            logger.info(f"Company Created")
            return redirect('companies')
        else:
            context = {'message': 'Something went wrong', 'forms': forms}
            logger.error(f"Company Not Created")
            return render(request, 'newadmin/add_company.html', context)
    return render(request, 'newadmin/add_company.html', context)


@login_required(login_url='login')
def update_company(request, company_id):
    update_company = models.Company.objects.get(id=company_id)
    company_instance = CompanyForm(instance=update_company)

    if request.method == 'POST':
        company_instance = CompanyForm(request.POST, instance=update_company)
        if company_instance.is_valid():
            company_instance.save()
            logger.info(f"Company {company_id} Updated ")
            return redirect('companies')
        else:
            message = {'error': 'Invalid Data'}
            logger.error(f"Company Not Updated")
            return render('/', message)
    context = {
        'update_company': company_instance
    }
    return render(request, 'newadmin/company_details.html', context)


@login_required(login_url='login')
def delete_company(request, del_id):
    del_company = models.Company.objects.get(id=del_id)
    del_company.delete()
    logger.info(f"Company Deleted {del_company}")
    return redirect('companies')
