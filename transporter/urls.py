from django.urls import path

from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

router = routers.SimpleRouter(trailing_slash=False)

router.register(r'order', views.OrderViewSet),
router.register(r'consignment', views.ConsignmentViewSet),
router.register(r'remark', views.RemarkViewSet),
router.register(r'entries', views.CollectionEntriesViewSet, basename='collection')

urlpatterns = [
    path('order/list', views.orders, name='orders'),
    path('order/create', views.create_order, name='create_order'),  # FIXME: ---||--- 'add'
    path('order/update/<int:order_id>/', views.update_order, name='update_order'),  # FIXME: ---||--- 'order/entry'
    path('order/delete/<int:del_id>', views.delete_order, name='delete_order'),
    path('consignment/list', views.consignments, name='consignments'),
    path('consignment/create', views.create_consignment, name='create_consignment'),  # FIXME: add/consignment
    path('consignment/update/<int:consignment_id>/', views.update_consignment, name='update_consignment'),
    path('consignment/delete/<int:del_id>', views.delete_consignment, name='delete_consignment'),
    path('', views.collections, name='collections'),  # FIXME: ---||--- 'entry'
    path('create', views.create_collection, name='create_collection'),
    path('update/<int:entry_id>/', views.update_collection, name='update_collection'),
    path('delete/<int:del_id>', views.delete_collection_entry, name='delete_collection_entry'),

]
urlpatterns += format_suffix_patterns(router.urls)
