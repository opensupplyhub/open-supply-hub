import React from 'react';
import ProductionLocationDetails from '../../components/Contribute/ProductionLocationDetails';
import renderWithProviders from '../../util/testUtils/renderWithProviders';

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

    test('renders the production location details correctly', () => {
        const { getByText } = renderWithProviders(<ProductionLocationDetails {...defaultProps}/>);
    
        expect(getByText(name)).toBeInTheDocument();
        expect(getByText(`Current OS ID: ${osId}`)).toBeInTheDocument();
        expect(getByText(`Previous OS ID: ${historicalOsIds[0]}`)).toBeInTheDocument();
        expect(getByText(`Previous OS ID: ${historicalOsIds[1]}`)).toBeInTheDocument();
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
    
    test('renders the tooltip for each historical OS ID', () => {
        const { getAllByTestId } = renderWithProviders(<ProductionLocationDetails {...defaultProps}/>);
    
        const tooltips = getAllByTestId('previous-os-id-tooltip');
        expect(tooltips.length).toBe(defaultProps.historicalOsIds.length);
    });
});


