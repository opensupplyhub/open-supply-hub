import React from 'react';

import ClaimFacilityIntroStep from '../../components/ClaimFacilityIntroStep';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import { updateClaimFacilityIntro } from '../../actions/claimFacility';


describe('ClaimFacilityIntroStep component', () => {
    it('renders without crashing', () => {
        renderWithProviders(
            <ClaimFacilityIntroStep/>
        )
    });

    it('select "Yes" radio button by action', () => {
        const {reduxStore} = renderWithProviders(
            <ClaimFacilityIntroStep agreement="yes" updateAgreement={() => {}}/>
        )

        reduxStore.dispatch(
            updateClaimFacilityIntro('yes')
        )

        const updatedAgreementState = reduxStore.getState().claimFacility.claimData.formData.agreement
        expect(updatedAgreementState).toBe('yes')
    });


    it('select "No" radio button by action', () => {
        const {reduxStore} = renderWithProviders(
            <ClaimFacilityIntroStep agreement="no" updateAgreement={() => {}}/>
        )

        reduxStore.dispatch(
            updateClaimFacilityIntro('no')
        )

        const updatedAgreementState = reduxStore.getState().claimFacility.claimData.formData.agreement
        expect(updatedAgreementState).toBe('no')
    });
});

