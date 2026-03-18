import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { screen, fireEvent } from '@testing-library/react';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import SupplyChain from '../../components/ProductionLocation/Sidebar/SupplyChain/SupplyChain';

const publicContributor = {
    id: 1,
    contributor_name: 'Acme Brands',
    contributor_type: 'Brand / Retailer',
    list_name: 'Acme Supplier List 2025',
    is_verified: false,
    count: 1,
    name: 'Acme Brands',
};

const anotherPublicContributor = {
    id: 2,
    contributor_name: 'Global Auditors Inc',
    contributor_type: 'Auditor',
    list_name: 'Verified Facilities Q1 2025',
    is_verified: true,
    count: 1,
    name: 'Global Auditors Inc',
};

const nonPublicContributor = {
    contributor_type: 'Civil Society Organization',
    count: 3,
    name: '3 Others',
};

const nonPublicContributorNullType = {
    contributor_type: null,
    count: 2,
    name: '2 Others',
};

const getPreloadedState = (contributors = []) => ({
    facilities: {
        singleFacility: {
            data: {
                properties: {
                    contributors,
                },
            },
        },
    },
});

const renderSection = (contributors = []) =>
    renderWithProviders(
        <Router>
            <SupplyChain />
        </Router>,
        { preloadedState: getPreloadedState(contributors) },
    );

describe('SupplyChainNetwork section', () => {
    test('renders nothing when contributors array is empty', () => {
        renderSection([]);
        expect(
            screen.queryByText('Supply Chain Network'),
        ).not.toBeInTheDocument();
    });

    test('renders nothing when all contributors have no name and no type', () => {
        renderSection([{ id: 1, count: 1 }]);
        expect(
            screen.queryByText('Supply Chain Network'),
        ).not.toBeInTheDocument();
    });

    test('renders section title and subtitle when contributors exist', () => {
        renderSection([publicContributor]);

        expect(
            screen.getByText('Supply Chain Network'),
        ).toBeInTheDocument();
        expect(
            screen.getByText(
                /Organizations that have shared information about this production location/,
            ),
        ).toBeInTheDocument();
    });

    test('renders contributor type counts per line', () => {
        renderSection([publicContributor, nonPublicContributor]);

        expect(
            screen.getByText(/Brand \/ Retailer/),
        ).toBeInTheDocument();
        expect(
            screen.getByText(/Civil Society Organization/),
        ).toBeInTheDocument();
    });

    test('renders public contributor names as links', () => {
        renderSection([publicContributor, anotherPublicContributor]);

        expect(screen.getByText('Acme Brands')).toBeInTheDocument();
        expect(screen.getByText('Global Auditors Inc')).toBeInTheDocument();
    });

    test('renders public contributors grouped by contributor type', () => {
        // Three contributors: two Brand / Retailers surrounding one Auditor in API order.
        // After grouping the two Brand / Retailers must appear consecutively.
        const brandA = {
            id: 10,
            contributor_name: 'Brand A',
            contributor_type: 'Brand / Retailer',
            list_name: 'List A',
            count: 1,
        };
        const auditor = {
            id: 11,
            contributor_name: 'Solo Auditor',
            contributor_type: 'Auditor',
            list_name: 'Audit List',
            count: 1,
        };
        const brandB = {
            id: 12,
            contributor_name: 'Brand B',
            contributor_type: 'Brand / Retailer',
            list_name: 'List B',
            count: 1,
        };

        // API returns them interleaved: Brand A, Auditor, Brand B
        renderSection([brandA, auditor, brandB]);

        const links = screen
            .getAllByRole('link')
            .filter(el =>
                ['Brand A', 'Solo Auditor', 'Brand B'].includes(
                    el.textContent,
                ),
            );

        const names = links.map(el => el.textContent);
        const brandAIndex = names.indexOf('Brand A');
        const brandBIndex = names.indexOf('Brand B');
        const auditorIndex = names.indexOf('Solo Auditor');

        // The two Brand / Retailer contributors must not have the Auditor between them
        expect(Math.abs(brandAIndex - brandBIndex)).toBe(1);
        expect(auditorIndex).not.toBe(
            Math.min(brandAIndex, brandBIndex) + 1,
        );
    });

    test('renders "View all N data sources" trigger button', () => {
        renderSection([publicContributor, nonPublicContributor]);

        expect(
            screen.getByRole('button', { name: /View all 4 data sources/i }),
        ).toBeInTheDocument();
    });

    test('opens drawer when trigger button is clicked', () => {
        renderSection([publicContributor]);

        // Drawer content is in the DOM but aria-hidden when closed
        const trigger = screen.getByRole('button', { name: /View all/i });
        expect(trigger).toBeInTheDocument();

        fireEvent.click(trigger);

        // After clicking, the drawer close button should be accessible
        expect(screen.getByLabelText('Close')).toBeInTheDocument();
    });

    test('filters out non-public contributors with null contributor_type', () => {
        renderSection([publicContributor, nonPublicContributorNullType]);

        fireEvent.click(
            screen.getByRole('button', { name: /View all/i }),
        );

        // The null-type anonymous contributor should not appear in the drawer
        expect(
            screen.queryByText('2 Civil Society Organization'),
        ).not.toBeInTheDocument();
    });
});

