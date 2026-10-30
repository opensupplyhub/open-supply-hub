import { renderHook } from '@testing-library/react-hooks';
import { useClaimFormSubmission } from '../../components/InitialClaimFlow/ClaimForm/hooks';

const OS_ID = 'BD2019083CDP49S';

const renderSubmission = resetForm =>
    renderHook(
        ({ fetching, error }) =>
            useClaimFormSubmission(fetching, error, OS_ID, resetForm),
        { initialProps: { fetching: false, error: null } },
    );

describe('useClaimFormSubmission', () => {
    // The test environment is node; setupTests.js provides a JSDOM
    // window, whose sessionStorage the hook uses.
    beforeAll(() => {
        global.sessionStorage = window.sessionStorage;
    });
    afterAll(() => {
        delete global.sessionStorage;
    });
    beforeEach(() => sessionStorage.clear());

    test('shows the success dialog when the submission succeeds', () => {
        const resetForm = jest.fn();
        sessionStorage.setItem(`claim-form-access-${OS_ID}`, 'true');
        const { result, rerender } = renderSubmission(resetForm);

        rerender({ fetching: true, error: null });
        rerender({ fetching: false, error: null });

        expect(result.current.dialogIsOpen).toBe(true);
        expect(resetForm).toHaveBeenCalledTimes(1);
        expect(sessionStorage.getItem(`claim-form-access-${OS_ID}`)).toBeNull();
    });

    test('does not show the dialog when the submission fails', () => {
        const resetForm = jest.fn();
        const { result, rerender } = renderSubmission(resetForm);

        rerender({ fetching: true, error: null });
        rerender({ fetching: false, error: ['Invalid value'] });

        expect(result.current.dialogIsOpen).toBe(false);
        expect(resetForm).not.toHaveBeenCalled();
    });

    test('clearing the error after a failed submission is not treated as success', () => {
        const resetForm = jest.fn();
        sessionStorage.setItem(`claim-form-access-${OS_ID}`, 'true');
        const { result, rerender } = renderSubmission(resetForm);

        rerender({ fetching: true, error: null });
        rerender({ fetching: false, error: ['Invalid value'] });
        // Editing a field clears the server error without submitting.
        rerender({ fetching: false, error: null });

        expect(result.current.dialogIsOpen).toBe(false);
        expect(resetForm).not.toHaveBeenCalled();
        expect(sessionStorage.getItem(`claim-form-access-${OS_ID}`)).toBe(
            'true',
        );
    });

    test('resubmitting after a failed submission shows the dialog on success', () => {
        const resetForm = jest.fn();
        const { result, rerender } = renderSubmission(resetForm);

        rerender({ fetching: true, error: null });
        rerender({ fetching: false, error: ['Invalid value'] });
        rerender({ fetching: false, error: null });
        rerender({ fetching: true, error: null });
        rerender({ fetching: false, error: null });

        expect(result.current.dialogIsOpen).toBe(true);
        expect(resetForm).toHaveBeenCalledTimes(1);
    });
});
