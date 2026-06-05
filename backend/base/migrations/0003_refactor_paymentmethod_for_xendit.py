# Generated during the Xendit payment gateway refactor.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_cartuser_paymentmethod_orderitem_shippingaddress'),
    ]

    operations = [
        migrations.RenameField(
            model_name='paymentmethod',
            old_name='paymongopayment',
            new_name='xendit_invoice_id',
        ),
        migrations.RenameField(
            model_name='paymentmethod',
            old_name='paymongostatus',
            new_name='xendit_status',
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='xendit_external_id',
            field=models.CharField(blank=True, db_index=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='paymentmethod',
            name='xendit_invoice_id',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='paymentmethod',
            name='xendit_status',
            field=models.CharField(blank=True, default='PENDING', max_length=50),
        ),
        migrations.AlterField(
            model_name='paymentmethod',
            name='paidAt',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='shippingaddress',
            name='paymentId',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.paymentmethod'),
        ),
    ]
