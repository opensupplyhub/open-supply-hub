import React from 'react';
import { screen, fireEvent, act } from '@testing-library/react';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import {
    reviewData,
    cleaningState,
} from '../../util/testUtils/listCleaningFixtures';
import ListCleaningReviewDialog from '../../components/ListCleaningReviewDialog';
import {
    applyFacilityListCleaning,
    recordFacilityListCleaningEvent,
    submitFacilityListCleaningDecisions,
    submitFacilityListCleaningGroupDecisions,
} from '../../actions/facilityListCleaning';

jest.mock('../../actions/facilityListCleaning', () => ({
    fetchFacilityListCleaning: jest.fn(() => () => Promise.resolve()),
    resetFacilityListCleaning: jest.fn(() => ({
        type: 'RESET_FACILITY_LIST_CLEANING',
    })),
    submitFacilityListCleaningDecisions: jest.fn(() => () =>
        Promise.resolve(),
    ),
    submitFacilityListCleaningGroupDecisions: jest.fn(() => () =>
        Promise.resolve(),
    ),
    applyFacilityListCleaning: jest.fn(() => () => Promise.resolve()),
    recordFacilityListCleaningEvent: jest.fn(() => Promise.resolve(null)),
    beaconFacilityListCleaningEvent: jest.fn(),
}));


const actions = jest.requireMock('../../actions/facilityListCleaning');
const thunk = () => () => Promise.resolve();
const installMocks = () => {
    actions.fetchFacilityListCleaning.mockImplementation(thunk);
    actions.resetFacilityListCleaning.mockImplementation(() => ({
        type: 'RESET_FACILITY_LIST_CLEANING',
    }));
    actions.submitFacilityListCleaningDecisions.mockImplementation(thunk);
    actions.submitFacilityListCleaningGroupDecisions.mockImplementation(thunk);
    actions.applyFacilityListCleaning.mockImplementation(thunk);
    actions.recordFacilityListCleaningEvent.mockImplementation(() =>
        Promise.resolve(null),
    );
    actions.beaconFacilityListCleaningEvent.mockImplementation(() => {});
};

const renderDialog = (data, extra = {}, props = {}) => {
    const onContinue = jest.fn();
    const utils = renderWithProviders(
        <ListCleaningReviewDialog listID={42} open onContinue={onContinue} {...props} />,
        { preloadedState: cleaningState(data, extra) },
    );
    return { ...utils, onContinue };
};

const closeTour = () =>
    act(() => {
        window.dispatchEvent(new window.KeyboardEvent('keydown', { key: 'Escape' }));
    });

