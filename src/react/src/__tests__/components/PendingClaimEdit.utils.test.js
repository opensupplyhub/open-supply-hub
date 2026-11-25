/* eslint-env jest */
import {
    pendingClaimApiToFormData,
    buildPendingClaimPatchPayload,
} from '../../components/PendingClaimEdit/utils';
import { findSelectOptionObjects } from '../../util/testUtils/payloadShapeAssertions';

const APPAREL_ENTRY = Object.freeze({
    section: 'C - Manufacturing',
    division: '14 - Manufacture of wearing apparel',
    group: '141 - Manufacture of wearing apparel, except fur apparel',
    class: '1410 - Manufacture of wearing apparel, except fur apparel',
});

describe('pending claim edit ISIC mapping', () => {
    it('loads stored ISIC entries as picker options', () => {
        const formData = pendingClaimApiToFormData({
            your_name: 'Name',
            isic_4: [APPAREL_ENTRY],
            isic_5: null,
        });

        expect(formData.isic4).toEqual([
            {
                value: 'class:1410',
                label: 'Manufacture of wearing apparel, except fur apparel',
            },
        ]);
        expect(formData.isic5).toEqual([]);
    });

    it('loads a claim without ISIC fields as empty pickers', () => {
        const formData = pendingClaimApiToFormData({ your_name: 'Name' });

        expect(formData.isic4).toEqual([]);
        expect(formData.isic5).toEqual([]);
    });

    it('sends ISIC options as codes, not as option objects or titles', () => {
        const payload = buildPendingClaimPatchPayload({
            yourName: 'Name',
            isic4: [
                {
                    value: 'class:1410',
                    label: 'Manufacture of wearing apparel, except fur apparel',
                },
            ],
            isic5: [{ value: 'group:631', label: 'Computing infrastructure' }],
        });

        expect(payload.isic_4).toEqual(['class:1410']);
        expect(payload.isic_5).toEqual(['group:631']);
    });

    it('sends an empty list when every ISIC value was removed', () => {
        const payload = buildPendingClaimPatchPayload({
            yourName: 'Name',
            isic4: [],
            isic5: [],
        });

        expect(payload.isic_4).toEqual([]);
        expect(payload.isic_5).toEqual([]);
    });

    it('sends back unchanged the values it loaded', () => {
        const formData = pendingClaimApiToFormData({
            your_name: 'Name',
            isic_4: [APPAREL_ENTRY],
            isic_5: [],
        });

        const payload = buildPendingClaimPatchPayload(formData);

        expect(payload.isic_4).toEqual(['class:1410']);
        expect(payload.isic_5).toEqual([]);
    });
});

/*
 * Pins the whole PATCH body a fully filled edit form produces — the
 * OSDEV-3740 class was a reused step whose payload carried option
 * objects the serializer rejected, so these sweep every field, not just
 * the ISIC ones the fix already covers above.
 */
