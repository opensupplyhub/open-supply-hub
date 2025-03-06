import React from 'react';
import { MemoryRouter, Route } from "react-router-dom";
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import ClaimedFacilitiesList from '../../components/ClaimedFacilitiesList';
import {
    fetchClaimedFacilities,
    clearClaimedFacilities,
} from '../../actions/claimedFacilities';

jest.mock('../../actions/claimedFacilities', () => {
    const actualActions = jest.requireActual('../../actions/claimedFacilities');
    return {
        ...actualActions,
        fetchClaimedFacilities: jest.fn(),
        clearClaimedFacilities: jest.fn(),
    };
});

describe('ClaimedFacilitiesList', () => {
    const renderComponent = () => {
        const claimedPageRoute = '/claimed'
        const preloadedState = {
            claimedFacilities: {
                data: [],
                fetching: false
            }
        };

        return renderWithProviders(
            <MemoryRouter initialEntries={[claimedPageRoute]}>
                <Route
                    path={claimedPageRoute}
                    component={() => <ClaimedFacilitiesList />}
                />
            </MemoryRouter>,
            { preloadedState }
        );
    };

    beforeEach(() => {
        jest.clearAllMocks();
        fetchClaimedFacilities.mockReturnValue(() => Promise.resolve());
        clearClaimedFacilities.mockReturnValue(() => Promise.resolve());
    })

    test('renders the button with correct text and href if no claimed production locations are available', () => {
        const { getByRole } = renderComponent(ClaimedFacilitiesList);

        const button = getByRole('button', { name: /Find My Production Location/i });
        expect(button).toBeInTheDocument();

        expect(button).toHaveTextContent('Find My Production Location');

        expect(button).toHaveAttribute('href', '/contribute/single-location?tab=name-address');
    });
});

