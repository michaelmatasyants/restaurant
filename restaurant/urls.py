from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path


def redirect_to_orders(request):
    return redirect('orders:order_list')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', redirect_to_orders, name='home'),
    path('orders/', include('orders.urls', namespace='orders'))
]
