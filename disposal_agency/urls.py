from django.urls import path

from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf import settings
from django.conf.urls.static import static
from . import views

router = routers.SimpleRouter(trailing_slash=False)

router.register(r'entries', views.DisposalEntriesViewSet),

urlpatterns = [
    path('list', views.disposals, name='disposals'),
    path('create', views.add_disposal, name='add_disposals'),
    path('update/<int:edit_id>/', views.edit_disposal, name='edit_disposals'),  # FIXME : Not appropriate all
    path('delete/<int:del_id>', views.delete_disposal, name='delete_disposal_entry'),
]
urlpatterns += format_suffix_patterns(router.urls)
