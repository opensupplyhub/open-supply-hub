/*
 * Pins the exact JSON body the single location contribution form hands
 * to POST/PATCH /api/v1/production-locations/. ISIC conversion is pinned
 * at the unit level in IsicValuePicker.test.js; these tests cover the
 * action boundary: the full composed payload, the override query params,
 * and the failure dispatch.
 */
import configureStore from 'redux-mock-store';
import thunk from 'redux-thunk';

import {
    createProductionLocation,
    updateProductionLocation,
    startCreateProductionLocation,
    failCreateProductionLocation,
    completeCreateProductionLocation,
    startUpdateProductionLocation,
    completeUpdateProductionLocation,
} from '../../actions/contributeProductionLocation';
import apiRequest from '../../util/apiRequest';
import { findSelectOptionObjects } from '../../util/testUtils/payloadShapeAssertions';

jest.mock('../../util/apiRequest', () => ({
    __esModule: true,
    default: { post: jest.fn(), patch: jest.fn() },
}));

const mockStore = configureStore([thunk]);
const OS_ID = 'BD2019083CDP49S';

// Labels and values deliberately diverge: unlike the claim form, the SLC
// form sends option VALUES, so a swap to labels must fail these tests.
const option = (value, label) => ({ value, label });

const CONTRIB_DATA = Object.freeze({
    name: 'Azteca Apparel Ltd.',
    address: '12 Mill Road, Dhaka',
    country: option('BD', 'Bangladesh'),
    sector: [option('Apparel', 'Apparel & Garments')],
    productType: [option('Shirts', 'Shirts')],
    locationType: [
        option('Final Product Assembly', 'Final Product Assembly'),
    ],
    processingType: [option('Assembly', 'Assembly')],
    parentCompany: 'Azteca Group',
    numberOfWorkers: '100-250',
    isic: {
        4: [
            option(
                'class:1410',
                'Manufacture of wearing apparel, except fur apparel',
            ),
        ],
        5: [],
    },
});

const EXPECTED_BODY = Object.freeze({
    name: 'Azteca Apparel Ltd.',
    address: '12 Mill Road, Dhaka',
    country: 'BD',
    sector: ['Apparel'],
    product_type: ['Shirts'],
    location_type: ['Final Product Assembly'],
    processing_type: ['Assembly'],
    parent_company: 'Azteca Group',
    number_of_workers: { min: 100, max: 250 },
    // The v1 API takes ISIC entries keyed by level; the empty revision
    // is left out entirely.
    isic_4: [
        { class: '1410 - Manufacture of wearing apparel, except fur apparel' },
    ],
    source: 'SLC',
});

describe('single location contribution submissions', () => {
    beforeEach(() => {
        apiRequest.post.mockResolvedValue({ data: {} });
        apiRequest.patch.mockResolvedValue({ data: {} });
    });

    test('POSTs the composed v1 payload, with no overrides by default', async () => {
        const store = mockStore({});
        await store.dispatch(createProductionLocation(CONTRIB_DATA));

        expect(apiRequest.post).toHaveBeenCalledTimes(1);
        const [url, body, config] = apiRequest.post.mock.calls[0];
        expect(url).toBe('/api/v1/production-locations/');
        expect(body).toEqual(EXPECTED_BODY);
        expect(config).toBeUndefined();
        expect(findSelectOptionObjects(body)).toEqual([]);

        expect(store.getActions().map(action => action.type)).toEqual([
            startCreateProductionLocation.getType(),
            completeCreateProductionLocation.getType(),
        ]);
    });

    test('resubmits past confirmed checks through query params only', async () => {
        const store = mockStore({});
        await store.dispatch(createProductionLocation(CONTRIB_DATA, true));
        await store.dispatch(
            createProductionLocation(CONTRIB_DATA, true, true),
        );

        const [, firstBody, firstConfig] = apiRequest.post.mock.calls[0];
        expect(firstConfig).toEqual({ params: { duplicate_override: true } });
        expect(firstBody).toEqual(EXPECTED_BODY);

        const [, , secondConfig] = apiRequest.post.mock.calls[1];
        expect(secondConfig).toEqual({
            params: { duplicate_override: true, ignore_warnings: true },
        });
    });

    test('PATCHes the same payload to the location being updated', async () => {
        const store = mockStore({});
        await store.dispatch(updateProductionLocation(CONTRIB_DATA, OS_ID));

        expect(apiRequest.patch).toHaveBeenCalledTimes(1);
        const [url, body, config] = apiRequest.patch.mock.calls[0];
        expect(url).toBe(`/api/v1/production-locations/${OS_ID}/`);
        expect(body).toEqual(EXPECTED_BODY);
        expect(config).toBeUndefined();

        expect(store.getActions().map(action => action.type)).toEqual([
            startUpdateProductionLocation.getType(),
            completeUpdateProductionLocation.getType(),
        ]);
    });

    test('a rejected submission dispatches failure with the v1 error shape', async () => {
        const errors = [{ field: 'isic_4', detail: 'Invalid entry.' }];
        apiRequest.post.mockRejectedValue({
            response: {
                status: 422,
                data: { detail: 'The request body is invalid.', errors },
            },
        });
        const store = mockStore({});
        await store.dispatch(createProductionLocation(CONTRIB_DATA));

        const [start, fail] = store.getActions();
        expect(start.type).toBe(startCreateProductionLocation.getType());
        // The start action carries the parsed payload, not the raw form
        // values.
        expect(start.payload).toEqual(EXPECTED_BODY);
        expect(fail.type).toBe(failCreateProductionLocation.getType());
        expect(fail.payload).toEqual({
            errorSource: 'CLIENT',
            detail: 'The request body is invalid.',
            errors,
            rawData: { detail: 'The request body is invalid.', errors },
        });
    });
});
