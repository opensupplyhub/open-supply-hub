import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { fireEvent } from '@testing-library/react';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import FacilityListItemsConfirmationTableRowItem from '../../components/FacilityListItemsConfirmationTableRowItem';
import { facilityMatchStatusChoicesEnum, CONFIRM_ACTION } from '../../util/constants';

describe('FacilityListItemsConfirmationTableRowItem component', () => {
    const defaultProps = {
        id: 1,
        os_id: 'UA2019096H785YM',
        name: 'Test Facility',
        status: 'PENDING',
        className: '',
        activeCheckboxes: [],
        address: '123 Main St',
        isCheckboxDisabled: jest.fn(),
        confidence: '0.7',
        readOnly: false,
        toggleCheckbox: jest.fn(),
        action: '',
        is_claimed: false,
    };

    const renderComponent = (props = {}) =>
        renderWithProviders(
            <Router>
                <table>
                    <tbody>
                        <FacilityListItemsConfirmationTableRowItem {...defaultProps} {...props} />
                    </tbody>
                </table>
            </Router>
        );

    it('renders without crashing', () => {
        renderComponent();
    });

    it('renders the facility name', () => {
        const { getByText } = renderComponent();

        expect(getByText('Test Facility')).toBeInTheDocument();
    });

    it('renders the facility address', () => {
        const { getByText } = renderComponent();

        expect(getByText('123 Main St')).toBeInTheDocument();
    });

    it('renders the facility confidence', () => {
        const { getByText } = renderComponent();

        expect(getByText('0.7')).toBeInTheDocument();
    });

    it('renders BadgeVerified when is_claimed is true', () => {
        const { getByTestId } = renderComponent({ is_claimed: true });

        const badgeIcon = getByTestId('badge-verified');

        expect(badgeIcon).toBeInTheDocument();
    });

    it('does not render BadgeVerified when is_claimed is false', () => {
        const { queryByTestId } = renderComponent();

        const badgeIcon = queryByTestId('badge-verified');

        expect(badgeIcon).not.toBeInTheDocument();
    });

    it('renders a Checkbox when status is PENDING and readOnly is false', () => {
        const { getByRole } = renderComponent();

        const checkbox = getByRole('checkbox');
        expect(checkbox).toBeInTheDocument();
    });

    it('does not render a Checkbox when status is not PENDING', () => {
        const { queryByRole } = renderComponent({
            status: facilityMatchStatusChoicesEnum.CONFIRMED,
        });

        const checkbox = queryByRole('checkbox');
        expect(checkbox).not.toBeInTheDocument();
    });

    it('does not render a Checkbox when readOnly is true', () => {
        const { queryByRole } = renderComponent({ readOnly: true });

        const checkbox = queryByRole('checkbox');
        expect(checkbox).not.toBeInTheDocument();
    });

    it('renders the status text when status is not PENDING', () => {
        const { getByText } = renderComponent({
            status: facilityMatchStatusChoicesEnum.CONFIRMED,
        });

        expect(getByText(facilityMatchStatusChoicesEnum.CONFIRMED)).toBeInTheDocument();
    });

    it('calls toggleCheckbox when Checkbox is clicked', () => {
        const toggleCheckbox = jest.fn();

        const { getByRole } = renderComponent({ toggleCheckbox });

        const checkbox = getByRole('checkbox');
        fireEvent.click(checkbox);

        expect(toggleCheckbox).toHaveBeenCalledWith({
            id: 1,
            os_id: 'UA2019096H785YM',
            address: '123 Main St',
            name: 'Test Facility',
            confidence: '0.7',
        });
    });

    it('checks the Checkbox when action is CONFIRM_ACTION and activeCheckboxes contains the item', () => {
        const { getByRole } = renderComponent({
            action: CONFIRM_ACTION,
            activeCheckboxes: [{ id: 1 }],
        });

        const checkbox = getByRole('checkbox');
        expect(checkbox).toBeChecked();
    });

    it('disables the Checkbox based on isCheckboxDisabled', () => {
        const isCheckboxDisabled = jest.fn().mockReturnValue(true);

        const { getByRole } = renderComponent({ isCheckboxDisabled });

        const checkbox = getByRole('checkbox');
        expect(checkbox).toBeDisabled();
    });
});
