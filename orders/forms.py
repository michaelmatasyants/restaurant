from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory

from .models import Order, OrderItem


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['table_number', 'status', 'employee', 'comment']

    def __init__(self, *args, **kwargs):
        needs_status = kwargs.pop('needs_status', True)
        super().__init__(*args, **kwargs)

        if not needs_status:
            self.fields.pop('status')

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['dish', 'quantity', 'id']
    
    def clean(self):
        cleaned_data = super().clean()
        dish = cleaned_data.get('dish')
        quantity = cleaned_data.get('quantity')

        if not dish and quantity:
            raise ValidationError("Вы забыли выбрать блюдо, но указали количество.")
        if dish and not quantity:
            raise ValidationError("Укажите количество для выбранного блюда.")
        return cleaned_data

OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    extra=1,
    can_delete=True,
)

