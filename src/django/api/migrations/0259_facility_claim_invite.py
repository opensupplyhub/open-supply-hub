import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


SWITCH_NAME = 'claim_invite'


def create_switch(apps, schema_editor):
    Switch = apps.get_model('waffle', 'Switch')
    Switch.objects.get_or_create(
        name=SWITCH_NAME,
        defaults={'active': False},
    )


def delete_switch(apps, schema_editor):
    Switch = apps.get_model('waffle', 'Switch')
    Switch.objects.filter(name=SWITCH_NAME).delete()


class Migration(migrations.Migration):
    """
    Adds FacilityClaimInvite, which records the invites to claim a
    production location sent from its profile, links a claim to the
    invite it was submitted from, and introduces the switch that turns
    the "send them a link to claim" profile link and endpoint on or off.
    The switch is created inactive everywhere; staff enable it in the
    Django admin (Waffle > Switches).
    """

    dependencies = [
        ('api', '0253_add_earth_genome_candidates_switch'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FacilityClaimInvite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Code carried in the claim link sent with the invite.', unique=True)),
                ('recipient_email', models.EmailField(db_index=True, help_text='The email address the invite was sent to.', max_length=254)),
                ('note', models.TextField(blank=True, default='', help_text='Optional personal note from the sender, included in the email as plain text.', max_length=500)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='facilityclaiminvite',
            name='facility',
            field=models.ForeignKey(help_text='The production location the recipient is invited to claim.', on_delete=django.db.models.deletion.CASCADE, related_name='claim_invites', to='api.facility'),
        ),
        migrations.AddField(
            model_name='facilityclaiminvite',
            name='sent_by_contributor',
            field=models.ForeignKey(help_text='The contributor (organization) named as the sender in the invite email.', on_delete=django.db.models.deletion.PROTECT, to='api.contributor'),
        ),
        migrations.AddField(
            model_name='facilityclaiminvite',
            name='sent_by_user',
            field=models.ForeignKey(help_text='The user who sent the invite.', on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='facilityclaim',
            name='claim_invite',
            field=models.ForeignKey(blank=True, help_text='The invite whose claim link this claim was submitted from, if any.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='claims', to='api.facilityclaiminvite'),
        ),
        migrations.AddField(
            model_name='historicalfacilityclaim',
            name='claim_invite',
            field=models.ForeignKey(blank=True, db_constraint=False, help_text='The invite whose claim link this claim was submitted from, if any.', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='api.facilityclaiminvite'),
        ),
        migrations.RunPython(create_switch, delete_switch),
    ]
