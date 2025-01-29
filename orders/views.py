from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import localtime, now

from .forms import OrderForm, OrderItemFormSet
from .models import Order, OrderItem


def order_list(request):
    orders = Order.objects.fetch_total_price().prefetch_related('items__dish')
    return render(
        request,
        'order_list.html',
        {'orders': orders, 'page_title': 'Все заказы'}
    )



def order_create(request):
    if request.method == 'POST':
        form = OrderForm(request.POST, needs_status=False)
        items_formset = OrderItemFormSet(request.POST)
        if form.is_valid() and items_formset.is_valid():
            has_items = any(
                item.cleaned_data
                for item in items_formset
                if not item.cleaned_data.get('DELETE', False)
            )

            if not has_items:
                items_formset.non_form_errors = lambda: ["Добавьте хотя бы одно блюдо."]
                return render(
                    request,
                    'order_create.html',
                    {
                        'form': form,
                        'items_formset': items_formset,
                        'page_title': 'Создать новый заказ'
                    }
                )
            
            new_order = form.save(commit=False)
            new_order.status = 'pending'
            new_order.save()

            total_price = 0
            for item in items_formset.save(commit=False):
                item.price = item.dish.price
                item.order = new_order
                item.save()
                total_price += item.price * item.quantity

            new_order.total_price = total_price
            new_order.save()
            return redirect('orders:order_list')
        else:
            return render(
                request,
                'order_create.html',
                {
                    'form': form,
                    'items_formset': items_formset,
                    'page_title': 'Создать новый заказ'
                }
            )

    form = OrderForm()
    items_formset = OrderItemFormSet()
    return render(
        request,
        'order_create.html',
        {
            'form': form,
            'items_formset': items_formset,
            'page_title': 'Создать новый заказ'
        }
    )


def order_edit(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order, needs_status=True)
        items_formset = OrderItemFormSet(request.POST, instance=order)

        if form.is_valid() and items_formset.is_valid():
            has_items = any(
                item.cleaned_data
                for item in items_formset
                if not item.cleaned_data.get('DELETE', False)
            )

            if not has_items:
                items_formset.non_form_errors = lambda: [
                    "Добавьте хотя бы одно блюдо."
                ]
                return render(request, 'order_edit.html', {
                    'form': form,
                    'items_formset': items_formset,
                    'order': order
                })

            updated_order = form.save(commit=False)
            updated_order.save()

            total_price = 0
            for item in items_formset.save(commit=False):
                if not item.pk:
                    item.price = item.dish.price
                item.order = updated_order
                item.save()
                total_price += item.price * item.quantity

            items_formset.save()

            updated_order.total_price = total_price
            updated_order.save()
            return redirect('orders:order_list')
        else:
            return render(request, 'order_edit.html', {
                'form': form,
                'items_formset': items_formset,
                'order': order
            })

    form = OrderForm(instance=order)
    items_formset = OrderItemFormSet(instance=order)
    return render(request, 'order_edit.html', {
        'form': form,
        'items_formset': items_formset,
        'order': order,
        'page_title': 'Изменить заказ',
    })



def order_delete(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if request.method == 'POST':
        order.delete()
        return redirect('orders:order_list')
    return render(request, 'order_confirm_delete.html', {'order': order})


def order_search(request):
    query = request.GET.get('search', '').strip()
    orders = Order.objects.fetch_total_price().prefetch_related('items__dish')
    page_title = 'Все заказы'
    if query:
        page_title = 'Отфильтрованные заказы'
        if query.isdigit():
            orders = orders.filter(table_number=query)
        else:
            matching_statuses = [
                status_key for status_key, status_display in Order.ORDER_STATUS
                if status_display.lower().__contains__(query.lower())
            ]
            if matching_statuses:
                orders = orders.filter(status__in=matching_statuses)
            else:
                orders = orders.none()
    context = {'orders': orders,
               'search_query': query,
               'page_title': page_title}
    return render(request, 'order_list.html', context)


def revenue_report(request):
    today = localtime(now()).date()

    paid_orders = Order.objects.filter(
        status='paid',
        registered_at__date=today
    )
    total_revenue = paid_orders.aggregate(
        total=Sum(F('items__dish__price') * F('items__quantity'))
    )['total'] or 0

    dish_statistics = (
        OrderItem.objects  \
            .filter(order__status='paid', order__registered_at__date=today)
            .values('dish__name')
            .annotate(
                total_quantity=Sum('quantity'),
                total_revenue=Sum(ExpressionWrapper(
                    F('quantity') * F('dish__price'), output_field=DecimalField()
                ))
            ).order_by('-total_quantity')
    )
    context = {
        'date': today,
        'total_revenue': total_revenue,
        'dish_statistics': dish_statistics,
        'page_title': 'Выручка за смену'
    }

    return render(request, 'revenue_report.html', context)
