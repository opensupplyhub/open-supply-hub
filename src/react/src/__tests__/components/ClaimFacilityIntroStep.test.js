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
            updateClaimFacilityIntro(true)
        )

        const updatedAgreementState = reduxStore.getState().claimFacility.claimData.formData.agreement
        expect(updatedAgreementState).toBe(true)
    });

    it('select "No" radio button by action', () => {
        const {reduxStore} = renderWithProviders(
            <ClaimFacilityIntroStep agreement="no" updateAgreement={() => {}}/>
        )

        reduxStore.dispatch(
            updateClaimFacilityIntro(false)
        )

        const updatedAgreementState = reduxStore.getState().claimFacility.claimData.formData.agreement
        expect(updatedAgreementState).toBe(false)
    });
});

