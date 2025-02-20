import React from 'react';
import { Router } from 'react-router-dom';
import history from '../../util/history';
import SearchByOsIdResult from '../../components/Contribute/SearchByOsIdResult';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import {LOG_IN_TITLE} from '../../util/constants';


describe('SearchByOsIdResult component', () => {
    const mockNotAuthorizedState = {
        auth: {
            user: { user: { isAnon: true } },
            session: { fetching: false },
        },
    };

    const renderComponent = (detailOverride, authOverride) => {
        const preloadedState = {
            contributeProductionLocation: {

                singleProductionLocation: {
                    data: {},
                    fetching: false,
                    ...detailOverride,
                },
            },
            auth: {
                user: { user: { isAnon: false } },
                session: { fetching: false },
            },
            ...authOverride,
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

    it('renders for the unauthorized user', () => {
        const  expectedTitle = 'Production Location Search'
        const { getByText, getByRole } = renderComponent({}, mockNotAuthorizedState);
        const linkElement = getByRole('link', { name: /Log in to contribute to Open Supply Hub/i });

        expect(linkElement).toBeInTheDocument();
        expect(linkElement).toHaveAttribute('href', '/auth/login');
        expect(getByText(LOG_IN_TITLE)).toBeInTheDocument();
        expect(getByText(expectedTitle)).toBeInTheDocument();
    });

    it('renders for the authorized user', () => {
        const  expectedTitle = 'Production Location Search'
        const { getByText, getByRole } = renderComponent();
        const title = getByText(expectedTitle);
        const backToIdBtn = getByRole('button', { name: /Back to ID search/i });
        const byNameAndIdBtn = getByRole('button', { name: /Search by Name and Address/i });
        const anotherIdBtn = getByRole('button', { name: /Search for another ID/i });


        expect(title).toBeInTheDocument();
        expect(backToIdBtn).toBeInTheDocument();
        expect(byNameAndIdBtn).toBeInTheDocument();
        expect(anotherIdBtn).toBeInTheDocument();
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
