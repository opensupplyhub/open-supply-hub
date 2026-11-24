/*
 * Pins the single location contribution submit state machine: a failed
 * create or update must release the in-flight flag for a retry and must
 * never leave a moderation event behind that reads as success.
 */
import reducer from '../../reducers/ContributeProductionLocationReducer';
import {
    startCreateProductionLocation,
    failCreateProductionLocation,
    completeCreateProductionLocation,
    startUpdateProductionLocation,
    failUpdateProductionLocation,
    completeUpdateProductionLocation,
    resetPendingModerationEvent,
} from '../../actions/contributeProductionLocation';

const initial = reducer(undefined, { type: '@@INIT' });

const V1_ERROR = Object.freeze({
    errorSource: 'CLIENT',
    detail: 'The request body is invalid.',
    errors: [{ field: 'isic_4', detail: 'Invalid entry.' }],
    rawData: null,
});

describe.each([
    ['create', startCreateProductionLocation, failCreateProductionLocation, completeCreateProductionLocation],
    ['update', startUpdateProductionLocation, failUpdateProductionLocation, completeUpdateProductionLocation],
])('production location %s state machine', (name, start, fail, complete) => {
    const submitting = reducer(initial, start({ name: 'Azteca Apparel' }));

    test('submitting sets the in-flight flag and clears stale results', () => {
        expect(submitting.pendingModerationEvent).toEqual({
            fetching: true,
            error: null,
            data: {},
        });
    });

    test('a failed submission resets the in-flight flag so retrying is possible', () => {
        const failed = reducer(submitting, fail(V1_ERROR));

        expect(failed.pendingModerationEvent).toEqual({
            fetching: false,
            error: V1_ERROR,
            // No moderation event: nothing was created.
            data: {},
        });
    });

    test('a retried submission after a failure completes normally', () => {
        const moderationEvent = { moderation_id: 'abc123', status: 'PENDING' };
        const finished = [
            fail(V1_ERROR),
            start({ name: 'Azteca Apparel' }),
            complete(moderationEvent),
        ].reduce(reducer, submitting);

        expect(finished.pendingModerationEvent).toEqual({
            fetching: false,
            error: null,
            data: moderationEvent,
        });
    });

    test('leaving the flow clears the pending moderation event', () => {
        const finished = reducer(
            submitting,
            complete({ moderation_id: 'abc123' }),
        );
        const cleared = reducer(finished, resetPendingModerationEvent());

        expect(cleared.pendingModerationEvent).toEqual(
            initial.pendingModerationEvent,
        );
    });
});
