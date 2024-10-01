import React from 'react';
import { Router } from 'react-router-dom';
import history from '../../util/history';
import SearchByOsIdResult from '../../components/Contribute/SearchByOsIdResult';
import renderWithProviders from '../../util/testUtils/renderWithProviders';


describe('SearchByOsIdResult component', () => {
    
    const renderComponent = (detailOverride) => {
        const preloadedState = {
            contributeProductionLocation: {
                singleProductionLocation: { 
                    data: {}, 
                    fetching: false, 
                    ...detailOverride,
                },
            },
        };
    
        return renderWithProviders(
            <Router history={history}>
                <SearchByOsIdResult />
            </Router>,
            { preloadedState }
        );
    };
    
    beforeEach(() => {
        jest.clearAllMocks();
    });

    it('renders without crashing', () => {
        const {getByText} = renderComponent();

        expect(getByText('Production Location Search')).toBeInTheDocument();
    });

    it('shows loading spinner when fetching is true', () => {
        const {getByRole} = renderComponent({ fetching: true });

        expect(getByRole('progressbar')).toBeInTheDocument();
    });

    it('redirects to search by os id when back button is clicked', () => {
        const {getByText} = renderComponent();
        const backButton = getByText('Back to ID search');

        backButton.click();

        expect(history.location.search).toBe('?tab=os-id');
    });

    it('redirects to search by os id when Search for another ID button is clicked', () => {
        const {getByText} = renderComponent();
        const backButton = getByText('Search for another ID');

        backButton.click();

        expect(history.location.search).toBe('?tab=os-id');
    });

    it('redirects to search by name and address when Search by Name and Address button is clicked', () => {
        const {getByText} = renderComponent();
        const backButton = getByText('Search by Name and Address');

        backButton.click();

        expect(history.location.search).toBe('?tab=name-address');
    });
});
