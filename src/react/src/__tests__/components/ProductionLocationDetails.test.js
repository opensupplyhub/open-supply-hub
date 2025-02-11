import React from 'react';
import { useLocation } from 'react-router-dom';
import ProductionLocationDetails from '../../components/Contribute/ProductionLocationDetails';
import renderWithProviders from '../../util/testUtils/renderWithProviders';

jest.mock('react-router-dom', () => ({
    ...jest.requireActual('react-router-dom'),
    useLocation: jest.fn(),
}));

describe('ProductionLocationDetails component', () => {
    const osId = 'US2021250D1DTN7';
    const name = 'Production Location Name';
    const address = '1234 Production Location St, City, State, 12345';
    const countryName = 'United States';
    const historicalOsIds = ['US2020053ZH1RY4', 'US2020053ZH1RY5'];

    const defaultProps = {
        osId,
        name,
        address,
        countryName,
        historicalOsIds,
    };

    beforeEach(() => {
        jest.clearAllMocks();
    });

    test('renders production location details correctly', () => {
        useLocation.mockReturnValue({
            pathname: '/contribute/production-location/search/id/US2021250D1DTN7',
        });

        const { getByText } = renderWithProviders(
            <ProductionLocationDetails {...defaultProps} />
        );

        expect(getByText(name)).toBeInTheDocument();
        expect(getByText(`Current OS ID: ${osId}`)).toBeInTheDocument();
        expect(getByText(address)).toBeInTheDocument();
        expect(getByText(countryName)).toBeInTheDocument();
    });

    test('does not render historical OS IDs if the array is empty', () => {
        const props = { ...defaultProps, historicalOsIds: [] };
        const { getByText, queryByText } = renderWithProviders(<ProductionLocationDetails {...props}/>);
    
        expect(getByText(`OS ID: ${osId}`)).toBeInTheDocument();
        expect(queryByText('Previous OS ID:')).not.toBeInTheDocument();
    });
    
    test('renders without crashing when no historical OS IDs are provided', () => {
        const props = { ...defaultProps, historicalOsIds: undefined };
        const { getByText } = renderWithProviders(<ProductionLocationDetails {...props}/>);
    
        expect(getByText(`OS ID: ${osId}`)).toBeInTheDocument();
    });

    test('renders previous OS IDs that match the search parameter', () => {
        useLocation.mockReturnValue({
            pathname: '/contribute/production-location/search/id/US2020053ZH1RY5',
        });

        const { getByText } = renderWithProviders(
            <ProductionLocationDetails {...defaultProps} />
        );

        expect(getByText(`Current OS ID: ${osId}`)).toBeInTheDocument();
        expect(getByText('Previous OS ID: US2020053ZH1RY5')).toBeInTheDocument();
    });

    test('does not render previous OS IDs if they do not match the search parameter', () => {
        useLocation.mockReturnValue({
            pathname: '/contribute/production-location/search/id/UNKNOWN_OS_ID',
        });

        const { queryByText } = renderWithProviders(
            <ProductionLocationDetails {...defaultProps} />
        );

        expect(queryByText(`Previous OS ID: ${osId}`)).not.toBeInTheDocument();
    });

    test('renders only "OS ID:" if there are no historical OS IDs', () => {
        useLocation.mockReturnValue({
            pathname: '/contribute/production-location/search/id/US2021250D1DTN7',
        });

        const { getByText } = renderWithProviders(
            <ProductionLocationDetails
                {...defaultProps}
                historicalOsIds={[]}
            />
        );

        expect(getByText(`OS ID: ${osId}`)).toBeInTheDocument();
    });

    test('handles missing location pathname gracefully', () => {
        useLocation.mockReturnValue({});

        const { getByText } = renderWithProviders(
            <ProductionLocationDetails {...defaultProps} />
        );

        expect(getByText(`Current OS ID: ${osId}`)).toBeInTheDocument();
    });
});
