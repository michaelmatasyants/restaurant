from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Sum
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


# class DishCategory(models.Model):
#     name = models.CharField(verbose_name='Название',
#                             max_length=50)

#     class Meta:
#         verbose_name = 'Категория'
#         verbose_name_plural = 'Категории'

#     def __str__(self):
#         return str(self.name)


class Dish(models.Model):
    name = models.CharField(verbose_name='Название',
                            max_length=50)
    description = models.TextField(verbose_name='Описание',
                                   max_length=500,
                                   blank=True)
    price = models.DecimalField(verbose_name='Цена',
                                max_digits=8,
                                decimal_places=2,
                                validators=[MinValueValidator(0)])
    # possible improvements
    # category = models.ForeignKey(DishCategory,
    #                              verbose_name='Категория',
    #                              related_name='dishes',
    #                              null=True,
    #                              blank=True,
    #                              on_delete=models.SET_NULL)
    # image = models.ImageField(verbose_name='Картинка')

    class Meta:
        verbose_name = 'Блюдо'
        verbose_name_plural = 'Блюда'

    def __str__(self):
        return str(self.name)


class Employee(models.Model):
    full_name = models.CharField(verbose_name='ФИО сотрудника',
                                 max_length=100)
    phonenumber = PhoneNumberField(verbose_name='Телефон',
                                   region='RU',
                                   db_index=True)
    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        return str(self.full_name)


class OrderQuerySet(models.QuerySet):
    def fetch_total_price(self):
        order = self.annotate(
            price=Sum(F('items__dish__price') * F('items__quantity'))
        )
        return order


class Order(models.Model):
    ORDER_STATUS = [
        ('pending', 'в ожидании'),
        ('ready', 'готово'),
        ('paid', 'оплачено'),
    ]

    registered_at = models.DateTimeField(verbose_name='Cоздан',
                                         default=timezone.now,
                                         db_index=True)
    status = models.CharField(verbose_name='Статус заказа',
                              max_length=20,
                              db_index=True,
                              choices=ORDER_STATUS,
                              default='pending')
    table_number = models.IntegerField(verbose_name='Номер стола',
                                       db_index=True,
                                       validators=[MinValueValidator(1)])
    comment = models.TextField(verbose_name='Комментарий',
                               blank=True)
    employee = models.ForeignKey(Employee,
                                 verbose_name='Сотрудник',
                                 on_delete=models.SET_NULL,
                                 related_name='orders',
                                 null=True)
    
    # possible improvements
    # payment_type = models.CharField(verbose_name='Способ оплаты',
    #                                 default='Not specified')
    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'Заказ {self.id} для стола {self.table_number}'
    
    @classmethod
    def get_status_from_display(cls, display_value):
        """
        Convert a status display value to the corresponding internal key.
        """
        for key, display in cls.ORDER_STATUS:
            if display.lower() == display_value.lower():
                return key
        return None


class OrderItem(models.Model):
    order = models.ForeignKey(Order,
                              verbose_name='Заказ',
                              on_delete=models.CASCADE,
                              related_name='items')
    dish = models.ForeignKey(Dish,
                             verbose_name='Блюдо',
                             related_name='order_items',
                             on_delete=models.SET_NULL,
                             null=True)
    quantity = models.IntegerField(verbose_name='Количество',
                                   validators=[MinValueValidator(1)])
    price = models.DecimalField(verbose_name='Цена',
                                max_digits=8,
                                decimal_places=2,
                                validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = 'Позиция в заказе'
        verbose_name_plural = 'Позиции в заказе'

    def __str__(self):
        return f'{self.dish} - {self.quantity}'