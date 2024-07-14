from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns

from django.urls import path

from . import views

router = routers.SimpleRouter(trailing_slash=False)

router.register('user', views.UserViewSet, basename='user'),
# router.register('otp', views.OtpView, basename='otp'),

urlpatterns = [
    path('user/details', views.user_details),
    path('', views.dashboard, name='dashboard'),
    path('list/', views.user, name='user'),
    path('create/', views.create_user, name='create_user'),
    path('update/<int:user_id>/', views.update_user, name='update_user'),
    path('delete/<int:del_id>/', views.delete_user, name='delete_user'),
    # path('admin-panel', views.home, name='home'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('otp/', views.OtpView.as_view(), name='otp'),
    path('forgot_password/', views.ForgotPassword.as_view(), name='forgot_password'),
    path('orders', views.CustomersOrder.as_view(), name='customer_order'),
    path('review/<int:id>/', views.review, name='review'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('report_download/', views.report_dashboard, name='report_dashboard'),
    # path('otp/', views.otp, name='otp'),
    path('customer/list', views.customer_data, name='customer_list'),
    path('reset_otp', views.reset_otp, name='reset_otp'),
    path('reset/password', views.reset_password, name='reset_password'),
    path('privacy/policy', views.privacy_policy, name='privacy_policy')


    # report generate
    # path('report_generate/', views.report_generate, name='report_generate')
]
urlpatterns += format_suffix_patterns(router.urls)
