/*
 * Pins what savePendingClaim actually sends: the JSON PATCH body handed
 * to /api/facility-claims/{id}/pending/, the PATCH-before-upload
 * ordering that keeps a failed save retry-safe, and the failure path
 * (the OSDEV-3740 class caught these payloads only in the browser).
 */
import configureStore from 'redux-mock-store';
import thunk from 'redux-thunk';

import {
    savePendingClaim,
    startSavePendingClaim,
    failSavePendingClaim,
    completeSavePendingClaim,
} from '../../actions/pendingClaimEdit';
import apiRequest from '../../util/apiRequest';
import { findSelectOptionObjects } from '../../util/testUtils/payloadShapeAssertions';

jest.mock('../../util/apiRequest', () => ({
    __esModule: true,
    default: { patch: jest.fn(), post: jest.fn() },
}));

const mockStore = configureStore([thunk]);
const CLAIM_ID = 7;

const APPAREL_OPTION = Object.freeze({
    value: 'class:1410',
    label: 'Manufacture of wearing apparel, except fur apparel',
});
const APPAREL_ENTRY = Object.freeze({
    class: '1410 - Manufacture of wearing apparel, except fur apparel',
});

const FORM_DATA = Object.freeze({
    yourName: 'Jane Smith',
    sectors: [{ value: 'Apparel', label: 'Apparel' }],
    isic4: [APPAREL_OPTION],
    isic5: [],
});

const saveClaim = formData => {
    const store = mockStore({ pendingClaimEdit: { formData } });
    const saving = store.dispatch(savePendingClaim(CLAIM_ID));
    return { store, saving };
};

describe('savePendingClaim', () => {
    // The test environment is node; setupTests.js provides a JSDOM
    // window, whose FormData the upload step uses.
    beforeAll(() => {
        global.FormData = window.FormData;
    });
    afterAll(() => {
        delete global.FormData;
    });
    beforeEach(() => {
        apiRequest.patch.mockResolvedValue({ data: {} });
        apiRequest.post.mockResolvedValue({ data: {} });
    });

    test('PATCHes the pending-claim endpoint with the mapped payload', async () => {
        const { saving } = saveClaim(FORM_DATA);
        await saving;

        expect(apiRequest.patch).toHaveBeenCalledTimes(1);
        const [url, body] = apiRequest.patch.mock.calls[0];
        expect(url).toBe(`/api/facility-claims/${CLAIM_ID}/pending/`);
        expect(body).toEqual({
            your_name: 'Jane Smith',
            sectors: ['Apparel'],
            isic_4: ['class:1410'],
            isic_5: [],
        });
        expect(findSelectOptionObjects(body)).toEqual([]);
    });

    test('a failed PATCH dispatches failure and uploads nothing', async () => {
        apiRequest.patch.mockRejectedValue({
            response: { status: 400, data: ['Invalid isic_4 value'] },
        });
        const { store, saving } = saveClaim({
            ...FORM_DATA,
            employmentVerificationDocuments: [
                new window.File(['x'], 'new-upload.pdf'),
            ],
        });
        await saving;

        expect(store.getActions().map(action => action.type)).toEqual([
            startSavePendingClaim.getType(),
            failSavePendingClaim.getType(),
        ]);
        // Nothing was stored, so the still-populated picker can retry
        // without duplicating attachments.
        expect(apiRequest.post).not.toHaveBeenCalled();
    });

    test('uploads new documents only after the PATCH succeeds', async () => {
        const file = new window.File(['x'], 'new-upload.pdf');
        apiRequest.post.mockResolvedValue({
            data: { your_name: 'Jane Smith', isic_4: [APPAREL_ENTRY] },
        });
        const { store, saving } = saveClaim({
            ...FORM_DATA,
            employmentVerificationDocuments: [file],
        });
        await saving;

        expect(apiRequest.post).toHaveBeenCalledTimes(1);
        const [url, postData] = apiRequest.post.mock.calls[0];
        expect(url).toBe(`/api/facility-claims/${CLAIM_ID}/attachments/`);
        expect(postData.getAll('files')).toHaveLength(1);
        expect(
            apiRequest.patch.mock.invocationCallOrder[0],
        ).toBeLessThan(apiRequest.post.mock.invocationCallOrder[0]);

        // The fresh payload reloads into the form, ISIC included — the
        // OSDEV-3740 bug left stored ISIC values out of the form state.
        const complete = store
            .getActions()
            .find(action => action.type === completeSavePendingClaim.getType());
        expect(complete.payload.formData.isic4).toEqual([APPAREL_OPTION]);
    });

    test('a save without new documents sends only the PATCH', async () => {
        apiRequest.patch.mockResolvedValue({
            data: { your_name: 'Jane Smith', isic_4: [APPAREL_ENTRY] },
        });
        const { store, saving } = saveClaim({
            ...FORM_DATA,
            employmentVerificationDocuments: [],
            companyAddressVerificationDocuments: [],
        });
        await saving;

        expect(apiRequest.post).not.toHaveBeenCalled();
        const complete = store
            .getActions()
            .find(action => action.type === completeSavePendingClaim.getType());
        expect(complete.payload.data).toEqual({
            your_name: 'Jane Smith',
            isic_4: [APPAREL_ENTRY],
        });
    });
});
