import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import FacilityListItemsConfirmationTableRowItem from '../../components/FacilityListItemsConfirmationTableRowItem';

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

    it('renders without crashing', () => {
        renderWithProviders(
            <Router>
                <FacilityListItemsConfirmationTableRowItem {...defaultProps} />
            </Router>
        )
    });

    it('renders the facility name', () => {
        const { getByText } = renderWithProviders(
            <Router>
                <FacilityListItemsConfirmationTableRowItem {...defaultProps} />
            </Router>
        );

        expect(getByText('Test Facility')).toBeInTheDocument();
    });

    it('renders the facility address', () => {
        const { getByText } = renderWithProviders(
            <Router>
                <FacilityListItemsConfirmationTableRowItem {...defaultProps} />
            </Router>
        );

        expect(getByText('123 Main St')).toBeInTheDocument();
    });

    it('renders the facility confidence', () => {
        const { getByText } = renderWithProviders(
            <Router>
                <FacilityListItemsConfirmationTableRowItem {...defaultProps} />
            </Router>
        );

        expect(getByText('0.7')).toBeInTheDocument();
    });

    it('renders BadgeVerified when is_claimed is true', () => {
        const { getByTestId } = renderWithProviders(
            <Router>
                <FacilityListItemsConfirmationTableRowItem
                    {...defaultProps}
                    is_claimed={true}
                />
            </Router>
        );

        const badgeIcon = getByTestId('badge-verified');

        expect(badgeIcon).toBeInTheDocument();
    });

    it('does not render BadgeVerified when is_claimed is false', () => {
        const { queryByTestId } = renderWithProviders(
            <Router>
                <FacilityListItemsConfirmationTableRowItem {...defaultProps} />
            </Router>
        );
        
        const badgeIcon = queryByTestId('badge-verified');

        expect(badgeIcon).not.toBeInTheDocument();
    });
});

