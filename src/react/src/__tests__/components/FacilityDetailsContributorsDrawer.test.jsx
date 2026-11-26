/*
 * The contributors drawer of the production location page: a
 * contributor links to its profile, an organization is plain text.
 */
import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import { render, screen } from '@testing-library/react';

import FacilityDetailsContributorsDrawer from '../../components/FacilityDetailsContributorsDrawer';
import { splitContributorsIntoPublicAndNonPublic } from '../../util/util';

const contributors = [
    {
        id: 12,
        name: 'Acme Brands (Acme list)',
        contributor_name: 'Acme Brands',
        list_name: 'Acme list',
        is_verified: false,
    },
    {
        id: null,
        is_organization: true,
        name: 'Brand Group (Spring list)',
        contributor_name: 'Brand Group',
        list_name: 'Spring list',
        is_verified: false,
    },
    {
        id: null,
        is_organization: true,
        name: 'Brand Group (Autumn list)',
        contributor_name: 'Brand Group',
        list_name: 'Autumn list',
        is_verified: false,
    },
];

const renderDrawer = () =>
    render(
        <MemoryRouter>
            <FacilityDetailsContributorsDrawer
                open
                onClose={() => {}}
                splittedContributors={splitContributorsIntoPublicAndNonPublic(
                    contributors,
                )}
            />
        </MemoryRouter>,
    );

describe('FacilityDetailsContributorsDrawer', () => {
    test('links a contributor to its profile', () => {
        renderDrawer();

        expect(
            screen.getByRole('link', { name: 'Acme Brands' }),
        ).toHaveAttribute('href', '/profile/12');
    });

    test('shows an organization once, with its lists and no link', () => {
        renderDrawer();

        expect(screen.getAllByText('Brand Group')).toHaveLength(1);
        expect(
            screen.queryByRole('link', { name: 'Brand Group' }),
        ).not.toBeInTheDocument();
        expect(screen.getByText('Spring list')).toBeInTheDocument();
        expect(screen.getByText('Autumn list')).toBeInTheDocument();
        expect(screen.getByText(/Current Contributors \(\s*2\s*\)/)).toBeInTheDocument();
    });
});
