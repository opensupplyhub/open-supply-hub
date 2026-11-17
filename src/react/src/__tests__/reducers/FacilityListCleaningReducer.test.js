import reducer from '../../reducers/FacilityListCleaningReducer';
import {
    startFetchFacilityListCleaning,
    failFetchFacilityListCleaning,
    completeFetchFacilityListCleaning,
    resetFacilityListCleaning,
    startSubmitFacilityListCleaningDecisions,
    failSubmitFacilityListCleaningDecisions,
    completeSubmitFacilityListCleaningDecisions,
    startApplyFacilityListCleaning,
    failApplyFacilityListCleaning,
    completeApplyFacilityListCleaning,
} from '../../actions/facilityListCleaning';

const initial = reducer(undefined, { type: '@@INIT' });
const LIST = 42;

// A fetch for the list, and its reply as the server sent it: the reply
// carries the mutation count the fetch was sent at.
const fetchStarted = (state, listID = LIST, silent = false) =>
    reducer(state, startFetchFacilityListCleaning({ listID, silent }));
const fetched = (state, data, { listID = LIST, mutation = state.mutation } = {}) =>
    reducer(state, completeFetchFacilityListCleaning({ listID, mutation, data }));

describe('FacilityListCleaningReducer', () => {
    test('starts empty and idle', () => {
        expect(initial).toEqual({
            listID: null,
            mutation: 0,
            data: null,
            fetching: false,
            error: null,
            submitting: false,
            submitError: null,
            applying: false,
            applyError: null,
            lastApplied: null,
        });
    });

    test('tracks a fetch from start to data or error', () => {
        const fetching = fetchStarted(initial);
        expect(fetching.fetching).toBe(true);
        expect(fetching.listID).toBe(LIST);
        const data = { run: { id: 1 } };
        const done = fetched(fetching, data);
        expect(done.fetching).toBe(false);
        expect(done.data).toBe(data);
        const failed = reducer(
            fetching,
            failFetchFacilityListCleaning(['boom']),
        );
        expect(failed.fetching).toBe(false);
        expect(failed.error).toEqual(['boom']);
    });

    test('a silent fetch shows no spinner and keeps the data on screen', () => {
        const loaded = fetched(fetchStarted(initial), { run: { id: 1 } });
        const polling = fetchStarted(loaded, LIST, true);
        expect(polling.fetching).toBe(false);
        expect(polling.data).toEqual({ run: { id: 1 } });
    });

    test('a reply for another list is ignored', () => {
        const forA = fetchStarted(initial, 7);
        const forB = fetchStarted(forA, LIST);
        expect(forB.data).toBeNull();
        const stale = fetched(forB, { run: { id: 'A' } }, { listID: 7 });
        expect(stale).toBe(forB);
        const current = fetched(stale, { run: { id: 'B' } });
        expect(current.data).toEqual({ run: { id: 'B' } });
        expect(current.fetching).toBe(false);
    });

    test('after a reset, a reply for the old list is ignored', () => {
        const forA = fetchStarted(initial);
        const reset = reducer(forA, resetFacilityListCleaning());
        expect(fetched(reset, { run: { id: 'A' } })).toBe(reset);
    });

    test('a reply fetched before a decision was sent does not overwrite it', () => {
        const loaded = fetched(fetchStarted(initial), {
            run: { id: 1 },
            rows: [{ row_number: 2, suggestions: [{ decision: 'PENDING' }] }],
        });
        // a poll goes out, then the contributor decides a row
        const polling = fetchStarted(loaded, LIST, true);
        const deciding = reducer(polling, startSubmitFacilityListCleaningDecisions());
        const decided = reducer(
            deciding,
            completeSubmitFacilityListCleaningDecisions({
                run: { id: 1 },
                rows: [{ row_number: 2, suggestions: [{ decision: 'ACCEPTED' }] }],
                rows_partial: true,
            }),
        );
        expect(decided.mutation).toBe(2);
        // the poll's reply, from before the decision, arrives last
        const stale = fetched(decided, {
            run: { id: 1 },
            rows: [{ row_number: 2, suggestions: [{ decision: 'PENDING' }] }],
        }, { mutation: 0 });
        expect(stale.data.rows[0].suggestions[0].decision).toBe('ACCEPTED');
        expect(stale.fetching).toBe(false);
        // a fetch sent after the decision is taken
        const fresh = fetched(fetchStarted(stale, LIST, true), { run: { id: 1 }, rows: [] });
        expect(fresh.data.rows).toEqual([]);
    });

    test('a reply fetched before the submission is ignored too', () => {
        const loaded = fetched(fetchStarted(initial), { run: { id: 1, closed_at: null } });
        const polling = fetchStarted(loaded, LIST, true);
        const applying = reducer(polling, startApplyFacilityListCleaning());
        const applied = reducer(
            applying,
            completeApplyFacilityListCleaning({
                run: { id: 1, closed_at: 'now' },
                applied: { applied: 1, reverted: 0 },
            }),
        );
        const stale = fetched(applied, { run: { id: 1, closed_at: null } }, { mutation: 0 });
        expect(stale.data.run.closed_at).toBe('now');
    });

    test('a restart counts as a change', () => {
        const loaded = fetched(fetchStarted(initial), { run: { id: 1 } });
        const polling = fetchStarted(loaded, LIST, true);
        const restarting = reducer(
            polling,
            startFetchFacilityListCleaning({ listID: LIST, restart: true }),
        );
        expect(restarting.mutation).toBe(1);
        const stale = fetched(restarting, { run: { id: 1 } }, { mutation: 0 });
        expect(stale.data).toEqual({ run: { id: 1 } });
        const fresh = fetched(stale, { run: { id: 2 } }, { mutation: 1 });
        expect(fresh.data).toEqual({ run: { id: 2 } });
    });

    test('tracks decisions being saved', () => {
        const saving = reducer(
            initial,
            startSubmitFacilityListCleaningDecisions(),
        );
        expect(saving.submitting).toBe(true);
        const data = { run: { id: 1 }, summary: {} };
        const saved = reducer(
            saving,
            completeSubmitFacilityListCleaningDecisions(data),
        );
        expect(saved.submitting).toBe(false);
        expect(saved.data).toBe(data);
        const failed = reducer(
            saving,
            failSubmitFacilityListCleaningDecisions(['no']),
        );
        expect(failed.submitting).toBe(false);
        expect(failed.submitError).toEqual(['no']);
    });

    test('a partial decision reply replaces only the rows it carries', () => {
        const loaded = fetched(fetchStarted(initial), {
            run: { id: 1 },
            summary: { rows_pending_review: 2 },
            tour_seen: true,
            rows: [
                { row_number: 2, suggestions: ['a'] },
                { row_number: 3, suggestions: ['b'] },
                { row_number: 5, suggestions: ['c'] },
            ],
        });
        const merged = reducer(
            loaded,
            completeSubmitFacilityListCleaningDecisions({
                run: { id: 1 },
                summary: { rows_pending_review: 1 },
                rows: [
                    { row_number: 3, suggestions: ['b2'] },
                    { row_number: 4, suggestions: ['d'] },
                ],
                rows_partial: true,
            }),
        );
        expect(merged.data.summary).toEqual({ rows_pending_review: 1 });
        expect(merged.data.rows_partial).toBeUndefined();
        expect(merged.data.tour_seen).toBe(true);
        expect(merged.data.rows).toEqual([
            { row_number: 2, suggestions: ['a'] },
            { row_number: 3, suggestions: ['b2'] },
            { row_number: 4, suggestions: ['d'] },
            { row_number: 5, suggestions: ['c'] },
        ]);
    });

    test('keeps what the submission applied', () => {
        const applying = reducer(initial, startApplyFacilityListCleaning());
        expect(applying.applying).toBe(true);
        const payload = { run: { id: 1 }, applied: { applied: 3, reverted: 0 } };
        const applied = reducer(
            applying,
            completeApplyFacilityListCleaning(payload),
        );
        expect(applied.applying).toBe(false);
        expect(applied.lastApplied).toEqual({ applied: 3, reverted: 0 });
        expect(applied.data).toBe(payload);
        const failed = reducer(applying, failApplyFacilityListCleaning(['x']));
        expect(failed.applying).toBe(false);
        expect(failed.applyError).toEqual(['x']);
    });

    test('reset returns to the initial state', () => {
        const busy = fetched(fetchStarted(initial), {});
        expect(reducer(busy, resetFacilityListCleaning())).toEqual(initial);
    });
});
