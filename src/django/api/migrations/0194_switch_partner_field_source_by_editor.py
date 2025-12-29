from django.db import migrations
import django_ckeditor_5.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0193_populate_wage_indicator_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partnerfield',
            name='source_by',
            field=django_ckeditor_5.fields.CKEditor5Field(
                blank=True,
                help_text='Rich text field describing the source of this partner field.',
                null=True,
            ),
        ),
    ]

