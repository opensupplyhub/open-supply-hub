/*
 * Pins the exact multipart payload the claim create form hands to
 * POST /api/facilities/{os_id}/claim/, and the submit error path, for a
 * fully filled form. Field-level ISIC and sector extraction is pinned in
 * claimForm.submit.test.js; these tests sweep the whole payload so a new
 * or reused select field cannot ship option objects unnoticed
 * (the OSDEV-3737 class).
 */
import configureStore from 'redux-mock-store';
import thunk from 'redux-thunk';

import {
    submitClaimFormData,
    startSubmitClaimFormData,
    failSubmitClaimFormData,
    completeSubmitClaimFormData,
} from '../../actions/claimForm';
import apiRequest from '../../util/apiRequest';
import {
    findObjectCoercions,
    formDataEntries,
} from '../../util/testUtils/payloadShapeAssertions';

jest.mock('../../util/apiRequest', () => ({
    __esModule: true,
    default: { post: jest.fn() },
}));

const mockStore = configureStore([thunk]);
const OS_ID = 'BD2019083CDP49S';

// Labels and values deliberately diverge so the test fails if a field
// switches between sending one and the other.
const option = (value, label) => ({ value, label });

const FULL_FORM_DATA = Object.freeze({
    yourName: 'Jane Smith',
    yourTitle: 'Plant Manager',
    facilityNameEnglish: 'Azteca Apparel Ltd.',
    facilityAddress: '12 Mill Road, Dhaka',
    facilityPhoneNumberPubliclyVisible: false,
    claimantLocationRelationship: null,
    sectors: [option('Apparel', 'Apparel')],
    facilityType: [
        option('Final Product Assembly', 'Final Product Assembly'),
        option('Office / HQ', 'Office / HQ'),
    ],
    facilityProductionTypes: [
        option('Assembly', 'Assembly'),
        option('Cut & Sew', 'Cut & Sew'),
    ],
    facilityProductTypes: [option('Shirts', 'Shirts')],
    facilityAffiliations: [option('fair_wear', 'Fair Wear Foundation')],
    facilityCertifications: [option('iso_9001', 'ISO 9001')],
    isic4: [
        option(
            'class:1410',
            'Manufacture of wearing apparel, except fur apparel',
        ),
    ],
    isic5: [option('division:13', 'Manufacture of textiles')],
    numberOfWorkers: '250',
    openingDate: '',
    estimatedAnnualThroughput: '12000',
    energyCoal: '12.5',
    energyCoalEnabled: true,
    energyDiesel: '7',
    energyDieselEnabled: false,
});

const submitForm = (formData = FULL_FORM_DATA) => {
    const store = mockStore({ claimForm: { formData } });
    const submission = store.dispatch(submitClaimFormData(OS_ID, false));
    return { store, submission };
};

const sentPayload = () => apiRequest.post.mock.calls[0][1];

describe('submitClaimFormData payload shape', () => {
    // The test environment is node; setupTests.js provides a JSDOM
    // window, whose FormData and localStorage the action uses.
    beforeAll(() => {
        global.FormData = window.FormData;
        global.localStorage = window.localStorage;
    });
    afterAll(() => {
        delete global.FormData;
        delete global.localStorage;
    });
    beforeEach(() => {
        localStorage.clear();
        apiRequest.post.mockResolvedValue({ data: {} });
    });

    test('serializes a fully filled form to the fields the claim API takes', () => {
        submitForm();

        expect(apiRequest.post).toHaveBeenCalledWith(
            `/api/facilities/${OS_ID}/claim/`,
            expect.any(FormData),
        );
        expect(formDataEntries(sentPayload())).toEqual({
            your_name: ['Jane Smith'],
            your_title: ['Plant Manager'],
            facility_name_english: ['Azteca Apparel Ltd.'],
            facility_address: ['12 Mill Road, Dhaka'],
            facility_phone_number_publicly_visible: ['false'],
            // Select fields send one entry per option, as labels.
            sectors: ['Apparel'],
            facility_production_types: ['Assembly', 'Cut & Sew'],
            facility_product_types: ['Shirts'],
            facility_affiliations: ['Fair Wear Foundation'],
            facility_certifications: ['ISO 9001'],
            // Facility type is a single pipe-joined entry.
            facility_type: ['Final Product Assembly|Office / HQ'],
            // ISIC sends the codes, never the titles (OSDEV-3737).
            isic_4: ['class:1410'],
            isic_5: ['division:13'],
            number_of_workers: ['250'],
            // Emissions fields: enabled values go out, the checkbox
            // flags, disabled values and the empty date do not.
            estimated_annual_throughput: ['12000'],
            energy_coal: ['12.5'],
        });
    });

    test('never hands the API a coerced option object', () => {
        submitForm();

        expect(findObjectCoercions(sentPayload())).toEqual([]);
    });

    test('sends the remembered invite code and forgets it only on success', async () => {
        const storageKey = `claim-invite-${OS_ID}`;
        localStorage.setItem(
            storageKey,
            JSON.stringify({ code: 'INVITE-X7K2QP', savedAt: Date.now() }),
        );

        const { submission } = submitForm({});
        expect(sentPayload().getAll('claim_invite')).toEqual(['INVITE-X7K2QP']);

        await submission;
        expect(localStorage.getItem(storageKey)).toBeNull();
    });

    test('a rejected submission dispatches failure, not success, and keeps the invite code', async () => {
        apiRequest.post.mockRejectedValue({
            response: { status: 400, data: ['Invalid value'] },
        });
        const storageKey = `claim-invite-${OS_ID}`;
        localStorage.setItem(
            storageKey,
            JSON.stringify({ code: 'INVITE-X7K2QP', savedAt: Date.now() }),
        );

        const { store, submission } = submitForm({});
        await submission;

        expect(store.getActions().map(action => action.type)).toEqual([
            startSubmitClaimFormData.getType(),
            failSubmitClaimFormData.getType(),
        ]);
        expect(
            store
                .getActions()
                .filter(
                    action =>
                        action.type === completeSubmitClaimFormData.getType(),
                ),
        ).toEqual([]);
        // The code is still there for the retry.
        expect(localStorage.getItem(storageKey)).not.toBeNull();
    });
});
