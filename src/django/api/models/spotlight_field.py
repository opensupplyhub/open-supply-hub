import re

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone
from simple_history.models import HistoricalRecords

NAME_MAX_LENGTH = 50
NAME_PATTERN = re.compile(r'^[a-z][a-z0-9_]*$')
NAME_RULES = (
    'Use only lowercase letters, numbers and underscores, start with a '
    'letter, and keep it to 50 characters or fewer (for example '
    '"certification_status").'
)
DISPLAY_NAME_RULES = 'Keep the display name to 50 characters or fewer.'


def validate_internal_name(value):
    """
    Reject internal names that are not lowercase-with-underscores.

    The error message tells the partner exactly what the rule is, because it
    is shown to them in the dashboard form.
    """
    if not value or len(value) > NAME_MAX_LENGTH \
            or not NAME_PATTERN.match(value):
        raise ValidationError(f'Invalid internal name. {NAME_RULES}')


class SpotlightField(models.Model):
    """
    One per Spotlight partner. Wraps the partner's single object-type
    `PartnerField` and holds the settings shared by every property inside it,
    such as the go-live date.
    """

    contributor = models.OneToOneField(
        'Contributor',
        on_delete=models.CASCADE,
        related_name='spotlight_field',
        help_text='The Spotlight partner who owns these fields.',
    )
    partner_field = models.OneToOneField(
        'PartnerField',
        on_delete=models.PROTECT,
        related_name='spotlight_field',
        help_text='The object-type partner field the properties live in.',
    )
    go_live_date = models.DateField(
        null=True,
        blank=True,
        help_text=(
            'Until this date the partner cannot activate fields. On this '
            'date every approved field is switched on automatically. '
            'Leave blank for no date. Changing it may deactivate fields '
            'that are currently active.'
        ),
    )
    go_live_applied = models.BooleanField(
        default=False,
        help_text='Set once the go-live date has switched the fields on.',
    )
    last_partner_edit_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text='When the partner last edited one of these fields.',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Spotlight field set'
        verbose_name_plural = 'Spotlight field sets'

    def __str__(self):
        return f'Spotlight fields for {self.contributor.name}'

    @property
    def go_live_pending(self):
        """True while a go-live date is set and has not arrived yet."""
        return (
            self.go_live_date is not None
            and self.go_live_date > timezone.localdate()
        )

    @classmethod
    def get_or_create_for(cls, contributor):
        """
        Return the contributor's field set, creating the object-type
        `PartnerField` and linking it to the contributor the first time.
        """
        from api.models.partner_field import PartnerField

        existing = cls.objects.filter(contributor=contributor).first()
        if existing is not None:
            return existing

        with transaction.atomic():
            partner_field = PartnerField.objects.create(
                name=f'spotlight_partner_{contributor.id}',
                type=PartnerField.OBJECT,
                label=contributor.name,
                json_schema={'type': 'object', 'properties': {}},
            )
            contributor.partner_fields.add(partner_field)
            return cls.objects.create(
                contributor=contributor, partner_field=partner_field
            )

    def sync_partner_field(self):
        """
        Rewrite the partner field's JSON schema from the properties so the
        JSON always holds each field's names plus its approved and active
        state.
        """
        properties = {}
        for prop in self.properties.order_by('id'):
            properties[prop.name] = {
                'title': prop.display_name,
                'approved': prop.approved,
                'active': prop.active,
            }
        schema = dict(self.partner_field.json_schema or {})
        schema['type'] = 'object'
        schema['properties'] = properties
        self.partner_field.json_schema = schema
        self.partner_field.save()

    def set_go_live_date(self, new_date, user=None):
        """
        Change the go-live date. Moving it into the future deactivates every
        field that is currently active, because partners cannot hold fields
        active before the date. Fields are reapplied when the date arrives.
        """
        with transaction.atomic():
            self.go_live_date = new_date
            self.go_live_applied = False
            self.save()
            if self.go_live_pending:
                for prop in self.properties.filter(active=True):
                    prop.active = False
                    prop._history_user = user
                    prop.save(sync=False)
                self.sync_partner_field()
            else:
                self.apply_go_live(user=user)

    def apply_go_live(self, user=None):
        """
        Switch every approved field on once the date has arrived. Runs only
        once per date, so a partner who later turns a field off is not
        overridden.
        """
        if self.go_live_applied or self.go_live_date is None \
                or self.go_live_pending:
            return 0
        count = 0
        with transaction.atomic():
            for prop in self.properties.filter(approved=True, active=False):
                prop.active = True
                prop._history_user = user
                prop.save(sync=False)
                count += 1
            self.go_live_applied = True
            self.save()
            self.sync_partner_field()
        return count


