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

describe('FacilityListCleaningReducer', () => {
    test('starts empty and idle', () => {
        expect(initial).toEqual({
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
        const fetching = reducer(initial, startFetchFacilityListCleaning());
        expect(fetching.fetching).toBe(true);
        const data = { run: { id: 1 } };
        const done = reducer(fetching, completeFetchFacilityListCleaning(data));
        expect(done.fetching).toBe(false);
        expect(done.data).toBe(data);
        const failed = reducer(
            fetching,
            failFetchFacilityListCleaning(['boom']),
        );
        expect(failed.fetching).toBe(false);
        expect(failed.error).toEqual(['boom']);
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
        const loaded = reducer(
            initial,
            completeFetchFacilityListCleaning({
                run: { id: 1 },
                summary: { rows_pending_review: 2 },
                tour_seen: true,
                rows: [
                    { row_number: 2, suggestions: ['a'] },
                    { row_number: 3, suggestions: ['b'] },
                    { row_number: 5, suggestions: ['c'] },
                ],
            }),
        );
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
        const busy = reducer(initial, completeFetchFacilityListCleaning({}));
        expect(reducer(busy, resetFacilityListCleaning())).toEqual(initial);
    });
});
