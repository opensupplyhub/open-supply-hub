from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0136_remove_indexing_unnecessary_emails'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='facilityindex',
            name='ppe',
        ),
        migrations.RemoveField(
            model_name='facilityindex',
            name='ppe_contact_email',
        ),
        migrations.RemoveField(
            model_name='facilityindex',
            name='ppe_contact_phone',
        ),
        migrations.RemoveField(
            model_name='facilityindex',
            name='ppe_product_types',
        ),
        migrations.RemoveField(
            model_name='facilityindex',
            name='ppe_website',
        ),
        migrations.RemoveField(
            model_name='facility',
            name='ppe_contact_email',
        ),
        migrations.RemoveField(
            model_name='facility',
            name='ppe_contact_phone',
        ),
        migrations.RemoveField(
            model_name='facility',
            name='ppe_product_types',
        ),
        migrations.RemoveField(
            model_name='facility',
            name='ppe_website',
        ),
        migrations.RemoveField(
            model_name='facilitylistitem',
            name='ppe_contact_email',
        ),
        migrations.RemoveField(
            model_name='facilitylistitem',
            name='ppe_contact_phone',
        ),
        migrations.RemoveField(
            model_name='facilitylistitem',
            name='ppe_product_types',
        ),
        migrations.RemoveField(
            model_name='facilitylistitem',
            name='ppe_website',
        ),
        migrations.RemoveField(
            model_name='facilitylistitemtemp',
            name='ppe_contact_email',
        ),
        migrations.RemoveField(
            model_name='facilitylistitemtemp',
            name='ppe_contact_phone',
        ),
        migrations.RemoveField(
            model_name='facilitylistitemtemp',
            name='ppe_product_types',
        ),
        migrations.RemoveField(
            model_name='facilitylistitemtemp',
            name='ppe_website',
        ),
        migrations.RemoveField(
            model_name='historicalfacility',
            name='ppe_contact_email',
        ),
        migrations.RemoveField(
            model_name='historicalfacility',
            name='ppe_contact_phone',
        ),
        migrations.RemoveField(
            model_name='historicalfacility',
            name='ppe_product_types',
        ),
        migrations.RemoveField(
            model_name='historicalfacility',
            name='ppe_website',
        ),
    ]
