from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0171_added_origin_source_field'),
    ]

    operations = [
        migrations.CreateModel(
            name='DownloadLocationSuccessPayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_session_id', models.CharField(help_text='The unique identifier for the Stripe checkout session.', max_length=255, unique=True)),
                ('payment_id', models.CharField(help_text='The unique identifier for the payment, if available.', max_length=255, unique=True)),
                ('amount_subtotal', models.IntegerField(help_text='The subtotal amount of the payment, stored in cents.')),
                ('amount_total', models.IntegerField(help_text='The total amount of the payment, stored in cents.')),
                ('promotion_code', models.CharField(blank=True, help_text='The promotion code applied to the payment, if any.', max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
        ),
        migrations.AddField(
            model_name='downloadlocationsuccesspayment',
            name='user',
            field=models.ForeignKey(help_text='The user who made the payment.', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
