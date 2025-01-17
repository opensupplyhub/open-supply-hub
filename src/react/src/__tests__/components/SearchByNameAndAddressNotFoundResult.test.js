import React from 'react';
import { fireEvent } from '@testing-library/react';
import SearchByNameAndAddressNotFoundResult from '../../components/Contribute/SearchByNameAndAddressNotFoundResult';
import { contributeProductionLocationRoute, productionLocationInfoRoute } from '../../util/constants';
import history from '../../util/history';
import renderWithProviders from '../../util/testUtils/renderWithProviders';

jest.mock('../../util/history', () => ({
    push: jest.fn(),
}));

describe('SearchByNameAndAddressNotFoundResult component', () => {
    test('renders the not found message and buttons correctly', () => {
        const { getByText, getByRole } = renderWithProviders(<SearchByNameAndAddressNotFoundResult />);

        expect(getByText('Search returned no results')).toBeInTheDocument();
        expect(
            getByText(
              'We could not find any results that match your search criteria. ' +
              'If you think the production location you are looking for is ' +
              'already on OS Hub, check the information you entered and try ' +
              'again. If you still don\'t find any results, add a new ' +
              'production location.'
          )).toBeInTheDocument();

        expect(getByRole('button', { name: 'Search again' })).toBeInTheDocument();
        expect(getByRole('button', { name: 'Add a new Location' })).toBeInTheDocument();
    });

    test('navigates to the contribute page when Search again is clicked', () => {
        const { getByRole } = renderWithProviders(<SearchByNameAndAddressNotFoundResult />);

        const searchAgainButton = getByRole('button', { name: 'Search again' });
        fireEvent.click(searchAgainButton);

        expect(history.push).toHaveBeenCalledWith(`${contributeProductionLocationRoute}?tab=name-address`);
    });

    test("navigates to the contribute page when 'Add a new Location' is clicked", () => {
        const { getByRole } = renderWithProviders(<SearchByNameAndAddressNotFoundResult />);

        const addNewLocation = getByRole('button', { name: 'Add a new Location' });
        fireEvent.click(addNewLocation);

        expect(history.push).toHaveBeenCalledWith(productionLocationInfoRoute);
    });
});
