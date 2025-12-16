import json
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
from django.db import transaction
from django.utils import timezone
from waffle import switch_is_active

from api.constants import FacilityClaimStatuses
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
from ...models.contributor.contributor import Contributor
from ...models.extended_field import ExtendedField
from ...models.facility.facility_claim import FacilityClaim
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
from ..make_report import _report_facility_claim_email_error_to_rollbar


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

            FacilityClaimReviewNote.objects.create(
                claim=claim,
                author=request.user,
                note=message,
            )

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
                note=request.data.get('note')
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

            prev_location = claim.facility_location
            location_data = request.data.get('facility_location') or ''
            if location_data != '':
                claim.facility_location = GEOSGeometry(
                    json.dumps(location_data))
            if request.data.get('facility_address', '') == '':
                claim.facility_location = None

            parent_company_data = request.data.get('facility_parent_company')
            parent_company_name = request.data.get('parent_company_name')

            if isinstance(parent_company_data, str):
                parent_company_data = {
                    'id': None,
                    'name': parent_company_data
                }

            if parent_company_data:
                parent_company_name = (
                    parent_company_data.get('name') or parent_company_name
                )

                parent_company_id = parent_company_data.get('id')

                try:
                    parent_company = (
                        Contributor.objects.get(pk=parent_company_id)
                        if parent_company_id
                        else None
                    )
                    parent_company_name = (
                        parent_company.name
                        if parent_company
                        else parent_company_name
                    )
                except (ValueError, TypeError, Contributor.DoesNotExist):
                    parent_company = None
            else:
                parent_company = None
                parent_company_name = parent_company_name or None

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

            array_field_names = (
                'facility_affiliations',
                'facility_certifications',
                'facility_product_types',
                'facility_production_types',
                'sector',
            )
            for field_name in array_field_names:
                data = request.data.get(field_name)
                if data:
                    setattr(claim, field_name, data)
                else:
                    setattr(claim, field_name, None)

            opening_date = request.data.get('opening_date')
            closing_date = request.data.get('closing_date')

            claim.opening_date = opening_date
            claim.closing_date = closing_date
            claim.estimated_annual_throughput = request.data.get(
                'estimated_annual_throughput'
            )

            energy_field_names = (
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

            for field_name in energy_field_names:
                setattr(
                    claim,
                    field_name,
                    request.data.get(field_name),
                )

            field_names = (
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

            for field_name in field_names:
                setattr(claim, field_name, request.data.get(field_name))

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
