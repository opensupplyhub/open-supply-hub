import json
from datetime import datetime
from api.models.transactions.index_facilities_new import index_facilities_new

from api.helpers.helpers import validate_workers_count
from rest_framework.decorators import action
from rest_framework.exceptions import (
    NotFound,
    PermissionDenied,
    ValidationError
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.contrib.gis.geos import GEOSGeometry
from django.core.exceptions import FieldDoesNotExist
from django.db import models, transaction
from django.http import HttpResponseRedirect
from django.utils import timezone
from waffle import switch_is_active

from api.constants import (
    FacilityClaimReviewNoteTypes,
    FacilityClaimStatuses,
)
from ...exceptions import BadRequestException
from ...extended_fields import create_extendedfields_for_claim
from ...geocoding import geocode_address
from ...mail import (
    send_approved_claim_notice_to_list_contributors,
    send_claim_facility_approval_email,
    send_claim_facility_denial_email,
    send_claim_facility_revocation_email,
    send_claim_update_notice_to_list_contributors,
    send_message_to_claimant_email,
)
from ...helpers.attachment_download import generate_attachment_download_url
from ...helpers.claim_attachments import (
    create_claim_attachment,
    delete_claim_attachment,
    validate_attachment_files,
)
from ...models.contributor.contributor import Contributor
from ...models.extended_field import ExtendedField
from ...models.facility.facility_claim import FacilityClaim
from ...models.facility.facility_claim_attachments import (
    FacilityClaimAttachments
)
from ...models.facility.facility_claim_review_note import (
    FacilityClaimReviewNote
)
from ...models.facility.facility import Facility
from ...permissions import (
    IsRegisteredAndConfirmed,
    IsSuperuser
)
from ...serializers import (
    ApprovedFacilityClaimSerializer,
    FacilityClaimSerializer,
    FacilityClaimDetailsSerializer,
    FacilityClaimListQueryParamsSerializer
)
from ...serializers.facility.edit_pending_claim_serializer import (
    EditPendingClaimSerializer,
    PendingClaimSerializer,
)
from ..make_report import _report_facility_claim_email_error_to_rollbar


# Field groups the claimed-details PUT applies in bulk. get_claimed_details
# iterates these same tuples when copying request values onto the claim, so
# a field added to any group is tracked for no-op detection automatically.
CLAIM_PROFILE_ARRAY_FIELDS = (
    'facility_affiliations',
    'facility_certifications',
    'facility_product_types',
    'facility_production_types',
    'sector',
)

CLAIM_PROFILE_DATE_FIELDS = (
    'opening_date',
)

CLAIM_PROFILE_EMISSION_FIELDS = (
    'estimated_annual_throughput',
    'energy_coal',
    'energy_natural_gas',
    'energy_diesel',
    'energy_kerosene',
    'energy_biomass',
    'energy_charcoal',
    'energy_animal_waste',
    'energy_electricity',
    'energy_other',
)

CLAIM_PROFILE_SIMPLE_FIELDS = (
    'facility_description',
    'facility_name_english',
    'facility_name_native_language',
    'facility_address',
    'facility_phone_number',
    'facility_phone_number_publicly_visible',
    'facility_website',
    'facility_website_publicly_visible',
    'facility_minimum_order_quantity',
    'facility_average_lead_time',
    'point_of_contact_person_name',
    'point_of_contact_email',
    'point_of_contact_publicly_visible',
    'office_official_name',
    'office_address',
    'office_country_code',
    'office_phone_number',
    'office_info_publicly_visible',
)

# Fields get_claimed_details assigns individually rather than through the
# group loops above. A new individually-assigned field must be added here
# by hand, or edits touching only that field would be dropped as "no-op".
CLAIM_PROFILE_INDIVIDUAL_FIELDS = (
    'parent_company_id',
    'parent_company_name',
    'facility_workers_count',
    'facility_female_workers_percentage',
    'facility_type',
    'other_facility_type',
    'facility_location',
)

# Every claim field the claimed-details PUT can modify. Used to detect
# no-op saves: an unconditional save bumps updated_at even when nothing
# changed, which pollutes the claimed section's "last updated" date and
# makes claim-data recency untrustworthy across channels.
CLAIM_PROFILE_TRACKED_FIELDS = (
    CLAIM_PROFILE_INDIVIDUAL_FIELDS
    + CLAIM_PROFILE_ARRAY_FIELDS
    + CLAIM_PROFILE_DATE_FIELDS
    + CLAIM_PROFILE_EMISSION_FIELDS
    + CLAIM_PROFILE_SIMPLE_FIELDS
)


def get_tracked_claim_value(claim, field_name):
    """Return the claim field value normalized through the model field's
    to_python, so raw request values (e.g. the string "False" from a form
    submit) compare equal to their saved database representation.

    Text fields additionally treat NULL and the empty string as the same
    value. They are distinct in the database but identical everywhere a
    user can see them, and the claim form submits '' for every field left
    blank — so without this, the first save of a claim holding NULLs
    counts as a change and bumps updated_at without altering anything
    visible. Most approved claims carry such NULLs, so nearly every
    claimant would have seen one unexplained "last updated" bump.

    Deliberately keyed on field type rather than name: the visibility
    booleans in CLAIM_PROFILE_SIMPLE_FIELDS keep NULL and False distinct,
    since those genuinely differ (unanswered vs. answered "no").
    """
    value = getattr(claim, field_name)
    try:
        model_field = claim._meta.get_field(field_name)
    except FieldDoesNotExist:
        # Attname-only entries such as parent_company_id.
        return value
    try:
        value = model_field.to_python(value)
    except Exception:
        return value
    if isinstance(model_field, (models.CharField, models.TextField)):
        return '' if value is None else value
    return value


class FacilityClaimViewSet(ModelViewSet):
    """
    Viewset for admin operations on FacilityClaims.
    """
    queryset = FacilityClaim.objects.select_related(
        'facility',
        'contributor',
        'contributor__admin',
        'status_change_by'
    ).all()
    serializer_class = FacilityClaimSerializer
    permission_classes = [IsSuperuser]
    swagger_schema = None
    throttle_classes = []

    def create(self, request):
        pass

    def delete(self, request):
        pass

    def list(self, request):
        params = FacilityClaimListQueryParamsSerializer(
            data=self.request.query_params
        )
        if not params.is_valid():
            raise ValidationError(params.errors)

        statuses = params.validated_data.get('statuses')
        countries = params.validated_data.get('countries')

        queryset = FacilityClaim.objects.select_related(
            'facility',
            'contributor',
            'contributor__admin',
            'status_change_by'
        ).all().order_by('-id')
        if statuses:
            queryset = queryset.filter(status__in=statuses)
        if countries:
            queryset = queryset.filter(facility__country_code__in=countries)

        response_data = FacilityClaimSerializer(queryset, many=True).data

        return Response(response_data)

    def retrieve(self, request, pk=None):
        if not switch_is_active('claim_a_facility'):
            raise NotFound()

        try:
            claim = FacilityClaim.objects.get(pk=pk)
            response_data = FacilityClaimDetailsSerializer(claim).data

            return Response(response_data)
        except FacilityClaim.DoesNotExist as exc:
            raise NotFound() from exc

    @transaction.atomic
    @action(detail=True,
            methods=['post'],
            url_path='message-claimant')
    def message_claimant(self, request, pk=None):
        if not request.user.is_superuser:
            raise PermissionDenied()

        try:
            claim = FacilityClaim.objects.get(pk=pk)
            message = request.data.get('message', '')

            if not message:
                raise BadRequestException('Message is required.')

            # Creates the CLAIMANT_MESSAGE review note and sends the
            # email as one unit (see mail.py) — @transaction.atomic
            # rolls the note back if the send fails.
            send_message_to_claimant_email(request, claim, message)

            response_data = FacilityClaimDetailsSerializer(claim).data
            return Response(response_data)
        except FacilityClaim.DoesNotExist as exc:
            raise NotFound() from exc

    @transaction.atomic
    @action(detail=True,
            methods=['post'],
            url_path='approve')
    def approve_claim(self, request, pk=None):
        if not switch_is_active('claim_a_facility'):
            raise NotFound()

        if not request.user.is_superuser:
            raise PermissionDenied()

        try:
            claim = FacilityClaim.objects.get(pk=pk)

            if claim.status != FacilityClaimStatuses.PENDING:
                raise BadRequestException(
                    'Only PENDING claims can be approved.',
                )

            approved_claims_for_facility_count = (
                FacilityClaim
                .objects
                .filter(status=FacilityClaimStatuses.APPROVED)
                .filter(facility=claim.facility)
                .count()
            )
            if approved_claims_for_facility_count > 0:
                raise BadRequestException(
                    'A facility may have at most one approved facility claim'
                )

            claim.status_change_reason = request.data.get('reason', '')
            claim.status_change_by = request.user
            claim.status_change_date = timezone.now()
            claim.status = FacilityClaimStatuses.APPROVED
            claim.save()
            Facility.update_facility_updated_at_field(claim.facility_id)

            note = (
                f'Status was updated to {FacilityClaimStatuses.APPROVED} '
                f'for reason: {claim.status_change_reason}'
            )

            FacilityClaimReviewNote.objects.create(
                claim=claim,
                author=request.user,
                note=note,
            )

            send_claim_facility_approval_email(request, claim)
            create_extendedfields_for_claim(claim)

            try:
                send_approved_claim_notice_to_list_contributors(request,
                                                                claim)
            except Exception:
                _report_facility_claim_email_error_to_rollbar(claim)

            response_data = FacilityClaimDetailsSerializer(claim).data
            return Response(response_data)
        except FacilityClaim.DoesNotExist as exc:
            raise NotFound() from exc

    @transaction.atomic
    @action(detail=True,
            methods=['post'],
            url_path='deny')
    def deny_claim(self, request, pk=None):
        if not switch_is_active('claim_a_facility'):
            raise NotFound()

        if not request.user.is_superuser:
            raise PermissionDenied()

        try:
            claim = FacilityClaim.objects.get(pk=pk)

            if claim.status != FacilityClaimStatuses.PENDING:
                raise BadRequestException(
                    'Only PENDING claims can be denied.',
                )

            claim.status_change_reason = request.data.get('reason', '')
            claim.status_change_by = request.user
            claim.status_change_date = timezone.now()
            claim.status = FacilityClaimStatuses.DENIED
            claim.save()
            Facility.update_facility_updated_at_field(claim.facility_id)

            note = (
                f'Status was updated to {FacilityClaimStatuses.DENIED} '
                f'for reason: {claim.status_change_reason}'
            )

            FacilityClaimReviewNote.objects.create(
                claim=claim,
                author=request.user,
                note=note,
            )

            send_claim_facility_denial_email(request, claim)

            response_data = FacilityClaimDetailsSerializer(claim).data
            return Response(response_data)
        except FacilityClaim.DoesNotExist as exc:
            raise NotFound() from exc

    @transaction.atomic
    @action(detail=True,
            methods=['post'],
            url_path='revoke')
    def revoke_claim(self, request, pk=None):
        if not switch_is_active('claim_a_facility'):
            raise NotFound()

        if not request.user.is_superuser:
            raise PermissionDenied()

        try:
            claim = FacilityClaim.objects.get(pk=pk)

            if claim.status != FacilityClaimStatuses.APPROVED:
                raise BadRequestException(
                    'Only APPROVED claims can be revoked.',
                )

            claim.status_change_reason = request.data.get('reason', '')
            claim.status_change_by = request.user
            claim.status_change_date = timezone.now()
            claim.status = FacilityClaimStatuses.REVOKED
            claim.save()
            Facility.update_facility_updated_at_field(claim.facility_id)

            note = (
                f'Status was updated to {FacilityClaimStatuses.REVOKED} '
                f'for reason: {claim.status_change_reason}'
            )

            FacilityClaimReviewNote.objects.create(
                claim=claim,
                author=request.user,
                note=note,
            )

            send_claim_facility_revocation_email(request, claim)

            ExtendedField.objects.filter(facility_claim=claim).delete()
            index_facilities_new([claim.facility_id])

            response_data = FacilityClaimDetailsSerializer(claim).data
            return Response(response_data)
        except FacilityClaim.DoesNotExist as exc:
            raise NotFound() from exc

    @transaction.atomic
    @action(detail=True,
            methods=['post'],
            url_path='note')
    def add_note(self, request, pk=None):
        if not switch_is_active('claim_a_facility'):
            raise NotFound()

        if not request.user.is_superuser:
            raise PermissionDenied()

        try:
            claim = FacilityClaim.objects.get(pk=pk)

            FacilityClaimReviewNote.objects.create(
                claim=claim,
                author=request.user,
                note=request.data.get('note'),
                note_type=FacilityClaimReviewNoteTypes.INTERNAL,
            )

            response_data = FacilityClaimDetailsSerializer(claim).data
            return Response(response_data)
        except FacilityClaim.DoesNotExist as exc:
            raise NotFound() from exc

    @transaction.atomic
    @action(detail=True,
            methods=['GET', 'PUT'],
            url_path='claimed',
            permission_classes=(IsRegisteredAndConfirmed,))
    def get_claimed_details(self, request, pk=None):
        if not switch_is_active('claim_a_facility'):
            raise NotFound()

        try:
            claim = (
                FacilityClaim
                .objects
                .filter(contributor=request.user.contributor)
                .filter(status=FacilityClaimStatuses.APPROVED)
                .get(pk=pk)
            )
            if request.user.contributor != claim.contributor:
                raise NotFound()

            if request.method == 'GET':
                response_data = ApprovedFacilityClaimSerializer(claim).data
                return Response(response_data)

            snapshot = {
                field: get_tracked_claim_value(claim, field)
                for field in CLAIM_PROFILE_TRACKED_FIELDS
            }

            prev_location = claim.facility_location
            location_data = request.data.get('facility_location') or ''
            if location_data != '':
                claim.facility_location = GEOSGeometry(
                    json.dumps(location_data))
            if request.data.get('facility_address', '') == '':
                claim.facility_location = None

            parent_company_data = request.data.get('facility_parent_company')

            if not parent_company_data:
                parent_company = None
                parent_company_name = None
            elif 'id' not in parent_company_data:
                parent_company = None
                parent_company_name = None
            else:
                try:
                    parent_company = (
                        Contributor
                        .objects
                        .get(pk=parent_company_data['id'])
                    )
                    parent_company_name = parent_company.name
                except ValueError:
                    parent_company = None
                    parent_company_name = parent_company_data['name']

            claim.parent_company = parent_company
            claim.parent_company_name = parent_company_name

            try:
                workers_count = request.data.get('facility_workers_count')

                if len(workers_count) == 0:
                    workers_count = None
                elif not validate_workers_count(workers_count):
                    workers_count = None

            except (ValueError, TypeError):
                workers_count = None

            claim.facility_workers_count = workers_count

            try:
                female_workers_percentage = int(
                    request.data.get('facility_female_workers_percentage')
                )
            except ValueError:
                female_workers_percentage = None
            except TypeError:
                female_workers_percentage = None

            claim.facility_female_workers_percentage = (
                female_workers_percentage
            )

            facility_type = request.data.get('facility_type')

            claim.facility_type = facility_type

            if facility_type == FacilityClaim.OTHER:
                other_facility_type = request.data.get('other_facility_type')
            else:
                other_facility_type = None
            claim.other_facility_type = other_facility_type

            for field_name in CLAIM_PROFILE_ARRAY_FIELDS:
                data = request.data.get(field_name)
                if data:
                    setattr(claim, field_name, data)
                else:
                    setattr(claim, field_name, None)

            for date_field in CLAIM_PROFILE_DATE_FIELDS:
                value = request.data.get(date_field)

                if not value:
                    setattr(claim, date_field, None)
                    continue

                try:
                    setattr(
                        claim,
                        date_field,
                        datetime.fromisoformat(value).date(),
                    )
                except (ValueError, TypeError):
                    setattr(claim, date_field, None)

            for field_name in CLAIM_PROFILE_EMISSION_FIELDS:
                value = request.data.get(field_name, None)

                if not value:
                    setattr(claim, field_name, None)
                    continue

                try:
                    setattr(claim, field_name, int(value))
                except (ValueError, TypeError):
                    setattr(claim, field_name, None)

            for field_name in CLAIM_PROFILE_SIMPLE_FIELDS:
                setattr(claim, field_name, request.data.get(field_name))

            # Skip the save (and its side effects: updated_at bump, claim
            # reindex trigger, extended-field rebuild, notification email)
            # when no tracked value actually changed.
            has_changes = any(
                snapshot[field] != get_tracked_claim_value(claim, field)
                for field in CLAIM_PROFILE_TRACKED_FIELDS
            )
            if not has_changes:
                response_data = ApprovedFacilityClaimSerializer(claim).data
                return Response(response_data)

            claim.save()
            Facility.update_facility_updated_at_field(claim.facility_id)

            create_extendedfields_for_claim(claim)

            # Conditionally update the facility location if it was changed on
            # the approved claim. If the location was removed from the claim we
            # revert the location.
            if claim.facility_location is not None:
                if prev_location != claim.facility_location:
                    claim.facility.location = claim.facility_location
                    claim.facility._change_reason = \
                        'Location updated on FacilityClaim ({})'.format(
                            claim.id)
                    claim.facility.save()
            else:
                if prev_location is not None:
                    claim.facility.location = \
                        claim.facility.created_from.geocoded_point
                    claim.facility._change_reason = (
                        'Reverted location to created_from after clearing '
                        'claim location'
                    )
                    claim.facility.save()

            # No explicit reindex needed here: the DB trigger
            # facility_claim_post_update_insert_indexing_trigger fires on the
            # claim UPDATE and refreshes the claim-derived FacilityIndex
            # columns (including claim_info) via
            # perform_facility_claim_indexing. See OSDEV-2679.

            try:
                send_claim_update_notice_to_list_contributors(request, claim)
            except Exception:
                _report_facility_claim_email_error_to_rollbar(claim)

            response_data = ApprovedFacilityClaimSerializer(claim).data
            return Response(response_data)
        except FacilityClaim.DoesNotExist as exc:
            raise NotFound() from exc
        except Contributor.DoesNotExist as exc:
            raise NotFound('No contributor found for that user') from exc

    @action(detail=True,
            methods=['get'],
            url_path='geocode',
            permission_classes=(IsRegisteredAndConfirmed,))
    def geocode_claim_address(self, request, pk=None):
        """
        Reduce the potential misuse of the server-side geocoder by requiring
        that geocode requests are made by an account with an approved claim.
        """
        claim = (
            FacilityClaim
            .objects
            .filter(contributor=request.user.contributor)
            .filter(status=FacilityClaimStatuses.APPROVED)
            .get(pk=pk)
        )
        if request.user.contributor != claim.contributor:
            raise NotFound()

        country_code = request.query_params.get('country_code', None)
        if country_code is None:
            country_code = claim.facility.country_code

        address = request.query_params.get('address', None)
        if address is None:
            raise BadRequestException('Missing address')

        geocode_result = geocode_address(address, country_code)
        return Response(geocode_result)

    def __get_owned_pending_claim(self, request, pk):
        """
        Fetch a claim the requesting user may edit: they are its
        contributor and it is still PENDING. Anything else — including
        a claim that exists but belongs to someone else or has been
        decided — is a 404, so the endpoint does not leak which claim
        ids exist.
        """
        try:
            return FacilityClaim.objects.get(
                pk=pk,
                contributor=request.user.contributor,
                status=FacilityClaimStatuses.PENDING,
            )
        except (FacilityClaim.DoesNotExist, Contributor.DoesNotExist) as exc:
            raise NotFound() from exc

    @transaction.atomic
    @action(detail=True,
            methods=['GET', 'PATCH'],
            url_path='pending',
            permission_classes=(IsRegisteredAndConfirmed,))
    def pending(self, request, pk=None):
        """
        Claimant-facing view (GET) and edit (PATCH) of their own
        PENDING claim. OSDEV-3370. PATCH accepts any subset of the
        claim form's fields; validation is shared with claim creation
        via EditPendingClaimSerializer. Attachments are managed through
        the attachments sub-resource, not here.
        """
        if not switch_is_active('claim_a_facility'):
            raise NotFound()

        claim = self.__get_owned_pending_claim(request, pk)

        if request.method == 'GET':
            return Response(PendingClaimSerializer(claim).data)

        serializer = EditPendingClaimSerializer(
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        changed_fields = serializer.apply_to_claim(claim)
        if changed_fields:
            # simple-history records this save with history_user set to
            # the claimant via HistoryRequestMiddleware, which is what
            # lets moderators see exactly what the claimant changed.
            claim.save()

        return Response(PendingClaimSerializer(claim).data)

    @transaction.atomic
    @action(detail=True,
            methods=['POST'],
            url_path='attachments',
            permission_classes=(IsRegisteredAndConfirmed,))
    def add_attachments(self, request, pk=None):
        """
        Add attachment files to the requesting claimant's own PENDING
        claim. The MAX_ATTACHMENT_AMOUNT cap applies to the claim's
        lifetime total (submission plus edits), not per request.
        """
        if not switch_is_active('claim_a_facility'):
            raise NotFound()

        files = request.FILES.getlist('files')
        if not files:
            raise BadRequestException('No files submitted.')

        claim = self.__get_owned_pending_claim(request, pk)
        
        existing_count = FacilityClaimAttachments.objects.filter(
            claim=claim
        ).count()
        validate_attachment_files(files, existing_count=existing_count)

        for file in files:
            create_claim_attachment(file, claim)

        return Response(PendingClaimSerializer(claim).data)

    @transaction.atomic
    @action(detail=True,
            methods=['DELETE'],
            url_path=r'attachments/(?P<attachment_pk>[0-9]+)',
            permission_classes=(IsRegisteredAndConfirmed,))
    def delete_attachment(self, request, pk=None, attachment_pk=None):
        """
        Remove one attachment from the requesting claimant's own
        PENDING claim. Deletes the database row and the stored file
        together (file cleanup runs in the post_delete signal).
        """
        if not switch_is_active('claim_a_facility'):
            raise NotFound()

        claim = self.__get_owned_pending_claim(request, pk)

        try:
            attachment = FacilityClaimAttachments.objects.get(
                pk=attachment_pk,
                claim=claim,
            )
        except FacilityClaimAttachments.DoesNotExist as exc:
            raise NotFound() from exc

        delete_claim_attachment(attachment)

        return Response(PendingClaimSerializer(claim).data)

    @action(detail=True,
            methods=['GET'],
            url_path=r'attachments/(?P<attachment_pk>[0-9]+)/download',
            permission_classes=(IsRegisteredAndConfirmed,))
    def download_attachment(self, request, pk=None, attachment_pk=None):
        """
        Authorization-checked attachment download: the claim's own
        contributor or a superuser (moderator), nobody else. Responds
        with a 302 redirect to a presigned URL that is valid for 60
        seconds and scoped to this single object, minted by the
        dedicated signing role. Raw storage URLs are not exposed
        anywhere else in the API.
        """
        if not switch_is_active('claim_a_facility'):
            raise NotFound()

        try:
            attachment = FacilityClaimAttachments.objects.select_related(
                'claim'
            ).get(pk=attachment_pk, claim_id=pk)
        except FacilityClaimAttachments.DoesNotExist as exc:
            raise NotFound() from exc

        is_moderator = request.user.is_superuser
        if not is_moderator:
            try:
                is_owner = (
                    attachment.claim.contributor
                    == request.user.contributor
                )
            except Contributor.DoesNotExist as exc:
                raise NotFound() from exc
            if not is_owner:
                # 404, not 403: no existence leak.
                raise NotFound()

        if not attachment.claim_attachment:
            raise NotFound()

        url = generate_attachment_download_url(attachment)
        return HttpResponseRedirect(url)