class SpotlightFieldProperty(models.Model):
    """
    A single field inside a partner's object-type partner field. Every change
    is recorded in the history table (who, when, old and new values).
    """

    spotlight_field = models.ForeignKey(
        SpotlightField,
        on_delete=models.CASCADE,
        related_name='properties',
    )
    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        validators=[validate_internal_name],
        help_text=f'Internal name. Cannot change once saved. {NAME_RULES}',
    )
    display_name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        help_text=f'Name shown on OS Hub. {DISPLAY_NAME_RULES}',
    )
    approved = models.BooleanField(
        default=False,
        help_text='New fields need admin approval before they can be active.',
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        'User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    active = models.BooleanField(
        default=False,
        help_text='Inactive fields appear nowhere on the site.',
    )
    last_partner_edit_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    class Meta:
        unique_together = ('spotlight_field', 'name')
        ordering = ('id',)
        verbose_name = 'Spotlight field'
        verbose_name_plural = 'Spotlight fields'

    def __str__(self):
        return f'{self.display_name} ({self.name})'

    def clean(self):
        super().clean()
        if self.active and not self.approved:
            raise ValidationError(
                'A field must be approved by an admin before it can be '
                'active.'
            )
        if self.pk is not None:
            original = SpotlightFieldProperty.objects.filter(
                pk=self.pk
            ).first()
            if original is not None and original.name != self.name:
                raise ValidationError(
                    'The internal name cannot be changed once saved.'
                )

    def save(self, *args, sync=True, **kwargs):
        """Save, then keep the partner field's JSON in step."""
        if self.pk is not None:
            original = SpotlightFieldProperty.objects.filter(
                pk=self.pk
            ).first()
            if original is not None and original.name != self.name:
                raise ValidationError(
                    'The internal name cannot be changed once saved.'
                )
        if self.active and not self.approved:
            raise ValidationError(
                'A field must be approved by an admin before it can be '
                'active.'
            )
        result = super().save(*args, **kwargs)
        if sync:
            self.spotlight_field.sync_partner_field()
        return result

    def delete(self, *args, **kwargs):
        raise ValidationError('Spotlight fields cannot be deleted.')

    def approve(self, user, activate=False):
        """Approve the field, optionally switching it on straight away."""
        self.approved = True
        self.approved_at = timezone.now()
        self.approved_by = user
        if activate:
            self.active = True
        self._history_user = user
        self.save()

    def set_active(self, active, user, *, is_admin):
        """
        Switch the field on or off. Partners are blocked from switching a
        field on while a go-live date is pending; admins are not.
        """
        if active and not self.approved:
            raise ValidationError(
                'This field has not been approved yet. It can be switched '
                'on once an admin approves it.'
            )
        if active and not is_admin and self.spotlight_field.go_live_pending:
            raise ValidationError(
                'Your fields go live on '
                f'{self.spotlight_field.go_live_date:%B %-d, %Y}. You can '
                'switch them on yourself after that date.'
            )
        self.active = active
        self._history_user = user
        if not is_admin:
            self._mark_partner_edit()
        self.save()

    def update_display_name(self, display_name, user, *, is_admin):
        """Rename how the field appears. The internal name never changes."""
        display_name = (display_name or '').strip()
        if not display_name or len(display_name) > NAME_MAX_LENGTH:
            raise ValidationError(
                f'Invalid display name. {DISPLAY_NAME_RULES}'
            )
        self.display_name = display_name
        self._history_user = user
        if not is_admin:
            self._mark_partner_edit()
        self.save()

    def _mark_partner_edit(self):
        now = timezone.now()
        self.last_partner_edit_at = now
        SpotlightField.objects.filter(pk=self.spotlight_field_id).update(
            last_partner_edit_at=now
        )
