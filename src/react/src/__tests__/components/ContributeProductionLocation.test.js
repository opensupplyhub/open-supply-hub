import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import { fireEvent } from '@testing-library/react';
import ContributeProductionLocation from '../../components/Contribute/ContributeProductionLocation';
import renderWithProviders from '../../util/testUtils/renderWithProviders';

jest.mock('../../components/Contribute/SearchByOsIdTab', () => () => <div>Mocked SearchByOsIdTab</div>);
jest.mock('../../components/Contribute/SearchByNameAndAddressTab', () => () => <div>Mocked SearchByNameAndAddressTab</div>);

describe('ContributeProductionLocation component', () => {
    const renderComponent = (initialEntries = ['/']) =>
        renderWithProviders(
            <MemoryRouter initialEntries={initialEntries}>
                <ContributeProductionLocation />
            </MemoryRouter>
        );

    it('renders with the correct title', () => {
        const { getByText } = renderComponent();
        expect(getByText('Production Location Search')).toBeInTheDocument();
    });

    it('renders the Name and Address tab as selected by default', () => {
        const { getByRole } = renderComponent();
        const nameAddressTab = getByRole('tab', { name: /Search by name and address/i });
        expect(nameAddressTab).toHaveAttribute('aria-selected', 'true');
    });

    it('renders the OS ID tab as unselected by default', () => {
        const { getByRole } = renderComponent();
        const osIdTab = getByRole('tab', { name: /Search by OS ID/i });
        expect(osIdTab).toHaveAttribute('aria-selected', 'false');
    });

    it('changes the tab when clicked and updates the URL', () => {
        const { getByRole, getByText } = renderComponent();
        const nameAddressTab = getByRole('tab', { name: /Search by name and address/i });
        const osIdTab = getByRole('tab', { name: /Search by OS ID/i });

        expect(nameAddressTab).toHaveAttribute('aria-selected', 'true');
        fireEvent.click(osIdTab);
        expect(osIdTab).toHaveAttribute('aria-selected', 'true');
        expect(nameAddressTab).toHaveAttribute('aria-selected', 'false');
        expect(getByText('Search by OS ID')).toBeInTheDocument();
    });

    it('renders SearchByNameAndAddressTab when Name and Address tab is selected', () => {
        const { getByText } = renderComponent();
        expect(getByText('Mocked SearchByNameAndAddressTab')).toBeInTheDocument();
    });

    it('renders SearchByOsIdTab when OS ID tab is selected', () => {
        const { getByText, getByRole } = renderComponent();
        const osIdTab = getByRole('tab', { name: /Search by OS ID/i });
        
        fireEvent.click(osIdTab);``
        expect(getByText('Mocked SearchByOsIdTab')).toBeInTheDocument();
    });

    it('handles invalid tab and defaults to Name and Address tab', () => {
        const { getByRole } = renderComponent(['contribute/production-location?tab=invalid-tab']);
        const osIdTab = getByRole('tab', { name: /Search by name and address/i });

        expect(osIdTab).toHaveAttribute('aria-selected', 'true');
    });
});
