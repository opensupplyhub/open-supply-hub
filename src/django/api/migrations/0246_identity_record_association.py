# Hand-written rather than generated. `makemigrations` on this codebase also
# proposes dropping FacilityField and FacilityListItemField, because neither is
# imported in api/models/__init__.py and so neither is in the app registry.
# That is a pre-existing condition unrelated to this change, so the operations
# below were lifted from the generated output and the rest discarded.

import django.core.validators
import django.db.models.deletion
import simple_history.models
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0245_add_claim_quality_check_switch'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalIdentityRecordAssociation',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('os_id', models.CharField(help_text='The OS ID the record is registered against. Not a foreign key: see the note in the model source.', max_length=32)),
                ('resolver_uri', models.TextField(help_text="The issuer's Resolver URI for the record. Must be an absolute HTTPS URI. Never a Credential URL, which points at one specific version and would break the always-current guarantee (FR-06).", validators=[django.core.validators.URLValidator(schemes=['https'])])),
                ('record_type', models.CharField(help_text='The type of record held at the Resolver URI, for example untp:DigitalFacilityRecord.', max_length=200)),
                ('issuer', models.CharField(help_text='Identifier of the organization that issued the record, for example a did:web value.', max_length=500)),
                ('registrant_reference', models.CharField(blank=True, help_text="The registrant's own identifier for the location, kept so they can reconcile against their register.", max_length=200)),
                ('live_from', models.DateTimeField(blank=True, help_text='When this association began resolving. Null while a registration is pending; set when it goes live. Pilot-set registrations are live on creation (Section 3.2).', null=True)),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical identity record association',
                'verbose_name_plural': 'historical identity record associations',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='IdentityRecordAssociation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Unique identifier for the association.', unique=True)),
                ('os_id', models.CharField(help_text='The OS ID the record is registered against. Not a foreign key: see the note in the model source.', max_length=32)),
                ('resolver_uri', models.TextField(help_text="The issuer's Resolver URI for the record. Must be an absolute HTTPS URI. Never a Credential URL, which points at one specific version and would break the always-current guarantee (FR-06).", validators=[django.core.validators.URLValidator(schemes=['https'])])),
                ('record_type', models.CharField(help_text='The type of record held at the Resolver URI, for example untp:DigitalFacilityRecord.', max_length=200)),
                ('issuer', models.CharField(help_text='Identifier of the organization that issued the record, for example a did:web value.', max_length=500)),
                ('registrant_reference', models.CharField(blank=True, help_text="The registrant's own identifier for the location, kept so they can reconcile against their register.", max_length=200)),
                ('live_from', models.DateTimeField(blank=True, help_text='When this association began resolving. Null while a registration is pending; set when it goes live. Pilot-set registrations are live on creation (Section 3.2).', null=True)),
                ('origin_source', models.CharField(blank=True, choices=[('os_hub', ' OS Hub'), ('rba', 'RBA')], help_text='The environment value where instance running', max_length=200, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'identity record association',
                'verbose_name_plural': 'identity record associations',
            },
        ),
        migrations.AddField(
            model_name='historicalidentityrecordassociation',
            name='history_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='identityrecordassociation',
            index=models.Index(fields=['os_id'], name='idr_assoc_os_id_idx'),
        ),
        migrations.AddConstraint(
            model_name='identityrecordassociation',
            constraint=models.UniqueConstraint(fields=('os_id', 'resolver_uri'), name='unique_os_id_resolver_uri'),
        ),
    ]