describe('ListCleaningReviewDialog', () => {
    beforeEach(() => {
        jest.clearAllMocks();
        installMocks();
    });

    test('waits while the checks run and lets the contributor skip', () => {
        const { onContinue } = renderDialog(reviewData({ run: { status: 'RUNNING' } }));
        expect(screen.getByText('Checking your list for problems')).toBeInTheDocument();
        fireEvent.click(screen.getByRole('button', { name: /Skip and go to my list/ }));
        expect(onContinue).toHaveBeenCalled();
    });

    test('explains when the checks could not run', () => {
        renderDialog(reviewData({ run: { status: 'FAILED', error: 'x' } }));
        expect(screen.getByText('Automatic checks unavailable')).toBeInTheDocument();
    });

    test('the review step shows the journey, the tracker, the tiers and the one submission', () => {
        renderDialog(reviewData());
        expect(screen.getByText('Review issues')).toBeInTheDocument();
        expect(screen.getByText('Submit for manual review')).toBeInTheDocument();
        expect(screen.getByText(/Submit within 30 min/)).toBeInTheDocument();
        // the walkthrough opens with the review
        expect(screen.getByText('Where you are in the upload')).toBeInTheDocument();
        closeTour();
        expect(screen.getByRole('button', { name: /Show me around/ })).toBeInTheDocument();
        expect(screen.getByText(/A few issues in your list need your review/)).toBeInTheDocument();
        expect(screen.getByText('Your review is 0% done')).toBeInTheDocument();
        expect(screen.getByText('Needs review (3)')).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /Apply 2 changes and submit/ })).toBeInTheDocument();
        expect(recordFacilityListCleaningEvent).toHaveBeenCalledWith(
            42, 'opened', expect.objectContaining({ seconds_left: 1800 }),
        );
    });

    test('closing the walkthrough is recorded once, against the user', () => {
        renderDialog(reviewData());
        expect(screen.getByText('Where you are in the upload')).toBeInTheDocument();
        fireEvent.click(screen.getByRole('button', { name: 'Skip tour' }));
        expect(recordFacilityListCleaningEvent).toHaveBeenCalledWith(
            42, 'tour_dismissed', { how: 'skipped' },
        );
        // brought back from the header and closed again: not recorded twice
        fireEvent.click(screen.getByRole('button', { name: /Show me around/ }));
        expect(screen.getByText('Where you are in the upload')).toBeInTheDocument();
        closeTour();
        const dismissals = recordFacilityListCleaningEvent.mock.calls.filter(
            ([, kind]) => kind === 'tour_dismissed',
        );
        expect(dismissals).toHaveLength(1);
    });

    test('a user who has closed the walkthrough before starts without it', () => {
        renderDialog(reviewData({ tour_seen: true }));
        expect(screen.queryByText('Where you are in the upload')).toBeNull();
        expect(screen.getByText(/A few issues in your list need your review/)).toBeInTheDocument();
        fireEvent.click(screen.getByRole('button', { name: /Show me around/ }));
        expect(screen.getByText('Where you are in the upload')).toBeInTheDocument();
        closeTour();
        expect(recordFacilityListCleaningEvent).not.toHaveBeenCalledWith(
            42, 'tour_dismissed', expect.anything(),
        );
    });

    test('decisions go through the actions with the list id', () => {
        renderDialog(reviewData());
        closeTour();
        fireEvent.click(screen.getByRole('button', { name: /Accept all 1 fix/ }));
        expect(submitFacilityListCleaningGroupDecisions).toHaveBeenCalledWith(42, [
            { key: 'CORRECTION:workers_format:number_of_workers', decision: 'ACCEPTED' },
        ]);
        fireEvent.click(screen.getByRole('tab', { name: /Address is a PO Box/ }));
        fireEvent.click(screen.getByRole('button', { name: /^Remove 1 row$/ }));
        fireEvent.click(screen.getByLabelText('Select row 3'));
        fireEvent.click(screen.getByRole('button', { name: /^Keep original values$/ }));
        expect(submitFacilityListCleaningDecisions).toHaveBeenCalledWith(42, [
            { id: 3, decision: 'REJECTED' },
        ]);
    });

    test('resolve everything sends one request that accepts fixes and removes rows', () => {
        renderDialog(reviewData());
        closeTour();
        fireEvent.click(screen.getByRole('button', { name: /Resolve everything/ }));
        expect(submitFacilityListCleaningGroupDecisions).toHaveBeenCalledWith(42, [
            { key: 'ISSUE:address_po_box:address', decision: 'REMOVED' },
            { key: 'CORRECTION:workers_format:number_of_workers', decision: 'ACCEPTED' },
        ]);
    });

    test('submitting as uploaded warns while anything is still flagged', () => {
        renderDialog(reviewData());
        closeTour();
        fireEvent.click(screen.getByRole('button', { name: /Continue with no changes/ }));
        expect(screen.getByText('We may not be able to approve your list')).toBeInTheDocument();
        fireEvent.click(screen.getByRole('button', { name: /Go back and fix/ }));
        expect(screen.queryByText('We may not be able to approve your list')).toBeNull();
        expect(applyFacilityListCleaning).not.toHaveBeenCalled();
        // the closing warning briefly hides the rest of the page from
        // the accessibility tree, so find the button by its text
        fireEvent.click(screen.getByText('Continue with no changes'));
        fireEvent.click(screen.getByRole('button', { name: /Continue anyway/ }));
        expect(applyFacilityListCleaning).toHaveBeenCalledWith(42, { asUploaded: true });
    });

    test('a risky submission warns with the share of flagged rows', () => {
        // 1 flagged row of 6 is over the 15% share
        renderDialog(reviewData());
        closeTour();
        fireEvent.click(screen.getByRole('button', { name: /Apply 2 changes and submit/ }));
        expect(screen.getByText(/1 row still has a required fix/)).toBeInTheDocument();
        expect(screen.getByText(/That is 17% of your list/)).toBeInTheDocument();
        fireEvent.click(screen.getByRole('button', { name: /Continue anyway/ }));
        expect(applyFacilityListCleaning).toHaveBeenCalledWith(42, {});
    });

    test('a safe submission goes straight through', () => {
        renderDialog(reviewData({ summary: { rows_flagged_unresolved: 0, rows_total: 500 } }));
        closeTour();
        fireEvent.click(screen.getByRole('button', { name: /Apply 2 changes and submit/ }));
        expect(screen.queryByText(/still has a required fix/)).toBeNull();
        expect(applyFacilityListCleaning).toHaveBeenCalledWith(42, {});
    });

    test('deciding later records a left event and returns to the list', () => {
        const { onContinue } = renderDialog(reviewData());
        closeTour();
        fireEvent.click(screen.getByRole('button', { name: /Decide later/ }));
        expect(recordFacilityListCleaningEvent).toHaveBeenCalledWith(
            42, 'left', expect.objectContaining({ via: 'button' }),
        );
        expect(onContinue).toHaveBeenCalled();
    });

    test('after the server confirms, the done screen says what happens next', () => {
        renderDialog(
            reviewData({ summary: { rows_removed: 1, rows_flagged_unresolved: 1 } }),
            { lastApplied: { applied: 2, reverted: 0 } },
        );
        expect(screen.getByText('Your list has been submitted for review')).toBeInTheDocument();
        expect(screen.getByText(/2 fixes were applied to your list, including 1 row removed/)).toBeInTheDocument();
        expect(screen.getByText(/1 row still has a required fix/)).toBeInTheDocument();
        expect(screen.getByRole('link', { name: 'standard processing times' })).toHaveAttribute(
            'href',
            'https://info.opensupplyhub.org/resources/data-processing-timelines',
        );
        expect(screen.getByRole('button', { name: /Go to my list/ })).toBeInTheDocument();
    });

    test('a closed window explains itself', () => {
        const { unmount } = renderDialog(
            reviewData({
                window_open: false,
                seconds_left: 0,
                run: { closed_reason: 'lapsed', closed_at: '2026-11-09T11:00:00Z' },
            }),
        );
        expect(screen.getByText('The review window has closed')).toBeInTheDocument();
        expect(screen.getByText(/went to a human moderator exactly as uploaded/)).toBeInTheDocument();
        unmount();
        const lapsedWithChanges = renderDialog(
            reviewData({
                window_open: false,
                seconds_left: 0,
                run: { closed_reason: 'lapsed', closed_at: '2026-11-09T11:00:00Z' },
                summary: { changes_applied: 2 },
            }),
        );
        expect(
            screen.getByText(/with the 2 changes you had decided by then/),
        ).toBeInTheDocument();
        lapsedWithChanges.unmount();
        renderDialog(
            reviewData({
                window_open: false,
                run: { closed_reason: 'submitted', submitted_at: '2026-11-09T10:40:00Z', closed_at: '2026-11-09T10:40:00Z' },
                summary: { changes_applied: 3 },
            }),
        );
        expect(screen.getByText('This list has already been submitted')).toBeInTheDocument();
        expect(screen.getByText(/with 3 changes\. No further changes/)).toBeInTheDocument();
    });

    test('a clean list goes straight to moderation', () => {
        renderDialog(
            reviewData({
                window_open: false,
                rows: [],
                groups: [],
                run: { closed_reason: 'clean', closed_at: '2026-11-09T10:00:05Z' },
                summary: { removals: 0, list_findings: 0, rows_to_review: 0, rows_pending_review: 0 },
            }),
        );
        expect(screen.getByText('Your list looks good')).toBeInTheDocument();
        expect(screen.getByText(/gone straight to a human moderator/)).toBeInTheDocument();
    });
});
