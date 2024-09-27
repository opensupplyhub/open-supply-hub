import React from 'react';
import SearchByOsIdSuccessResult from '../../components/Contribute/SearchByOsIdSuccessResult';
import renderWithProviders from '../../util/testUtils/renderWithProviders';

jest.mock('../../components/Contribute/SearchByOsIdResultActions', () => () => <div>Mocked SearchByOsIdResultActions</div>);
jest.mock('../../components/Contribute/PreviousOsIdTooltip', () => () => <span>Tooltip</span>);

describe('SearchByOsIdSuccessResult component', () => {
    const name = 'Production Location Name';
    const osId = 'US2021250D1DTN7';
    const historicalOsIds = ['US2020053ZH1RY4', 'US2020053ZH1RY5'];
    const address = '1234 Production Location St. United States';
    const handleBackToSearchByNameAddress = jest.fn();

    const defaultProps = {
        name,
        osId,
        address,
        handleBackToSearchByNameAddress
    };

    it('renders without crashing', () => {
        const { getByText, queryByText } = renderWithProviders(<SearchByOsIdSuccessResult {...defaultProps}/>);

        expect(getByText('Is this your production location?')).toBeInTheDocument();
        expect(getByText(name)).toBeInTheDocument();
        expect(getByText(`OS ID: ${osId}`)).toBeInTheDocument();
        expect(queryByText('Previous OS ID:')).not.toBeInTheDocument();
        expect(getByText(address)).toBeInTheDocument();
    });

    it('renders SearchByOsIdResultActions', () => {
        const { getByText } = renderWithProviders(<SearchByOsIdSuccessResult {...defaultProps}/>);

        expect(getByText('Mocked SearchByOsIdResultActions')).toBeInTheDocument();
    });

    it('renders historical OS IDs when provided', () => {
        const { getByText, getAllByText } = renderWithProviders(<SearchByOsIdSuccessResult {...defaultProps} historicalOsIds={historicalOsIds}/>);
        const tooltips = getAllByText('Tooltip');

        expect(getByText(`Current OS ID: ${osId}`)).toBeInTheDocument();
        expect(getByText('Previous OS ID: US2020053ZH1RY4')).toBeInTheDocument();
        expect(getByText('Previous OS ID: US2020053ZH1RY5')).toBeInTheDocument();
        expect(tooltips).toHaveLength(2);
    });

});