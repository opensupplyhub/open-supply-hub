import django_ckeditor_5.fields
from django.db import migrations, models

IS_ACTIVE_HELP = (
    'Whether the banner is currently shown on the site. The banner '
    'only appears when this is ticked and the content is not empty.'
)
CONTENT_HELP = (
    'The banner text. Formatting and links are allowed and are '
    'rendered as written.'
)


def seed_banner(apps, schema_editor):
    AnnouncementBanner = apps.get_model('api', 'AnnouncementBanner')
    if not AnnouncementBanner.objects.exists():
        AnnouncementBanner.objects.create(is_active=False, content='')


def unseed_banner(apps, schema_editor):
    AnnouncementBanner = apps.get_model('api', 'AnnouncementBanner')
    AnnouncementBanner.objects.all().delete()


class Migration(migrations.Migration):
    """
    Create the admin-managed announcement banner and seed its single row.
    See OSDEV-3723.
    """

    dependencies = [
        ('api', '0265_widen_facility_name_and_address'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnnouncementBanner',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID',
                )),
                ('is_active', models.BooleanField(
                    default=False,
                    help_text=IS_ACTIVE_HELP,
                )),
                ('content', django_ckeditor_5.fields.CKEditor5Field(
                    blank=True,
                    help_text=CONTENT_HELP,
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Announcement banner',
                'verbose_name_plural': 'Announcement banner',
            },
        ),
        migrations.RunPython(seed_banner, unseed_banner),
    ]
