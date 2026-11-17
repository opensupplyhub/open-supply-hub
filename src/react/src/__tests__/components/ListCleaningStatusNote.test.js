import React from 'react';
import { screen, fireEvent } from '@testing-library/react';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import {
    reviewData,
    cleaningState,
} from '../../util/testUtils/listCleaningFixtures';
import ListCleaningStatusNote from '../../components/ListCleaningStatusNote';

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
