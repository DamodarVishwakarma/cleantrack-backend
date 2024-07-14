from django.urls import path

from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns

from . import views
from .report_generation import generate_customer_reports

router = routers.SimpleRouter(trailing_slash=False)

router.register(r'', views.CompanyViewSet)

urlpatterns = [
    path('list/', views.companies, name='companies'),  # FIXME : change name from companys to company or companies
    path('create', views.create_company, name='create_company'),
    path('update/<int:company_id>/', views.update_company, name='update_company'),
    path('delete/<int:del_id>', views.delete_company, name='delete_company'),
    # FIXME : change name company/edit-company/id, use 'edit' or anything else instead of 'edit-company'
    path('report/', generate_customer_reports, name='report'),
]
urlpatterns += format_suffix_patterns(router.urls)
