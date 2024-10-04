import React from 'react';  
import SearchByOsIdNotFoundResult from '../../components/Contribute/SearchByOsIdNotFoundResult';
import renderWithProviders from '../../util/testUtils/renderWithProviders';

jest.mock('../../components/Contribute/SearchByOsIdResultActions', () => () => <div>Mocked SearchByOsIdResultActions</div>);

describe('SearchByOsIdNotFoundResult component', () => {
    const handleBackToSearchByNameAddress = jest.fn();
    const handleBackToSearchByOsId = jest.fn();

    const defaultProps = {
        handleBackToSearchByNameAddress,
        handleBackToSearchByOsId,
    };

    it('renders the title and subtitle correctly', () => {
        const { getByText } = renderWithProviders(<SearchByOsIdNotFoundResult {...defaultProps}/>);

        expect(getByText("We didn't find a production location with that ID.")).toBeInTheDocument();
        expect(getByText('You can try searching by another OS ID or searching by name and address.')).toBeInTheDocument();
    });

    it('renders SearchByOsIdResultActions', () => {
        const { getByText } = renderWithProviders(<SearchByOsIdNotFoundResult {...defaultProps}/>);

        expect(getByText('Mocked SearchByOsIdResultActions')).toBeInTheDocument();
    });

});
