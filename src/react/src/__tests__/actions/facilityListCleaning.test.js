import configureStore from 'redux-mock-store';
import thunk from 'redux-thunk';

import {
    fetchFacilityListCleaning,
    startFacilityListCleaningRun,
    submitFacilityListCleaningDecisions,
    submitFacilityListCleaningGroupDecisions,
    applyFacilityListCleaning,
    recordFacilityListCleaningEvent,
    beaconFacilityListCleaningEvent,
    startFetchFacilityListCleaning,
    completeFetchFacilityListCleaning,
    failFetchFacilityListCleaning,
    startSubmitFacilityListCleaningDecisions,
    completeSubmitFacilityListCleaningDecisions,
    failSubmitFacilityListCleaningDecisions,
    startApplyFacilityListCleaning,
    completeApplyFacilityListCleaning,
    failApplyFacilityListCleaning,
} from '../../actions/facilityListCleaning';
import apiRequest from '../../util/apiRequest';

jest.mock('../../util/apiRequest', () => ({
    __esModule: true,
    default: { get: jest.fn(), post: jest.fn() },
}));

const mockStore = configureStore([thunk]);
const types = store => store.getActions().map(a => a.type);
const LIST = 42;

describe('facilityListCleaning actions', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    test('fetch dispatches start and complete with the payload', async () => {
        const payload = { run: { id: 1 } };
        apiRequest.get.mockResolvedValue({ data: payload });
        const store = mockStore({});
        await store.dispatch(fetchFacilityListCleaning(LIST));
        expect(apiRequest.get.mock.calls[0][0]).toContain(`/${LIST}/cleaning/`);
        expect(types(store)).toEqual([
            startFetchFacilityListCleaning.getType(),
            completeFetchFacilityListCleaning.getType(),
        ]);
        expect(store.getActions()[1].payload).toBe(payload);
    });

    test('a silent fetch skips the start action', async () => {
        apiRequest.get.mockResolvedValue({ data: {} });
        const store = mockStore({});
        await store.dispatch(fetchFacilityListCleaning(LIST, { silent: true }));
        expect(types(store)).toEqual([
            completeFetchFacilityListCleaning.getType(),
        ]);
    });

    test('a failed fetch dispatches the failure with a message', async () => {
        apiRequest.get.mockRejectedValue(new Error('nope'));
        const store = mockStore({});
        await store.dispatch(fetchFacilityListCleaning(LIST));
        expect(types(store)).toContain(failFetchFacilityListCleaning.getType());
    });

    test('start posts to the start endpoint', async () => {
        apiRequest.post.mockResolvedValue({ data: { run: { id: 2 } } });
        const store = mockStore({});
        await store.dispatch(startFacilityListCleaningRun(LIST));
        expect(apiRequest.post.mock.calls[0][0]).toContain('cleaning/start');
        expect(types(store)).toEqual([
            startFetchFacilityListCleaning.getType(),
            completeFetchFacilityListCleaning.getType(),
        ]);
    });

    test('row decisions are posted as a decisions list', async () => {
        apiRequest.post.mockResolvedValue({ data: { summary: {} } });
        const store = mockStore({});
        const decisions = [{ id: 1, decision: 'ACCEPTED' }];
        await store.dispatch(submitFacilityListCleaningDecisions(LIST, decisions));
        const [url, body] = apiRequest.post.mock.calls[0];
        expect(url).toContain('cleaning/decisions');
        expect(body).toEqual({ decisions });
        expect(types(store)).toEqual([
            startSubmitFacilityListCleaningDecisions.getType(),
            completeSubmitFacilityListCleaningDecisions.getType(),
        ]);
    });

    test('group decisions are posted as a groups list and can fail', async () => {
        apiRequest.post.mockRejectedValue({
            response: { status: 400, data: ['Group x is not part of this run.'] },
        });
        const store = mockStore({});
        const groups = [{ key: 'ISSUE:pii:name', decision: 'REMOVED' }];
        await store.dispatch(
            submitFacilityListCleaningGroupDecisions(LIST, groups),
        );
        expect(apiRequest.post.mock.calls[0][1]).toEqual({ groups });
        expect(types(store)).toEqual([
            startSubmitFacilityListCleaningDecisions.getType(),
            failSubmitFacilityListCleaningDecisions.getType(),
        ]);
    });

    test('the submission sends as_uploaded and keeps the applied counts', async () => {
        const payload = { run: { id: 1 }, applied: { applied: 2, reverted: 0 } };
        apiRequest.post.mockResolvedValue({ data: payload });
        const store = mockStore({});
        await store.dispatch(
            applyFacilityListCleaning(LIST, { asUploaded: true }),
        );
        const [url, body] = apiRequest.post.mock.calls[0];
        expect(url).toContain('cleaning/submit');
        expect(body).toEqual({ as_uploaded: true });
        expect(types(store)).toEqual([
            startApplyFacilityListCleaning.getType(),
            completeApplyFacilityListCleaning.getType(),
        ]);
    });

    test('a submission defaults to applying the changes and reports failure', async () => {
        apiRequest.post.mockRejectedValue(new Error('down'));
        const store = mockStore({});
        await store.dispatch(applyFacilityListCleaning(LIST));
        expect(apiRequest.post.mock.calls[0][1]).toEqual({ as_uploaded: false });
        expect(types(store)).toEqual([
            startApplyFacilityListCleaning.getType(),
            failApplyFacilityListCleaning.getType(),
        ]);
    });

    test('events are best effort and never reject', async () => {
        apiRequest.post.mockRejectedValue(new Error('429'));
        await expect(
            recordFacilityListCleaningEvent(LIST, 'left', { via: 'button' }),
        ).resolves.toBeNull();
        expect(apiRequest.post.mock.calls[0][0]).toContain('cleaning/events');
        expect(apiRequest.post.mock.calls[0][1]).toEqual({
            kind: 'left',
            meta: { via: 'button' },
        });
    });

    test('the unload beacon uses fetch with keepalive and swallows errors', () => {
        const fetchMock = jest.fn(() => Promise.reject(new Error('gone')));
        global.fetch = fetchMock;
        window.ENVIRONMENT = { OAR_CLIENT_KEY: 'key' };
        expect(() =>
            beaconFacilityListCleaningEvent(LIST, 'left', { via: 'unload' }),
        ).not.toThrow();
        const [url, options] = fetchMock.mock.calls[0];
        expect(url).toContain('cleaning/events');
        expect(options.keepalive).toBe(true);
        expect(JSON.parse(options.body)).toEqual({
            kind: 'left',
            meta: { via: 'unload' },
        });
        global.fetch = () => {
            throw new Error('no fetch');
        };
        expect(() =>
            beaconFacilityListCleaningEvent(LIST, 'left'),
        ).not.toThrow();
        delete global.fetch;
    });
});
