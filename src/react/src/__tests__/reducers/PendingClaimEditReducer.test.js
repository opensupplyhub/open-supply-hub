/*
 * Pins the pending-claim edit save state machine — the same submit-flag
 * machine whose create-flow twin shipped the OSDEV-3737 fake-success
 * bug. A failed save must free the Save button for a retry and must
 * never read as a completed save.
 */
import reducer from '../../reducers/PendingClaimEditReducer';
import {
    updatePendingClaimFormField,
    startSavePendingClaim,
    failSavePendingClaim,
    completeSavePendingClaim,
} from '../../actions/pendingClaimEdit';

const initial = reducer(undefined, { type: '@@INIT' });
const saving = reducer(initial, startSavePendingClaim());

describe('pending claim edit save state machine', () => {
    test('saving sets the in-flight flag and clears the previous outcome', () => {
        expect(saving.saving).toBe(true);
        expect(saving.savingError).toBeNull();
        expect(saving.saved).toBe(false);
    });

    test('a failed save resets the in-flight flag so retrying is possible', () => {
        const failed = reducer(
            saving,
            failSavePendingClaim(['Invalid isic_4 value']),
        );

        expect(failed.saving).toBe(false);
        expect(failed.savingError).toEqual(['Invalid isic_4 value']);
        expect(failed.saved).toBe(false);
    });

    test('editing a field after a failure clears the error without claiming success', () => {
        const failed = reducer(
            {
                ...saving,
                formData: { yourName: 'Jane' },
            },
            failSavePendingClaim(['Invalid isic_4 value']),
        );
        const edited = reducer(
            failed,
            updatePendingClaimFormField({
                field: 'yourName',
                value: 'Jane Smith',
            }),
        );

        expect(edited.savingError).toBeNull();
        expect(edited.saved).toBe(false);
        expect(edited.formData.yourName).toBe('Jane Smith');
    });

    test('a retried save after a failure completes and opens the outcome dialog', () => {
        const fresh = {
            data: { id: 7, your_name: 'Jane Smith' },
            formData: { yourName: 'Jane Smith' },
        };
        const finished = [
            failSavePendingClaim(['Invalid isic_4 value']),
            startSavePendingClaim(),
            completeSavePendingClaim(fresh),
        ].reduce(reducer, saving);

        expect(finished.saving).toBe(false);
        expect(finished.savingError).toBeNull();
        expect(finished.saved).toBe(true);
        expect(finished.data).toEqual(fresh.data);
        expect(finished.formData).toEqual(fresh.formData);
    });
});
