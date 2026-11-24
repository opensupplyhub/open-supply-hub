/*
 * Pins the claim form's submit state machine. The OSDEV-3737 regression
 * was a submit flag that survived a failed request, so a later error
 * clear read as success and silently dropped the claim; these tests keep
 * every transition of that machine honest at the reducer level.
 */
import reducer from '../../reducers/ClaimFormReducer';
import {
    startSubmitClaimFormData,
    failSubmitClaimFormData,
    completeSubmitClaimFormData,
    clearClaimFormSubmissionError,
} from '../../actions/claimForm';

const initial = reducer(undefined, { type: '@@INIT' });
const submitting = reducer(initial, startSubmitClaimFormData());

describe('claim form submission state machine', () => {
    test('starts idle with nothing submitted', () => {
        expect(initial.submissionState).toEqual({
            fetching: false,
            error: null,
            data: null,
        });
    });

    test('submitting sets the in-flight flag and clears stale results', () => {
        const failed = reducer(
            submitting,
            failSubmitClaimFormData(['Invalid value']),
        );
        const resubmitting = reducer(failed, startSubmitClaimFormData());

        expect(resubmitting.submissionState).toEqual({
            fetching: true,
            error: null,
            data: null,
        });
    });

    test('a failed submission resets the in-flight flag so retrying is possible', () => {
        const failed = reducer(
            submitting,
            failSubmitClaimFormData(['Invalid value']),
        );

        expect(failed.submissionState).toEqual({
            fetching: false,
            error: ['Invalid value'],
            data: null,
        });
    });

    test('clearing the error after a failure never looks like success', () => {
        // Editing any field clears the server error without submitting;
        // the OSDEV-3737 bug read the resulting state as a completed
        // claim. Submitted data must stay empty.
        const failed = reducer(
            submitting,
            failSubmitClaimFormData(['Invalid value']),
        );
        const cleared = reducer(failed, clearClaimFormSubmissionError());

        expect(cleared.submissionState).toEqual({
            fetching: false,
            error: null,
            data: null,
        });
    });

    test('a retried submission after a failure completes normally', () => {
        const confirmation = { id: 42 };
        const finished = [
            failSubmitClaimFormData(['Invalid value']),
            clearClaimFormSubmissionError(),
            startSubmitClaimFormData(),
            completeSubmitClaimFormData(confirmation),
        ].reduce(reducer, submitting);

        expect(finished.submissionState).toEqual({
            fetching: false,
            error: null,
            data: confirmation,
        });
    });
});