describe('pending claim edit PATCH payload shape', () => {
    // Labels and values deliberately diverge so the test fails if a
    // field switches between sending one and the other.
    const option = (value, label) => ({ value, label });

    const FULL_FORM_DATA = Object.freeze({
        // Client-only fields the API must never receive back.
        id: 7,
        osId: 'BD2019083CDP49S',
        status: 'PENDING',
        facilityName: 'Azteca Apparel Ltd.',
        createdAt: '2026-11-01T00:00:00Z',
        updatedAt: '2026-11-02T00:00:00Z',
        claimantUpdatedAt: '2026-11-02T00:00:00Z',
        attachments: [{ id: 1, file_name: 'doc.pdf' }],
        employmentVerificationDocuments: [{ name: 'new-upload.pdf' }],
        companyAddressVerificationDocuments: [],
        // The claim fields.
        yourName: 'Jane Smith',
        sectors: [option('Apparel', 'Apparel')],
        facilityType: [
            option('Final Product Assembly', 'Final Product Assembly'),
            option('Office / HQ', 'Office / HQ'),
        ],
        facilityProductTypes: [option('Shirts', 'Shirts')],
        facilityProductionTypes: [option('Assembly', 'Assembly')],
        facilityAffiliations: [],
        facilityCertifications: [option('iso_9001', 'ISO 9001')],
        isic4: [
            option(
                'class:1410',
                'Manufacture of wearing apparel, except fur apparel',
            ),
        ],
        isic5: [],
        numberOfWorkers: '',
        facilityFemaleWorkersPercentage: '40',
        openingDate: '',
        estimatedAnnualThroughput: '12000',
        energyCoal: '12500',
        energyCoalEnabled: true,
        energyDiesel: '7',
        energyDieselEnabled: false,
        energyNaturalGas: '',
        energyNaturalGasEnabled: false,
    });

    const payload = buildPendingClaimPatchPayload(FULL_FORM_DATA);

    it('unwraps every select to the plain strings the API stores', () => {
        expect(payload.sectors).toEqual(['Apparel']);
        expect(payload.facility_product_types).toEqual(['Shirts']);
        expect(payload.facility_production_types).toEqual(['Assembly']);
        expect(payload.facility_affiliations).toEqual([]);
        // Labels, exactly as the create flow sends them.
        expect(payload.facility_certifications).toEqual(['ISO 9001']);
    });

    it('pipe-joins the facility type the way the API stores it', () => {
        expect(payload.facility_type).toBe(
            'Final Product Assembly|Office / HQ',
        );
    });

    it('never sends a {value, label} option object anywhere', () => {
        expect(findSelectOptionObjects(payload)).toEqual([]);
    });

    it('strips client-only and document fields from the payload', () => {
        [
            'id',
            'os_id',
            'status',
            'facility_name',
            'created_at',
            'updated_at',
            'claimant_updated_at',
            'attachments',
            'employment_verification_documents',
            'company_address_verification_documents',
        ].forEach(field => expect(payload).not.toHaveProperty(field));
        // The UI-only checkbox flags stay client side too.
        Object.keys(payload).forEach(key =>
            expect(key.endsWith('_enabled')).toBe(false),
        );
    });

    it('sends null to clear emptied numbers and unchecked energy sections', () => {
        expect(payload.number_of_workers).toBeNull();
        expect(payload.opening_date).toBeNull();
        // Unchecked sections clear their stored value even when the
        // hidden input still holds one.
        expect(payload.energy_diesel).toBeNull();
        expect(payload.energy_natural_gas).toBeNull();
        // Checked sections send theirs.
        expect(payload.energy_coal).toBe('12500');
        expect(payload.estimated_annual_throughput).toBe('12000');
    });
});

describe('pending claim edit load/save round trip', () => {
    it('sends back exactly the values it loaded', () => {
        const formData = pendingClaimApiToFormData({
            id: 7,
            your_name: 'Jane Smith',
            sectors: ['Apparel', 'Textiles'],
            facility_type: 'Final Product Assembly|Office / HQ',
            facility_product_types: ['Shirts'],
            facility_certifications: [],
            isic_4: [APPAREL_ENTRY],
            isic_5: null,
            number_of_workers: '250',
            facility_female_workers_percentage: 40,
            opening_date: null,
            energy_coal: 12500,
            energy_diesel: null,
            attachments: [{ id: 1, file_name: 'doc.pdf' }],
        });

        const payload = buildPendingClaimPatchPayload(formData);

        expect(payload.your_name).toBe('Jane Smith');
        expect(payload.sectors).toEqual(['Apparel', 'Textiles']);
        expect(payload.facility_type).toBe(
            'Final Product Assembly|Office / HQ',
        );
        expect(payload.facility_product_types).toEqual(['Shirts']);
        expect(payload.facility_certifications).toEqual([]);
        expect(payload.isic_4).toEqual(['class:1410']);
        expect(payload.isic_5).toEqual([]);
        expect(payload.number_of_workers).toBe('250');
        expect(payload.facility_female_workers_percentage).toBe('40');
        expect(payload.opening_date).toBeNull();
        expect(payload.energy_coal).toBe('12500');
        expect(payload.energy_diesel).toBeNull();
        expect(findSelectOptionObjects(payload)).toEqual([]);
    });
});

describe('pending claim edit profile visibility choices (OSDEV-2680)', () => {
    it('loads the choices as booleans', () => {
        const formData = pendingClaimApiToFormData({
            your_name: 'Name',
            facility_website_publicly_visible: true,
            facility_phone_number_publicly_visible: false,
        });

        expect(formData.facilityWebsitePubliclyVisible).toBe(true);
        expect(formData.facilityPhoneNumberPubliclyVisible).toBe(false);
    });

    it('sends both choices, including an explicit false', () => {
        const payload = buildPendingClaimPatchPayload({
            yourName: 'Name',
            facilityWebsitePubliclyVisible: false,
            facilityPhoneNumberPubliclyVisible: true,
        });

        expect(payload.facility_website_publicly_visible).toBe(false);
        expect(payload.facility_phone_number_publicly_visible).toBe(true);
    });
});
