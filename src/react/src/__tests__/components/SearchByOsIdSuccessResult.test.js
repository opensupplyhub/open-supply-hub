import React from 'react';
import { fireEvent } from '@testing-library/react';
import SearchByOsIdSuccessResult from '../../components/Contribute/SearchByOsIdSuccessResult';
import renderWithProviders from '../../util/testUtils/renderWithProviders';

jest.mock('../../components/Contribute/SearchByOsIdResultActions', () => ({
    __esModule: true,
    default: ({ defaultButtonLabel, defaultButtonAction, secondaryButtonLabel, secondaryButtonAction }) => (
        <div>
            <button type='button' onClick={defaultButtonAction}>{defaultButtonLabel}</button>
            <button type='button' onClick={secondaryButtonAction}>{secondaryButtonLabel}</button>
        </div>
    ),
}));

jest.mock('../../components/Contribute/ProductionLocationDetails', () => ({
    __esModule: true,
    default: ({ osId, name, address, countryName, historicalOsIds }) => (
        <div>
            <div>{`OS ID: ${osId}`}</div>
            <div>{`Name: ${name}`}</div>
            <div>{`Address: ${address}`}</div>
            <div>{`Country: ${countryName}`}</div>
            {historicalOsIds && historicalOsIds.map((id) => <div key={id}>{`Historical OS ID: ${id}`}</div>)}
        </div>
    ),
}));

describe('SearchByOsIdSuccessResult component', () => {
    const defaultProps = {
        productionLocation: {
            name: 'Production Location Name',
            os_id: 'US2021250D1DTN7',
            address: '1234 Production Location St, City, State, 12345',
            country: {
                alpha_2: 'US',
                alpha_3: 'USA',
                name: 'United States',
                numeric: '840',
            },
            historical_os_id: ['US2020053ZH1RY4', 'US2020053ZH1RY5'],
        },
        handleBackToSearchByNameAddress: jest.fn(),
    };

    test('renders the production location details and actions correctly', () => {
        const { getByText, getByRole } = renderWithProviders(<SearchByOsIdSuccessResult {...defaultProps} />);

        expect(getByText('Is this your production location?')).toBeInTheDocument();
        expect(getByText('OS ID: US2021250D1DTN7')).toBeInTheDocument();
        expect(getByText('Name: Production Location Name')).toBeInTheDocument();
        expect(getByText('Address: 1234 Production Location St, City, State, 12345')).toBeInTheDocument();
        expect(getByText('Country: United States')).toBeInTheDocument();
        expect(getByText('Historical OS ID: US2020053ZH1RY4')).toBeInTheDocument();
        expect(getByText('Historical OS ID: US2020053ZH1RY5')).toBeInTheDocument();
        expect(getByRole('button', { name: 'No, search by name and address' })).toBeInTheDocument();
        expect(getByRole('button', { name: 'Yes, add data and claim' })).toBeInTheDocument();
    });

    test('calls handleBackToSearchByNameAddress when the default button is clicked', () => {
        const { getByRole } = renderWithProviders(<SearchByOsIdSuccessResult {...defaultProps} />);

        const backButton = getByRole('button', {
            name: 'No, search by name and address',
        });
        fireEvent.click(backButton);

        expect(defaultProps.handleBackToSearchByNameAddress).toHaveBeenCalledTimes(1);
    });
});
