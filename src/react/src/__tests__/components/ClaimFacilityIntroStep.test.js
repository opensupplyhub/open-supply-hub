import React from 'react';

import ClaimFacilityIntroStep from '../../components/ClaimFacilityIntroStep';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import { updateClaimFacilityIntro } from '../../actions/claimFacility';


describe('ClaimFacilityIntroStep component', () => {
    // let store;

    // beforeEach(() => {
    //     store = mockStore({
    //         claimFacility: {
    //             claimData: {
    //                 formData: { agreement },
    //         },
    //         },
    //     });
    // });

    it('renders without crashing', () => {
        renderWithProviders(
            <ClaimFacilityIntroStep/>
        )
    });

    it('select "Yes" radio button by action', () => {
        const {reduxStore} = renderWithProviders(
            <ClaimFacilityIntroStep agreement="true" updateAgreement={() => {}}/>
        )

        reduxStore.dispatch(
            updateClaimFacilityIntro(true)
        )

        const updatedAgreementState = reduxStore.getState().claimFacility.claimData.formData.agreement
        expect(updatedAgreementState).toBe(true)
    });

    it('select "No" radio button by action', () => {
        const {reduxStore} = renderWithProviders(
            <ClaimFacilityIntroStep agreement="false" updateAgreement={() => {}}/>
        )

        reduxStore.dispatch(
            updateClaimFacilityIntro(false)
        )

        const updatedAgreementState = reduxStore.getState().claimFacility.claimData.formData.agreement
        expect(updatedAgreementState).toBe(false)
    });

    // it('renders correct button for unselected radio button', () => {
    //     const { getByText, queryByText } = renderComponent(store, defaultProps);
    //     expect(getByText("GO BACK")).toBeInTheDocument();
    //     expect(queryByText("NEXT")).not.toBeInTheDocument();
    // });

    // test('renders correct buttons for selected "Yes" radio button', () => {
    // const props = {
    //     ...defaultProps,
    //     data: { ...defaultProps.data, status: "APPROVED" },
    // };
    // const { getByText, queryByText } = renderComponent(store, props);
    // expect(getByText("Revoke Claim")).toBeInTheDocument();
    // expect(queryByText("Message Claimant")).not.toBeInTheDocument();
    // expect(queryByText("Approve Claim")).not.toBeInTheDocument();
    // expect(queryByText("Deny Claim")).not.toBeInTheDocument();
    // });
});

