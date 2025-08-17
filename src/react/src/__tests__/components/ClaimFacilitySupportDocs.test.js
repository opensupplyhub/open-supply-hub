import React from 'react';
import { screen, fireEvent, waitFor } from '@testing-library/react';

import ClaimFacilitySupportDocs from '../../components/ClaimFacilitySupportDocs';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import { 
    updateClaimAFacilityClaimReason, 
    updateClaimAFacilityClaimReasonOther,
    completeFetchClaimsReasons
} from '../../actions/claimFacility';


describe('ClaimFacilitySupportDocs claim reason functionality', () => {
    const mockClaimsReasons = [
        { id: 1, text: 'Acme Inc' },
        { id: 2, text: 'Global Fashion Corp' }
    ];

    it('renders claim reason dropdown', () => {
        renderWithProviders(
            <ClaimFacilitySupportDocs />
        );
        
        expect(screen.getByText('What made you decide to claim?')).toBeInTheDocument();
    });

    it('shows Other text field when Other is selected', async () => {
        const { reduxStore } = renderWithProviders(
            <ClaimFacilitySupportDocs />
        );

        reduxStore.dispatch(updateClaimAFacilityClaimReason('Other'));

        await waitFor(() => {
            expect(screen.getByPlaceholderText('Please specify')).toBeInTheDocument();
        });
    });

    it('hides Other text field when non-Other option selected', async () => {
        const { reduxStore } = renderWithProviders(
            <ClaimFacilitySupportDocs />
        );

        // First select Other to show the field
        reduxStore.dispatch(updateClaimAFacilityClaimReason('Other'));
        
        await waitFor(() => {
            expect(screen.getByPlaceholderText('Please specify')).toBeInTheDocument();
        });

        // Then select a brand name
        reduxStore.dispatch(completeFetchClaimsReasons(mockClaimsReasons));
        reduxStore.dispatch(updateClaimAFacilityClaimReason('Acme Inc'));

        await waitFor(() => {
            expect(screen.queryByPlaceholderText('Please specify')).not.toBeInTheDocument();
        });
    });

    it('updates character counter correctly', async () => {
        const { reduxStore } = renderWithProviders(
            <ClaimFacilitySupportDocs />
        );

        reduxStore.dispatch(updateClaimAFacilityClaimReason('Other'));
        reduxStore.dispatch(updateClaimAFacilityClaimReasonOther('Test reason'));

        await waitFor(() => {
            expect(screen.getByText('89/100 characters remaining')).toBeInTheDocument();
        });
    });

    it('enforces 100 character limit', async () => {
        const { reduxStore } = renderWithProviders(
            <ClaimFacilitySupportDocs />
        );

        reduxStore.dispatch(updateClaimAFacilityClaimReason('Other'));
        
        await waitFor(() => {
            const textField = screen.getByPlaceholderText('Please specify');
            expect(textField).toHaveAttribute('maxLength', '100');
        });
    });
});