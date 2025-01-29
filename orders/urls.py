from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('<int:order_id>/delete/', views.order_delete, name='order_delete'),
    path('create/', views.order_create, name='order_create'),
    path('<int:order_id>/edit/', views.order_edit, name='order_edit'),
    path('search/', views.order_search, name='order_search'),
    path('revenue/', views.revenue_report, name='revenue_report'),
]
