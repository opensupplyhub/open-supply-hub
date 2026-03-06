import React from 'react';
import { screen } from '@testing-library/react';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import FacilityListControls from '../../components/FacilityListControls';

const createPreloadedState = (status, statusChangeReason = '') => ({
    facilityListDetails: {
        list: {
            data: {
                status,
                status_change_reason: statusChangeReason,
            },
            fetching: false,
            error: null,
        },
    },
});

describe('FacilityListControls', () => {
    it('displays "Feedback Phase" when status is REJECTED', () => {
        renderWithProviders(
            <FacilityListControls
                id={1}
                isAdminUser={false}
            />,
            {
                preloadedState: createPreloadedState('REJECTED', 'Some reason'),
            },
        );

        expect(screen.getByText(/Feedback Phase/)).toBeInTheDocument();
        expect(screen.queryByText('REJECTED')).not.toBeInTheDocument();
    });

    it('displays the raw status when status is not REJECTED', () => {
        renderWithProviders(
            <FacilityListControls
                id={1}
                isAdminUser={false}
            />,
            {
                preloadedState: createPreloadedState('APPROVED'),
            },
        );

        expect(screen.getByText(/APPROVED/)).toBeInTheDocument();
        expect(screen.queryByText('Feedback Phase')).not.toBeInTheDocument();
    });
});
