import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import { fireEvent } from '@testing-library/react';
import ContributeProductionLocation from '../../components/Contribute/ContributeProductionLocation';
import renderWithProviders from '../../util/testUtils/renderWithProviders';

jest.mock('../../components/Contribute/SearchByOsIdTab', () => () => <div>Mocked SearchByOsIdTab</div>);
jest.mock('../../components/Contribute/SearchByNameAndAddressTab', () => () => <div>Mocked SearchByNameAndAddressTab</div>);

describe('ContributeProductionLocation component', () => {
    const mockAuthorizedState = {
        auth: {
            user: { user: { isAnon: false } },
            session: { fetching: false },
        },
    };

    const mockNotAuthorizedState = {
        auth: {
            user: { user: { isAnon: true } },
            session: { fetching: false },
        },
    };

    const renderComponent = (preloadedState = {},initialEntries = ['/']) =>
        renderWithProviders(
            <MemoryRouter initialEntries={initialEntries}>
                <ContributeProductionLocation />
            </MemoryRouter>,
            { preloadedState }
        );

    beforeEach(() => {
        jest.clearAllMocks();
    });

    it('renders for the unauthorized user', () => {
        const  expectedTitle = 'Production Location Search'
        const { getByText, getByRole } = renderComponent(mockNotAuthorizedState);
        const linkElement = getByRole('link', { name: /Log in to contribute to Open Supply Hub/i });

        expect(linkElement).toBeInTheDocument();
        expect(linkElement).toHaveAttribute('href', '/auth/login');
        expect(getByText('Log in to contribute to Open Supply Hub')).toBeInTheDocument();
        expect(getByText(expectedTitle)).toBeInTheDocument();
    });

    it('renders for the authorized user', () => {
        const  expectedTitle = 'Production Location Search'
        const { getByText, getByRole } = renderComponent(mockAuthorizedState);
        const title = getByText(expectedTitle);
        const nameAddressTab = getByRole('tab', { name: /Search by name and address/i });
        const osIdTab = getByRole('tab', { name: /Search by OS ID/i });

        expect(title).toBeInTheDocument();
        expect(nameAddressTab).toBeInTheDocument();
        expect(osIdTab).toBeInTheDocument();
    });

    it('renders with the correct title', () => {
        const { getByText } = renderComponent(mockAuthorizedState);
        expect(getByText('Production Location Search')).toBeInTheDocument();
    });

    it('renders the Name and Address tab as selected by default', () => {
        const { getByRole } = renderComponent(mockAuthorizedState);
        const nameAddressTab = getByRole('tab', { name: /Search by name and address/i });
        expect(nameAddressTab).toHaveAttribute('aria-selected', 'true');
    });

    it('renders the OS ID tab as unselected by default', () => {
        const { getByRole } = renderComponent(mockAuthorizedState);
        const osIdTab = getByRole('tab', { name: /Search by OS ID/i });
        expect(osIdTab).toHaveAttribute('aria-selected', 'false');
    });

    it('changes the tab when clicked and updates the URL', () => {
        const { getByRole, getByText } = renderComponent(mockAuthorizedState);
        const nameAddressTab = getByRole('tab', { name: /Search by name and address/i });
        const osIdTab = getByRole('tab', { name: /Search by OS ID/i });

        expect(nameAddressTab).toHaveAttribute('aria-selected', 'true');
        fireEvent.click(osIdTab);
        expect(osIdTab).toHaveAttribute('aria-selected', 'true');
        expect(nameAddressTab).toHaveAttribute('aria-selected', 'false');
        expect(getByText('Search by OS ID')).toBeInTheDocument();
    });

    it('renders SearchByNameAndAddressTab when Name and Address tab is selected', () => {
        const { getByText } = renderComponent(mockAuthorizedState);
        expect(getByText('Mocked SearchByNameAndAddressTab')).toBeInTheDocument();
    });

    it('renders SearchByOsIdTab when OS ID tab is selected', () => {
        const { getByText, getByRole } = renderComponent(mockAuthorizedState);
        const osIdTab = getByRole('tab', { name: /Search by OS ID/i });
        
        fireEvent.click(osIdTab);
        expect(getByText('Mocked SearchByOsIdTab')).toBeInTheDocument();
    });

    it('handles invalid tab and defaults to Name and Address tab', () => {
        const { getByRole } = renderComponent(mockAuthorizedState, ['contribute/production-location?tab=invalid-tab']);
        const osIdTab = getByRole('tab', { name: /Search by name and address/i });

        expect(osIdTab).toHaveAttribute('aria-selected', 'true');
    });
});
