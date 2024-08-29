import React from 'react';
import { screen } from '@testing-library/react';
import { BrowserRouter as Router } from 'react-router-dom';
import DashboardClaimsDetails from '../../components/DashboardClaimsDetails';
import renderWithProviders from '../../util/testUtils/renderWithProviders';

describe('DashboardClaimsDetails component', () => {
    const routeProps = {
        match: {
            params: {
                id: '1',
            },
        },
    };

    const renderComponent = (detailOverride) => {
        const preloadedState = {
            claimFacilityDashboard: {
                detail: {
                    data: null,
                    fetching: false,
                    error: null,
                    ...detailOverride,
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

        return renderWithProviders(
            <Router>
                <DashboardClaimsDetails {...routeProps} />
            </Router>,
            { preloadedState }
        );
    };

    it('renders the loading spinner', () => {
        renderComponent({ fetching: true });

        expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });

    it('renders the error message', () => {
        renderComponent({ error: ['An error occurred'] });

        expect(screen.getByText('An error prevented fetching that facility claim.')).toBeInTheDocument();
    });

    it('renders nothing when data is null', () => {
        const { container } = renderComponent({});

        expect(container.firstChild).toBeNull();
    });

    it('renders the facility data correctly', () => {
        renderComponent({
            data: {
                id: 1,
                created_at: '2021-08-25T12:34:56Z',
                updated_at: '2021-08-25T12:34:56Z',
                facility: {
                    id: '1',
                    properties: {
                        name: 'Example Facility',
                        address: '123 Main St',
                        country_code: 'US',
                        country_name: 'United States',
                    },
                    type: "Feature",
                    geometry: {
                        type: "Point",
                        coordinates: [
                            90.5740474,
                            23.8973734
                        ]
                    }
                },
                contributor: {
                    id: '2',
                    name: 'Test contributor',
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
                status: "PENDING",
                status_change: {
                    status_change_by: '',
                    status_change_date: '',
                    status_change_reason: '',
                },
                sector: ['Agriculture', 'Food & Beverage'],
                linkedin_profile: 'www.linkedin.com',
                facility_website: 'www.facility-web.com',
                facility_description: 'A detailed description here.',
                facility_workers_count: '100-250',
                facility_name_native_language: 'Local Name',
                attachments: [],
                notes: [],
            },
        });

        expect(screen.getByText('Created on August 25, 2021 12:34 PM / Last updated on August 25, 2021 12:34 PM')).toBeInTheDocument();
        expect(screen.getByText('Example Facility')).toBeInTheDocument();
        expect(screen.getByText('Test contributor')).toBeInTheDocument();
        expect(screen.getByText('Jane Smith')).toBeInTheDocument();
        expect(screen.getByText('Manager')).toBeInTheDocument();
        expect(screen.getByText('jane@example.com')).toBeInTheDocument();
        expect(screen.getByText('www.example.com')).toBeInTheDocument();
        expect(screen.getByText('www.facility-web.com')).toBeInTheDocument();
        expect(screen.getByText('www.linkedin.com')).toBeInTheDocument();
        expect(screen.getByText('Agriculture, Food & Beverage')).toBeInTheDocument();
        expect(screen.getByText('100-250')).toBeInTheDocument();
        expect(screen.getByText('Local Name')).toBeInTheDocument();
    });
});
