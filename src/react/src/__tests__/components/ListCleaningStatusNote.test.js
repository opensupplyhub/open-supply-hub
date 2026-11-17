import React from 'react';
import { screen, fireEvent, act } from '@testing-library/react';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import {
    reviewData,
    cleaningState,
} from '../../util/testUtils/listCleaningFixtures';
import ListCleaningStatusNote from '../../components/ListCleaningStatusNote';
import {
    startFetchFacilityListCleaning,
    completeFetchFacilityListCleaning,
} from '../../actions/facilityListCleaning';

// The thunks are mocked; the plain action creators stay real, so the
// store's reducer still answers to them and a test can feed it a reply.
jest.mock('../../actions/facilityListCleaning', () => ({
    ...jest.requireActual('../../actions/facilityListCleaning'),
    fetchFacilityListCleaning: jest.fn(() => () => Promise.resolve()),
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
    actions.submitFacilityListCleaningDecisions.mockImplementation(thunk);
    actions.submitFacilityListCleaningGroupDecisions.mockImplementation(thunk);
    actions.applyFacilityListCleaning.mockImplementation(thunk);
    actions.recordFacilityListCleaningEvent.mockImplementation(() =>
        Promise.resolve(null),
    );
    actions.beaconFacilityListCleaningEvent.mockImplementation(() => {});
};

const renderNote = (data, props = {}) =>
    renderWithProviders(
        <ListCleaningStatusNote
            listID={42}
            isListOwner
            isAdminUser={false}
            {...props}
        />,
        { preloadedState: cleaningState(data) },
    );

describe('ListCleaningStatusNote', () => {
    beforeEach(installMocks);

    test('renders nothing until the run has completed', () => {
        const { container } = renderNote(
            reviewData({ run: { status: 'RUNNING' } }),
        );
        expect(container).toBeEmptyDOMElement();
    });

    test('the owner can resume the review while the window is open', () => {
        renderNote(reviewData());
        expect(
            screen.getByText(/You can still review and submit changes/),
        ).toBeInTheDocument();
        fireEvent.click(screen.getByRole('button', { name: /Resume review/ }));
        expect(
            screen.getByText(/Review your list before it goes to a human moderator/),
        ).toBeInTheDocument();
    });

    test('a moderator is told why approve and reject wait', () => {
        renderNote(reviewData(), { isListOwner: false, isAdminUser: true });
        expect(
            screen.getByText(/Approve and reject are unavailable until then/),
        ).toBeInTheDocument();
        expect(screen.queryByRole('button', { name: /Resume review/ })).toBeNull();
    });

    test('a submitted list says how much changed', () => {
        renderNote(
            reviewData({
                window_open: false,
                seconds_left: 0,
                run: {
                    closed_reason: 'submitted',
                    submitted_at: '2026-11-09T10:40:00Z',
                    closed_at: '2026-11-09T10:40:00Z',
                },
                summary: { changes_applied: 3 },
            }),
        );
        expect(
            screen.getByText(/with 3 changes from the automated checks/),
        ).toBeInTheDocument();
    });

    test('a submission as uploaded and a lapse are told apart', () => {
        const { unmount } = renderNote(
            reviewData({
                window_open: false,
                run: {
                    closed_reason: 'submitted',
                    submitted_at: '2026-11-09T10:40:00Z',
                    closed_at: '2026-11-09T10:40:00Z',
                },
            }),
        );
        expect(screen.getByText(/as uploaded\. No further changes/)).toBeInTheDocument();
        unmount();
        const second = renderNote(
            reviewData({
                window_open: false,
                run: { closed_reason: 'lapsed', closed_at: '2026-11-09T11:00:00Z' },
            }),
        );
        expect(
            screen.getByText(/closed .* without a submission, so the list went through as uploaded/),
        ).toBeInTheDocument();
        second.unmount();
        // a lapse after the contributor had decided things carries them
        renderNote(
            reviewData({
                window_open: false,
                run: { closed_reason: 'lapsed', closed_at: '2026-11-09T11:00:00Z' },
                summary: { changes_applied: 2 },
            }),
        );
        expect(
            screen.getByText(/without a submission, so the list went through with the 2 changes decided by then/),
        ).toBeInTheDocument();
    });

    test('the rows reload when an open review lapses on screen', () => {
        const onSubmitted = jest.fn();
        const { reduxStore } = renderNote(reviewData(), { onSubmitted });
        expect(onSubmitted).not.toHaveBeenCalled();
        // the ticking refetch finds the window closed
        act(() => {
            reduxStore.dispatch(
                completeFetchFacilityListCleaning({
                    listID: 42,
                    mutation: 0,
                    data: reviewData({
                        window_open: false,
                        seconds_left: 0,
                        run: {
                            closed_reason: 'lapsed',
                            closed_at: '2026-11-09T11:00:00Z',
                        },
                    }),
                }),
            );
        });
        expect(onSubmitted).toHaveBeenCalledTimes(1);
        expect(
            screen.getByText(/closed .* without a submission/),
        ).toBeInTheDocument();
    });

    test('leaving the resumed review refetches after the dialog has cleared the store', async () => {
        const onSubmitted = jest.fn();
        const lapsed = reviewData({
            window_open: false,
            seconds_left: 0,
            run: { closed_reason: 'lapsed', closed_at: '2026-11-09T11:00:00Z' },
        });
        // The fetch as the real one behaves: it names its list on the way
        // out, and its reply names it and the mutation count it was sent at.
        let reply = null;
        actions.fetchFacilityListCleaning.mockImplementation(
            listID => (dispatch, getState) => {
                dispatch(startFetchFacilityListCleaning({ listID, silent: true }));
                const { mutation } = getState().facilityListCleaning;
                if (!reply) return Promise.resolve();
                return Promise.resolve().then(() =>
                    dispatch(
                        completeFetchFacilityListCleaning({ listID, mutation, data: reply }),
                    ),
                );
            },
        );
        const { reduxStore } = renderNote(reviewData(), { onSubmitted });
        fireEvent.click(screen.getByRole('button', { name: /Resume review/ }));
        // the window closes while the review is on screen
        reply = lapsed;
        act(() => {
            reduxStore.dispatch(
                completeFetchFacilityListCleaning({ listID: 42, mutation: 0, data: lapsed }),
            );
        });
        // Leaving unmounts the dialog, which clears the store slice; the
        // refetch sent after that is for the list the store names again.
        fireEvent.click(screen.getByRole('button', { name: /Go to my list/ }));
        expect(
            await screen.findByText(/closed .* without a submission/),
        ).toBeInTheDocument();
        expect(reduxStore.getState().facilityListCleaning.listID).toBe(42);
        expect(onSubmitted).toHaveBeenCalledTimes(1);
    });

    test('a review already closed when the page opens does not reload the rows', () => {
        const onSubmitted = jest.fn();
        renderNote(
            reviewData({
                window_open: false,
                run: { closed_reason: 'lapsed', closed_at: '2026-11-09T11:00:00Z' },
            }),
            { onSubmitted },
        );
        expect(onSubmitted).not.toHaveBeenCalled();
    });

    test('a clean result went straight to moderation', () => {
        renderNote(
            reviewData({
                window_open: false,
                run: { closed_reason: 'clean', closed_at: '2026-11-09T10:00:05Z' },
            }),
        );
        expect(
            screen.getByText(/found nothing to fix, so the list went straight/),
        ).toBeInTheDocument();
    });
});
