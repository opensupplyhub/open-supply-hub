import django.db.models.deletion
import django.utils.timezone
import simple_history.models
import uuid
from django.conf import settings
from django.db import migrations, models


SWITCH_NAME = 'organization_level'


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
    Introduces the organization level: Organization, its memberships and
    its invitations, plus a nullable organization column on Source,
    ModerationEvent and FacilityClaim that records which organization a
    member was contributing for.

    Nothing that exists is modified. The new columns are nullable with
    no default, so adding them rewrites no rows and fires none of the
    indexing triggers; their indexes are built concurrently by the next
    migration. The organization_level switch that gates the feature is
    created inactive everywhere; staff enable it in the Django admin
    (Waffle > Switches).
    """

    dependencies = [
        ('api', '0268_index_zone_set_ids_search'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="HistoricalOrganization",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        db_index=True,
                        help_text="The name the organization is shown under to its members.",
                        max_length=200,
                    ),
                ),
                (
                    "legal_name",
                    models.CharField(
                        blank=True,
                        help_text="The legal or billing name of the organization.",
                        max_length=200,
                    ),
                ),
                (
                    "parent_entity_name",
                    models.CharField(
                        blank=True,
                        help_text="The name of the larger entity that owns the organization, if any.",
                        max_length=200,
                    ),
                ),
                (
                    "seat_limit",
                    models.PositiveIntegerField(
                        default=10,
                        help_text="The most people the organization can hold: active members plus invitations still waiting for an answer.",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Unselect to deactivate the organization instead of deleting it. Its members lose the organization views and new contributions stop being recorded against it; no data is deleted.",
                    ),
                ),
                (
                    "dashboard_enabled",
                    models.BooleanField(
                        default=False,
                        help_text="The paid organization dashboard. Select when the organization buys it and unselect when that subscription ends; no data is deleted.",
                        verbose_name="dashboard enabled",
                    ),
                ),
                (
                    "notes",
                    models.TextField(
                        blank=True, help_text="Internal notes for OS Hub staff."
                    ),
                ),
                ("created_at", models.DateTimeField(blank=True, editable=False)),
                ("updated_at", models.DateTimeField(blank=True, editable=False)),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
            ],
            options={
                "verbose_name": "historical organization",
                "verbose_name_plural": "historical organizations",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalOrganizationMembership",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[("ADMIN", "Admin"), ("MEMBER", "Member")],
                        default="MEMBER",
                        help_text="Admins manage the organization's people; Members belong to it.",
                        max_length=6,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("ACTIVE", "Active"), ("REMOVED", "Removed")],
                        default="ACTIVE",
                        help_text="Removed memberships are kept for the audit trail.",
                        max_length=7,
                    ),
                ),
                (
                    "joined_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        help_text="When the user became a member.",
                    ),
                ),
                (
                    "removed_at",
                    models.DateTimeField(
                        blank=True, help_text="When the membership ended.", null=True
                    ),
                ),
                ("created_at", models.DateTimeField(blank=True, editable=False)),
                ("updated_at", models.DateTimeField(blank=True, editable=False)),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
            ],
            options={
                "verbose_name": "historical organization membership",
                "verbose_name_plural": "historical organization memberships",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="Organization",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="Unique identifier for the organization.",
                        unique=True,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="The name the organization is shown under to its members.",
                        max_length=200,
                        unique=True,
                    ),
                ),
                (
                    "legal_name",
                    models.CharField(
                        blank=True,
                        help_text="The legal or billing name of the organization.",
                        max_length=200,
                    ),
                ),
                (
                    "parent_entity_name",
                    models.CharField(
                        blank=True,
                        help_text="The name of the larger entity that owns the organization, if any.",
                        max_length=200,
                    ),
                ),
                (
                    "seat_limit",
                    models.PositiveIntegerField(
                        default=10,
                        help_text="The most people the organization can hold: active members plus invitations still waiting for an answer.",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Unselect to deactivate the organization instead of deleting it. Its members lose the organization views and new contributions stop being recorded against it; no data is deleted.",
                    ),
                ),
                (
                    "dashboard_enabled",
                    models.BooleanField(
                        default=False,
                        help_text="The paid organization dashboard. Select when the organization buys it and unselect when that subscription ends; no data is deleted.",
                        verbose_name="dashboard enabled",
                    ),
                ),
                (
                    "notes",
                    models.TextField(
                        blank=True, help_text="Internal notes for OS Hub staff."
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="OrganizationInvitation",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="Unique identifier for the invitation.",
                        unique=True,
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        help_text="The email address the Admin entered.", max_length=254
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[("ADMIN", "Admin"), ("MEMBER", "Member")],
                        default="MEMBER",
                        help_text="The role the user gets when they accept.",
                        max_length=6,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pending"),
                            ("ACCEPTED", "Accepted"),
                            ("DECLINED", "Declined"),
                            ("REVOKED", "Revoked"),
                            ("EXPIRED", "Expired"),
                        ],
                        default="PENDING",
                        help_text="Where the invitation stands.",
                        max_length=8,
                    ),
                ),
                (
                    "expires_at",
                    models.DateTimeField(
                        help_text="After this moment the invitation can no longer be used."
                    ),
                ),
                (
                    "responded_at",
                    models.DateTimeField(
                        blank=True,
                        help_text="When the invitation was accepted, declined or revoked.",
                        null=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="OrganizationMembership",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="Unique identifier for the membership.",
                        unique=True,
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[("ADMIN", "Admin"), ("MEMBER", "Member")],
                        default="MEMBER",
                        help_text="Admins manage the organization's people; Members belong to it.",
                        max_length=6,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("ACTIVE", "Active"), ("REMOVED", "Removed")],
                        default="ACTIVE",
                        help_text="Removed memberships are kept for the audit trail.",
                        max_length=7,
                    ),
                ),
                (
                    "joined_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        help_text="When the user became a member.",
                    ),
                ),
                (
                    "removed_at",
                    models.DateTimeField(
                        blank=True, help_text="When the membership ended.", null=True
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ("joined_at",),
            },
        ),
        migrations.AddField(
            model_name="historicalorganization",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                help_text="The staff user who created the organization.",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="historicalorganization",
            name="history_user",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="historicalorganizationmembership",
            name="history_user",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="historicalorganizationmembership",
            name="invited_by",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                help_text="The user whose invitation created the membership. Empty when OS Hub staff added the member.",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="historicalorganizationmembership",
            name="removed_by",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                help_text="The user who ended the membership; the member themselves when they left.",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="historicalorganizationmembership",
            name="user",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                help_text="The existing OS Hub account that is a member.",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="organization",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                help_text="The staff user who created the organization.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="historicalorganizationmembership",
            name="organization",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                help_text="The organization the user belongs to.",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="api.organization",
            ),
        ),
        migrations.AddField(
            model_name="facilityclaim",
            name="organization",
            field=models.ForeignKey(
                blank=True,
                db_index=False,
                help_text="The organization the contributor belonged to when the claim was filed. Recorded for members only and kept when the member leaves.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="api.organization",
            ),
        ),
        migrations.AddField(
            model_name="historicalfacilityclaim",
            name="organization",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                help_text="The organization the contributor belonged to when the claim was filed. Recorded for members only and kept when the member leaves.",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="api.organization",
            ),
        ),
        migrations.AddField(
            model_name="moderationevent",
            name="organization",
            field=models.ForeignKey(
                blank=True,
                db_index=False,
                help_text="The organization the contributor belonged to when the event was submitted. Recorded for members only and kept when the member leaves.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="api.organization",
            ),
        ),
        migrations.AddField(
            model_name="source",
            name="organization",
            field=models.ForeignKey(
                blank=True,
                db_index=False,
                help_text="The organization the contributor belonged to when the data was submitted. Recorded for members only, kept when the member leaves, and never used for public attribution.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="api.organization",
            ),
        ),
        migrations.AddField(
            model_name="organizationinvitation",
            name="invited_by",
            field=models.ForeignKey(
                blank=True,
                help_text="The Admin who sent the invitation.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="organizationinvitation",
            name="invited_user",
            field=models.ForeignKey(
                help_text="The existing OS Hub account that was invited.",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="organization_invitations",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="organizationinvitation",
            name="organization",
            field=models.ForeignKey(
                help_text="The organization the user is invited to join.",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="invitations",
                to="api.organization",
            ),
        ),
        migrations.AddField(
            model_name="organizationmembership",
            name="invited_by",
            field=models.ForeignKey(
                blank=True,
                help_text="The user whose invitation created the membership. Empty when OS Hub staff added the member.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="organizationmembership",
            name="organization",
            field=models.ForeignKey(
                help_text="The organization the user belongs to.",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="memberships",
                to="api.organization",
            ),
        ),
        migrations.AddField(
            model_name="organizationmembership",
            name="removed_by",
            field=models.ForeignKey(
                blank=True,
                help_text="The user who ended the membership; the member themselves when they left.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="organizationmembership",
            name="user",
            field=models.ForeignKey(
                help_text="The existing OS Hub account that is a member.",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="organization_memberships",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddConstraint(
            model_name="organizationinvitation",
            constraint=models.UniqueConstraint(
                condition=models.Q(("status", "PENDING")),
                fields=("organization", "invited_user"),
                name="unique_pending_org_invitation_per_user",
            ),
        ),
        migrations.AddConstraint(
            model_name="organizationmembership",
            constraint=models.UniqueConstraint(
                condition=models.Q(("status", "ACTIVE")),
                fields=("user",),
                name="unique_active_org_membership_per_user",
                violation_error_message="This user already belongs to an organization.",
            ),
        ),
        migrations.RunPython(create_switch, delete_switch),
    ]
