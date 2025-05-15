import React from 'react';
import { waitFor } from "@testing-library/react";
import { toast } from 'react-toastify';
import FacilityDetailsCoreFields from '../../components/FacilityDetailsCoreFields';
import { facilityDetailsActions } from '../../util/constants';
import renderWithProviders from '../../util/testUtils/renderWithProviders';

jest.mock('react-toastify', () => ({
    toast: jest.fn(),
}));

jest.mock('../../components/ReportFacilityStatusDialog', () => ({ showDialog }) =>
    showDialog ? <div data-testid="report-dialog" /> : null
);

describe('FacilityDetailsCoreFields component', () => {
    const defaultProps = {
        name: 'Test Name',
        osId: 'US202510850SQCV',
        isEmbed: false,
        isClaimed: false,
        isClosed: false,
        facilityIsClaimedByCurrentUser: false,
        userHasPendingFacilityClaim: false,
    };

    afterEach(() => {
        jest.clearAllMocks();
    });

    test('renders facility name and OS ID', () => {
        const { getByText } = renderWithProviders(
            <FacilityDetailsCoreFields {...defaultProps} />,
        );

        expect(getByText('Facility')).toBeInTheDocument();
        expect(getByText('Test Name')).toBeInTheDocument();
        expect(getByText('OS ID:')).toBeInTheDocument();
        expect(getByText('US202510850SQCV')).toBeInTheDocument();
    });

    test('shows action buttons when not embedded', () => {
        const { getByRole } = renderWithProviders(
            <FacilityDetailsCoreFields {...defaultProps} />,
        );

        expect(getByRole('button', { name: /Report/i })).toBeInTheDocument();
        expect(getByRole('button', { name: /Copy Link/i })).toBeInTheDocument();
        expect(getByRole('button', { name: /Copy OS ID/i })).toBeInTheDocument();
    });

    test('does not show action buttons when embedded', () => {
        const { queryByRole } = renderWithProviders(
            <FacilityDetailsCoreFields {...defaultProps} isEmbed />,
        );

        expect(queryByRole('button', { name: /Report/i })).not.toBeInTheDocument();
        expect(queryByRole('button', { name: /Copy Link/i })).not.toBeInTheDocument();
        expect(queryByRole('button', { name: /Copy OS ID/i })).not.toBeInTheDocument();
    });

    test('copies OS ID and calls toast', () => {
        const { getByRole } = renderWithProviders(
            <FacilityDetailsCoreFields {...defaultProps} />,
        );

        const copyButton = getByRole('button', { name: /Copy OS ID/i });
        copyButton.click();

        expect(toast).toHaveBeenCalledWith('Copied OS ID to clipboard');
    });

    test('copies link and calls toast', () => {
        const { getByRole } = renderWithProviders(
            <FacilityDetailsCoreFields {...defaultProps} />,
        );

        const copyLinkButton = getByRole('button', { name: /Copy Link/i });
        copyLinkButton.click();
        
        expect(toast).toHaveBeenCalledWith('Copied link');
    });

    test('opens report menu and shows all menu items', () => {
        const { getByRole, getByText } = renderWithProviders(
            <FacilityDetailsCoreFields {...defaultProps} />,
        );

        const reportButton = getByRole('button', { name: /Report/i });
        reportButton.click();

        expect(getByText(facilityDetailsActions.REPORT_AS_DUPLICATE)).toBeInTheDocument();
        expect(getByText(facilityDetailsActions.REPORT_AS_CLOSED)).toBeInTheDocument();
        expect(getByText(facilityDetailsActions.SUGGEST_AN_EDIT)).toBeInTheDocument();
    });

    test('opens report menu and shows "Dispute Claim" when facility is claimed', () => {
        const { getByRole, getByText } = renderWithProviders(
            <FacilityDetailsCoreFields {...defaultProps} isClaimed />,
        );

        const reportButton = getByRole('button', { name: /Report/i });
        reportButton.click();

        expect(getByText(facilityDetailsActions.DISPUTE_CLAIM)).toBeInTheDocument();
    });

    test('opens report menu and does not show "Dispute Claim" when facility is claimed by current user', () => {
        const { getByRole, queryByText } = renderWithProviders(
            <FacilityDetailsCoreFields
                {...defaultProps}
                isClaimed
                facilityIsClaimedByCurrentUser
            />,
        );

        const reportButton = getByRole('button', { name: /Report/i });
        reportButton.click();

        expect(queryByText(facilityDetailsActions.DISPUTE_CLAIM)).not.toBeInTheDocument();
    });

    test('opens report menu and does not show "Dispute Claim" when user has pending facility claim', () => {
        const { getByRole, queryByText } = renderWithProviders(
            <FacilityDetailsCoreFields
                {...defaultProps}
                isClaimed
                userHasPendingFacilityClaim
            />,
        );

        const reportButton = getByRole('button', { name: /Report/i });
        reportButton.click();

        expect(queryByText(facilityDetailsActions.DISPUTE_CLAIM)).not.toBeInTheDocument();
    });

    test('opens report menu and shows "Report as Reopened" when facility is closed', () => {
        const { getByRole, getByText } = renderWithProviders(
            <FacilityDetailsCoreFields {...defaultProps} isClosed />,
        );

        const reportButton = getByRole('button', { name: /Report/i });
        reportButton.click();

        expect(getByText(facilityDetailsActions.REPORT_AS_REOPENED)).toBeInTheDocument();
    });

    test('opens report menu and shows "Report as Closed" dialog when this menu item is clicked', () => {
        const { getByRole, getByText, getByTestId } = renderWithProviders(
            <FacilityDetailsCoreFields {...defaultProps} />,
        );

        const reportButton = getByRole('button', { name: /Report/i });
        reportButton.click();

        const reportAsClosedButton = getByText(facilityDetailsActions.REPORT_AS_CLOSED);
        reportAsClosedButton.click();

        expect(getByTestId('report-dialog')).toBeInTheDocument();
    });

    test('clicking "Suggest an Edit" renders correct link and closes the menu', () => {
        const { getByRole, queryByText } = renderWithProviders(
            <FacilityDetailsCoreFields {...defaultProps} />,
        );

        const reportButton = getByRole('button', { name: /Report/i });
        reportButton.click();

        const suggestAnEditLink = getByRole('link', {
            name: facilityDetailsActions.SUGGEST_AN_EDIT,
          });
        
        expect(suggestAnEditLink).toHaveAttribute(
            'href',
            '/contribute/single-location/US202510850SQCV/info/',
        );
        expect(suggestAnEditLink).toHaveAttribute('target', '_blank');
        expect(suggestAnEditLink).toHaveAttribute('rel', 'noreferrer');

        suggestAnEditLink.click();

        waitFor(() => {
            expect(queryByText(facilityDetailsActions.SUGGEST_AN_EDIT)).not.toBeInTheDocument();
        });
    });

    test('clicking "Report as Duplicate" opens correct mailto link and closes the menu', () => {
        const { getByRole, queryByText } = renderWithProviders(
            <FacilityDetailsCoreFields {...defaultProps} />,
        );

        const reportButton = getByRole('button', { name: /Report/i });
        reportButton.click();

        const reportAsDuplicateLink = getByRole('link', {
            name: facilityDetailsActions.REPORT_AS_DUPLICATE,
        });
        
        expect(reportAsDuplicateLink).toHaveAttribute(
            'href',
            'mailto:data@opensupplyhub.org?subject=Reporting ID US202510850SQCV as a duplicate facility',
        );

        reportAsDuplicateLink.click();

        waitFor(() => {
            expect(queryByText(facilityDetailsActions.REPORT_AS_DUPLICATE)).not.toBeInTheDocument();
        });
    });

    test('clicking "Dispute Claim" opens correct mailto link and closes the menu', () => {
        const { getByRole, queryByText } = renderWithProviders(
            <FacilityDetailsCoreFields {...defaultProps} isClaimed />,
        );

        const reportButton = getByRole('button', { name: /Report/i });
        reportButton.click();

        const disputeClaimLink = getByRole('link', {
            name: facilityDetailsActions.DISPUTE_CLAIM,
        });
        
        expect(disputeClaimLink).toHaveAttribute(
            'href',
            'mailto:claims@opensupplyhub.org?subject=Disputing a claim of facility ID US202510850SQCV',
        );
        
        disputeClaimLink.click();
        
        waitFor(() => {
            expect(queryByText(facilityDetailsActions.DISPUTE_CLAIM)).not.toBeInTheDocument();
        });
    });
})
