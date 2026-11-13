/*
 * The My Organization page, opened from the account menu: who is asked
 * to log in, and that a signed-in user gets the organization content
 * under the page title.
 */
import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import { screen } from '@testing-library/react';

import apiRequest from '../../util/apiRequest';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import OrganizationPage from '../../components/Organization/OrganizationPage';

jest.mock('../../util/apiRequest', () => ({
    __esModule: true,
    default: { get: jest.fn() },
}));

const signedInState = {
    auth: {
        user: { user: { isAnon: false, id: 2, email: 'member@brand.example' } },
        session: { fetching: false },
    },
};

const notFound = () =>
    Promise.reject(
        Object.assign(new Error('Not Found'), { response: { status: 404 } }),
    );

const renderPage = (preloadedState = signedInState) =>
    renderWithProviders(
        <MemoryRouter>
            <OrganizationPage />
        </MemoryRouter>,
        { preloadedState },
    );

describe('OrganizationPage', () => {
    beforeEach(() => {
        apiRequest.get.mockReset();
    });

    test('asks an anonymous visitor to log in and fetches nothing', () => {
        renderPage({});

        expect(
            screen.getByText('Log in to see your organization'),
        ).toBeInTheDocument();
        expect(screen.queryByTestId('organization-tab')).toBeNull();
        expect(apiRequest.get).not.toHaveBeenCalled();
    });

    test('waits for the session before deciding what to show', () => {
        renderPage({
            auth: {
                user: { user: { isAnon: true } },
                session: { fetching: true },
            },
        });

        expect(
            screen.queryByText('Log in to see your organization'),
        ).toBeNull();
        expect(apiRequest.get).not.toHaveBeenCalled();
    });

    test('shows a signed-in user the organization content under its title', async () => {
        apiRequest.get.mockImplementation(url =>
            url.startsWith('/api/organizations/current/')
                ? notFound()
                : Promise.resolve({ data: [] }),
        );

        renderPage();

        expect(
            await screen.findByTestId('organization-tab'),
        ).toBeInTheDocument();
        expect(screen.getByText('My Organization')).toBeInTheDocument();
        expect(
            screen.getByText(/You don't belong to an organization/),
        ).toBeInTheDocument();
    });
});
