from django.db import migrations, models
import uuid
from api.models.partner_field import TYPES

class Migration(migrations.Migration):
    """
    Migration to create PartnerField model and add partner_fields ManyToManyField to Contributor model.
    """

    dependencies = [
        ('api', '0176_introduce_enable_dromo_uploading_switch'),
    ]

    operations = [
        migrations.CreateModel(
            name='PartnerField',
            fields=[
                ('name', models.CharField(help_text='The partner field name.', max_length=200, primary_key=True, serialize=False)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Unique identifier for the partner field.', unique=True)),
                ('type', models.CharField(help_text='The partner field type.', max_length=200, blank=False, null=False, choices=[('int','int'),('float','float'),('string','string'),('object','object')])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'partner field',
            },
        ),

        migrations.AddField(
            model_name='contributor',
            name='partner_fields',
            field=models.ManyToManyField(
                blank=True,
                help_text='Partner fields that this contributor can access',
                to='api.partnerfield'
            ),
        ),
    ]
