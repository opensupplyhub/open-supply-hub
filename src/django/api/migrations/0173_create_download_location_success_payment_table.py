from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0172_add_facility_download_limit'),
    ]

    operations = [
        migrations.CreateModel(
            name='DownloadLocationPayment',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'stripe_session_id',
                    models.CharField(
                        help_text='The unique identifier for the Stripe checkout session.',
                        max_length=255,
                        unique=True,
                    ),
                ),
                (
                    'payment_id',
                    models.CharField(
                        help_text='The unique identifier for the payment, if available.',
                        max_length=255,
                        unique=True,
                    ),
                ),
                (
                    'amount_subtotal',
                    models.IntegerField(
                        help_text='The subtotal amount of the payment, stored in cents.'
                    ),
                ),
                (
                    'amount_total',
                    models.IntegerField(
                        help_text='The total amount of the payment, stored in cents.'
                    ),
                ),
                (
                    'discounts',
                    models.JSONField(
                        blank=True,
                        default=list,
                        help_text='List of discount objects applied to the payment, each containing coupon and promotion_code.',
                    ),
                ),
                (
                    'created_at',
                    models.DateTimeField(auto_now_add=True, db_index=True),
                ),
            ],
        ),
        migrations.AddField(
            model_name='downloadlocationpayment',
            name='user',
            field=models.ForeignKey(
                help_text='The user who made the payment.',
                on_delete=models.deletion.CASCADE,
                related_name='download_location_payments',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
