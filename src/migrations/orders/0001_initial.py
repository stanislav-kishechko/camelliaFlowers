import django.db.models.deletion
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clients', '0001_initial'),
        ('products', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Створено')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Оновлено')),
                ('total_price', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10, verbose_name='Загальна сума')),
                ('needs_delivery', models.BooleanField(default=False, help_text='Чи потрібна доставка для цього замовлення', verbose_name='Потребує доставки')),
                ('delivery_address', models.CharField(blank=True, max_length=255, null=True, verbose_name='Адреса доставки')),
                ('delivery_date', models.DateField(blank=True, null=True, verbose_name='Дата доставки')),
                ('delivery_time', models.TimeField(blank=True, null=True, verbose_name='Час доставки')),
                ('status', models.CharField(choices=[('new', 'Нове'), ('processing', 'В обробці'), ('delivery', 'Доставка'), ('completed', 'Завершено'), ('cancelled', 'Скасовано')], default='new', max_length=20, verbose_name='Статус')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Примітки')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='clients.client', verbose_name='Клієнт')),
            ],
            options={
                'verbose_name': 'Замовлення',
                'verbose_name_plural': 'Замовлення',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Створено')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Оновлено')),
                ('quantity', models.PositiveIntegerField(default=1, verbose_name='Кількість')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Ціна за одиницю')),
                ('subtotal', models.DecimalField(decimal_places=2, editable=False, max_digits=10, verbose_name='Сума')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='orders.order', verbose_name='Замовлення')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='order_items', to='products.product', verbose_name='Продукт')),
            ],
            options={
                'verbose_name': 'Товар в замовленні',
                'verbose_name_plural': 'Товари в замовленні',
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='OrderStatusHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Створено')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Оновлено')),
                ('from_status', models.CharField(choices=[('new', 'Нове'), ('processing', 'В обробці'), ('delivery', 'Доставка'), ('completed', 'Завершено'), ('cancelled', 'Скасовано')], max_length=20, verbose_name='Попередній статус')),
                ('to_status', models.CharField(choices=[('new', 'Нове'), ('processing', 'В обробці'), ('delivery', 'Доставка'), ('completed', 'Завершено'), ('cancelled', 'Скасовано')], max_length=20, verbose_name='Новий статус')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Примітки')),
                ('changed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order_status_changes', to=settings.AUTH_USER_MODEL, verbose_name='Змінив')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='status_history', to='orders.order', verbose_name='Замовлення')),
            ],
            options={
                'verbose_name': 'Історія статусу',
                'verbose_name_plural': 'Історія статусів',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['status'], name='orders_orde_status_c6dd84_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['client'], name='orders_orde_client__7a26db_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['delivery_date'], name='orders_orde_deliver_e4274f_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['-created_at'], name='orders_orde_created_f0ce29_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['needs_delivery'], name='orders_orde_needs_d_890b51_idx'),
        ),
        migrations.AddIndex(
            model_name='orderitem',
            index=models.Index(fields=['order'], name='orders_orde_order_i_5d347b_idx'),
        ),
        migrations.AddIndex(
            model_name='orderitem',
            index=models.Index(fields=['product'], name='orders_orde_product_32ff41_idx'),
        ),
        migrations.AddIndex(
            model_name='orderstatushistory',
            index=models.Index(fields=['order', '-created_at'], name='orders_orde_order_i_ca028d_idx'),
        ),
    ]
