import React from 'react';
import { waitFor } from '@testing-library/react';
import { screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { BrowserRouter as Router } from 'react-router-dom';
import DashboardClaimsDetails from '../../components/DashboardClaimsDetails';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import { setupStore } from '../../configureStore';

// Action creators
// import {
//     fetchSingleFacilityClaim,
//     clearSingleFacilityClaim,
// } from '../../actions/claimFacilityDashboard';

const preloadedState = {
    claimFacilityDashboard: {
        detail: {
            data: {
                id: 1,
                created_at: '2021-08-25T12:34:56Z',
                updated_at: '2021-08-25T12:34:56Z',
                facility: {
                    id: '1',
                    properties: {
                        name: 'Example Facility',
                    },
                },
                contributor: {
                    id: '2',
                    name: 'John Doe',
                },
                contact_person: 'Jane Smith',
                job_title: 'Manager',
                email: 'jane@example.com',
                company_name: 'Example Co',
                website: 'www.example.com',
                facility_parent_company: {
                    name: 'Parent Co',
                    id: '3',
                },
                linkedin_profile: 'www.linkedin.com/in/janedoe',
                facility_description: 'A detailed description here.',
                attachments: [],
                notes: [],
            },
            fetching: false,
            error: null,
        },
        note: {
            note: '',
            fetching: false,
            error: null,
        },
        statusControls: {
            fetching: false,
            error: null,
        },
    },
};


describe('DashboardClaimsDetails component', () => {
    const routeProps = {
        match: {
            params: {
                id: '1',
            },
        },
    };
    

    it('renders without crashing and calls data fetching on mount', async () => {
        renderWithProviders(
            <MemoryRouter>
                <DashboardClaimsDetails {...routeProps} />
            </MemoryRouter>,
            // { reduxStore: store }
            { preloadedState }
        );
    });

    it ('renders the loading spinner', () => {
        const state = {
            claimFacilityDashboard: {
                detail: {
                    data: null,
                    fetching: true,
                    error: null,
                },
                note: {
                    note: '',
                    fetching: false,
                    error: null,
                },
                statusControls: {
                    fetching: false,
                    error: null,
                },
            },
        }
        renderWithProviders(
            <MemoryRouter>
                <DashboardClaimsDetails {...routeProps} />
            </MemoryRouter>,
            { state }
        );
        expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });
    

    it('renders the facility data correctly',  () => {
        renderWithProviders(
            <MemoryRouter>
                <DashboardClaimsDetails {...routeProps} />
            </MemoryRouter>,
            // { reduxStore: store }
            { preloadedState }
        );

        expect(screen.getByText('Example Facility')).toBeInTheDocument();
        expect(screen.getByText('John Doe')).toBeInTheDocument();
        expect(screen.getByText('Jane Smith')).toBeInTheDocument();
        expect(screen.getByText('Manager')).toBeInTheDocument();
        expect(screen.getByText('jane@example.com')).toBeInTheDocument();
        expect(screen.getByText('Example Co')).toBeInTheDocument();
        expect(screen.getByText('www.example.com')).toBeInTheDocument();
        expect(screen.getByText('Parent Co')).toBeInTheDocument();
        expect(screen.getByText('www.linkedin.com/in/janedoe')).toBeInTheDocument();
        expect(screen.getByText('A detailed description here.')).toBeInTheDocument();
    });

});
