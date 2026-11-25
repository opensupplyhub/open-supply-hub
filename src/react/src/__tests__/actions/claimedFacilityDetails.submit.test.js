/*
 * Pins the PUT body the approved-claim editor hands to
 * /api/facility-claims/{id}/claimed/. It is the third surface reusing
 * the claim profile fields (after claim create and pending-claim edit),
 * and the only one that sends ISIC values as stored-entry objects rather
 * than "level:code" strings — the view accepts both, so the test pins
 * the shape this surface actually sends.
 */
import configureStore from 'redux-mock-store';
import thunk from 'redux-thunk';

import {
    submitClaimedFacilityDetailsUpdate,
    startUpdateClaimedFacilityDetails,
    failUpdateClaimedFacilityDetails,
    completeUpdateClaimedFacilityDetails,
} from '../../actions/claimedFacilityDetails';
import apiRequest from '../../util/apiRequest';
import { findSelectOptionObjects } from '../../util/testUtils/payloadShapeAssertions';

jest.mock('../../util/apiRequest', () => ({
    __esModule: true,
    default: { put: jest.fn() },
}));

const mockStore = configureStore([thunk]);
const CLAIM_ID = 7;

const APPAREL_ENTRY = Object.freeze({
    class: '1410 - Manufacture of wearing apparel, except fur apparel',
});

// The claimed-details state as the GET payload plus the reducer's edits
// leave it: selects already unwrapped to strings, ISIC already converted
// to stored entries (updateClaimedIsic), choice lists loaded for the
// pickers, and the UI-only energy checkbox flags derived.
const CLAIMED_DATA = Object.freeze({
    id: CLAIM_ID,
    facility_name_english: 'Azteca Apparel Ltd.',
    facility_address: '12 Mill Road, Dhaka',
    sector: ['Apparel'],
    isic_4: [APPAREL_ENTRY],
    isic_5: [],
    facility_production_types: ['Assembly'],
    facility_phone_number: '+880123456789',
    facility_parent_company: { id: 3, name: 'Azteca Group' },
    parent_company_name: '  Azteca Group  ',
    facility_workers_count: '250',
    facility_female_workers_percentage: '40',
    opening_date: '',
    estimated_annual_throughput: '',
    energy_coal: '12500',
    energy_coal_enabled: true,
    energy_diesel: '',
    energy_diesel_enabled: true,
    // Unchecking a section clears its value to '' in the UI handler.
    energy_natural_gas: '',
    energy_natural_gas_enabled: false,
    // Reference data for the pickers; never part of the claim.
    contributors: [[1, 'A Contributor', false]],
    countries: [['BD', 'Bangladesh']],
    facility_types: [['Office / HQ', 'Office / HQ']],
    affiliation_choices: [['fair_wear', 'Fair Wear Foundation']],
    certification_choices: [['iso_9001', 'ISO 9001']],
    production_type_choices: [['Assembly', 'Assembly']],
    location_name: 'Azteca Apparel Ltd.',
    location_address: '12 Mill Road, Dhaka',
});

const submitUpdate = (dismissedWarnings = []) => {
    const store = mockStore({
        claimedFacilityDetails: { data: CLAIMED_DATA },
        featureFlags: { flags: {} },
    });
    const submission = store.dispatch(
        submitClaimedFacilityDetailsUpdate(CLAIM_ID, dismissedWarnings),
    );
    return { store, submission };
};

describe('submitClaimedFacilityDetailsUpdate payload shape', () => {
    beforeEach(() => {
        apiRequest.put.mockResolvedValue({ data: {} });
    });

    test('PUTs the claim fields and strips the picker reference data', async () => {
        const { submission } = submitUpdate();
        await submission;

        expect(apiRequest.put).toHaveBeenCalledTimes(1);
        const [url, body] = apiRequest.put.mock.calls[0];
        expect(url).toBe(`/api/facility-claims/${CLAIM_ID}/claimed/`);
        expect(body).toEqual({
            id: CLAIM_ID,
            facility_name_english: 'Azteca Apparel Ltd.',
            facility_address: '12 Mill Road, Dhaka',
            sector: ['Apparel'],
            // Stored-entry objects pass through unchanged; the API
            // accepts them as what it last returned.
            isic_4: [APPAREL_ENTRY],
            isic_5: [],
            facility_production_types: ['Assembly'],
            facility_phone_number: '+880123456789',
            facility_parent_company: { id: 3, name: 'Azteca Group' },
            parent_company_name: 'Azteca Group',
            facility_workers_count: '250',
            facility_female_workers_percentage: '40',
            opening_date: null,
            estimated_annual_throughput: null,
            // Enabled sections send their value (null when emptied).
            // A disabled section's cleared '' rides along in the bulk
            // copy; the API reads both '' and null as "cleared".
            energy_coal: '12500',
            energy_diesel: null,
            energy_natural_gas: '',
        });
        expect(findSelectOptionObjects(body)).toEqual([]);
    });

    test('reports dismissed quality warnings only when there are any', async () => {
        const dismissed = [{ code: 'NAME_TOO_GENERIC' }];
        const first = submitUpdate(dismissed);
        await first.submission;
        const second = submitUpdate();
        await second.submission;

        const [, withWarnings] = apiRequest.put.mock.calls[0];
        expect(withWarnings.dismissed_warnings).toEqual(dismissed);
        const [, withoutWarnings] = apiRequest.put.mock.calls[1];
        expect(withoutWarnings).not.toHaveProperty('dismissed_warnings');
    });

    test('a rejected update dispatches failure, not success', async () => {
        apiRequest.put.mockRejectedValue({
            response: { status: 400, data: ['Invalid value'] },
        });
        const { store, submission } = submitUpdate();
        await submission;

        expect(store.getActions().map(action => action.type)).toEqual([
            startUpdateClaimedFacilityDetails.getType(),
            failUpdateClaimedFacilityDetails.getType(),
        ]);
        expect(
            store
                .getActions()
                .filter(
                    action =>
                        action.type ===
                        completeUpdateClaimedFacilityDetails.getType(),
                ),
        ).toEqual([]);
    });
});
