import React from 'react';
import { fireEvent } from '@testing-library/react';
import SearchByNameAndAddressSuccessResult from '../../components/Contribute/SearchByNameAndAddressSuccessResult';
import renderWithProviders from '../../util/testUtils/renderWithProviders';

jest.mock('../../components/Contribute/ConfirmNotFoundLocationDialog', () => ({
    __esModule: true,
    default: ({ confirmDialogIsOpen, handleConfirmDialogClose }) => <div>{confirmDialogIsOpen && <button type='button' onClick={handleConfirmDialogClose}>Close Dialog</button>}</div>,
}));

jest.mock('../../components/Contribute/ProductionLocationDetails', () => ({
    __esModule: true,
    default: ({ osId, name, address, countryName }) => (
        <div>
            <div>{`OS ID: ${osId}`}</div>
            <div>{`Name: ${name}`}</div>
            <div>{`Address: ${address}`}</div>
            <div>{`Country: ${countryName}`}</div>
        </div>
    ),
}));

describe('SearchByNameAndAddressSuccessResult component', () => {
    const defaultProps = {
        productionLocationsCount: 2,
        productionLocations: [
            {
                os_id: 'US1234567890124',
                name: 'Location 1',
                address: '1234 Address St.',
                country: {
                    alpha_2: 'US',
                    alpha_3: 'USA',
                    name: 'United States',
                    numeric: '840',
                },
            },
            {
                os_id: 'CA1234567890124',
                name: 'Location 2',
                address: '5678 Avenue Rd.',
                country: {
                    alpha_2: 'CA',
                    alpha_3: 'CAN',
                    name: 'Canada',
                    numeric: '124',
                },
            },
        ],
        clearLocations: jest.fn(),
    };

    test('renders the search results and locations correctly', () => {
        const { getByText, getAllByRole } = renderWithProviders(<SearchByNameAndAddressSuccessResult {...defaultProps} />);
        expect(getByText('Search results')).toBeInTheDocument();
        expect(
            getByText(
              'We found results that closely match your search criteria. Since names ' +
              'and addresses on OS Hub are user-provided, there may be slight ' +
              'differences between what you entered and what\'s shown below. Find the ' +
              'best match for the production location you are looking for in the list ' +
              'below, click “Select” to edit the name, address and country, and to ' +
              'add more information.'
            )
        ).toBeInTheDocument();
        expect(getByText('Locations')).toBeInTheDocument();
        expect(getByText('2 results')).toBeInTheDocument();
        expect(getByText('Sort By:')).toBeInTheDocument();
        expect(getByText('Best match')).toBeInTheDocument();

        expect(getByText('OS ID: US1234567890124')).toBeInTheDocument();
        expect(getByText('Name: Location 1')).toBeInTheDocument();
        expect(getByText('Address: 1234 Address St.')).toBeInTheDocument();
        expect(getByText('Country: United States')).toBeInTheDocument();

        expect(getByText('OS ID: CA1234567890124')).toBeInTheDocument();
        expect(getByText('Name: Location 2')).toBeInTheDocument();
        expect(getByText('Address: 5678 Avenue Rd.')).toBeInTheDocument();
        expect(getByText('Country: Canada')).toBeInTheDocument();

        const selectButtons = getAllByRole('button', { name: 'Select' });
        expect(selectButtons).toHaveLength(2);
    });

    test('opens the ConfirmNotFoundLocationDialog when the "I don\'t see my Location" button is clicked', () => {
        const { getByText, getByRole } = renderWithProviders(<SearchByNameAndAddressSuccessResult {...defaultProps} />);

        const notFoundButton = getByRole('button', {
            name: "I don't see my Location",
        });
        fireEvent.click(notFoundButton);

        expect(getByText('Close Dialog')).toBeInTheDocument();
    });

    test('closes the ConfirmNotFoundLocationDialog when the close button is clicked', () => {
        const { getByText, getByRole, queryByText } = renderWithProviders(<SearchByNameAndAddressSuccessResult {...defaultProps} />);

        const notFoundButton = getByRole('button', {
            name: "I don't see my Location",
        });
        fireEvent.click(notFoundButton);

        const closeButton = getByText('Close Dialog');
        fireEvent.click(closeButton);

        expect(queryByText('Close Dialog')).not.toBeInTheDocument();
    });
});