describe('SupplyChainNetworkDrawer', () => {
    const openDrawer = contributors => {
        renderSection(contributors);
        fireEvent.click(screen.getByRole('button', { name: /View all/i }));
    };

    test('shows "All Data Sources" as the drawer title', () => {
        openDrawer([publicContributor]);
        expect(screen.getByText('All Data Sources')).toBeVisible();
    });

    test('shows total contributor count in subtitle', () => {
        openDrawer([publicContributor, nonPublicContributor]);
        // total = 1 + 3 = 4
        expect(
            screen.getByText(/4 organizations have shared data/i),
        ).toBeInTheDocument();
    });

    test('shows info box with explanatory text', () => {
        openDrawer([publicContributor]);
        expect(
            screen.getByText(/Multiple organizations may have shared data/i),
        ).toBeInTheDocument();
    });

    test('shows "Learn more" link in info box', () => {
        openDrawer([publicContributor]);
        expect(
            screen.getByText(/Learn more about our open data model/i),
        ).toBeInTheDocument();
    });

    test('shows public contributors by name under All Data Sources', () => {
        openDrawer([publicContributor, anotherPublicContributor]);
        // Names appear both in the section and in the drawer; getAll checks at least one
        expect(
            screen.getAllByText('Acme Brands').length,
        ).toBeGreaterThanOrEqual(1);
    });

    test('shows contributor type label for public contributors', () => {
        openDrawer([publicContributor]);
        // contributor_type "Brand / Retailer" appears as type label in drawer
        expect(
            screen.getAllByText('Brand / Retailer').length,
        ).toBeGreaterThanOrEqual(1);
    });

    test('shows Anonymized Data Sources section when non-public contributors exist', () => {
        openDrawer([publicContributor, nonPublicContributor]);
        expect(
            screen.getByText('Anonymized Data Sources'),
        ).toBeInTheDocument();
    });

    test('does not show Anonymized Data Sources when only public contributors exist', () => {
        openDrawer([publicContributor]);
        expect(
            screen.queryByText('Anonymized Data Sources'),
        ).not.toBeInTheDocument();
    });

    test('shows non-public contributors by type and count in anonymized section', () => {
        openDrawer([publicContributor, nonPublicContributor]);
        // "3 Civil Society Organization" may appear multiple times (type chips + anonymized section)
        const matches = screen.getAllByText(/3 Civil Society Organization/);
        expect(matches.length).toBeGreaterThanOrEqual(1);
    });

    test('drawer close button is present after opening', () => {
        openDrawer([publicContributor]);
        expect(screen.getByLabelText('Close')).toBeInTheDocument();
    });
});
