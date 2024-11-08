import React from 'react';
import { fireEvent } from '@testing-library/react';
import { BrowserRouter as Router } from 'react-router-dom';
import DashboardModerationQueueListTable from '../../components/Dashboard/DashboardModerationQueueListTable';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import { EMPTY_PLACEHOLDER, DATE_FORMATS } from '../../util/constants';
import { formatDate } from '../../util/util';

describe('DashboardModerationQueueListTable component', () => {
    const sampleModerationEvents = [
        {
            moderation_id: 11,
            created_at: '2024-10-17T11:30:20.287Z',
            name: 'Eco Friendly Plastics',
            country: {
                name: 'Germany',
                alpha_2: 'DE',
                alpha_3: 'DEU',
                numeric: '276',
            },
            contributor_name: 'Green Solutions Corp',
            moderation_status: 'PENDING',
            moderation_decision_date: null,
            updated_at: '2024-10-18T11:30:20.287Z',
            source: 'SLC',
        },
        {
            moderation_id: 12,
            created_at: '2024-10-10T12:45:30.297Z',
            name: 'Solar Energy Systems Ltd',
            country: {
                name: 'France',
                alpha_2: 'FR',
                alpha_3: 'FRA',
                numeric: '250',
            },
            contributor_name: 'Renewable Resources Inc',
            moderation_status: 'APPROVED',
            moderation_decision_date: '2024-10-12T12:45:30.297Z',
            updated_at: '2024-10-13T12:45:30.297Z',
            source: 'API',
        },
    ];
    const paginatedModerationEvents = [
        ...sampleModerationEvents,
        {
            moderation_id: 13,
            created_at: '2024-10-15T09:10:20.287Z',
            name: 'Organic Textiles',
            country: {
                name: 'Spain',
                alpha_2: 'ES',
                alpha_3: 'ESP',
                numeric: '724',
            },
            contributor_name: 'Textile Innovations',
            moderation_status: 'REJECTED',
            moderation_decision_date: '2024-10-15T09:10:20.287Z',
            updated_at: '2024-10-15T09:10:20.287Z',
            source: 'API',
        },
        {
            moderation_id: 14,
            created_at: '2024-10-16T13:25:40.317Z',
            name: 'High Tech Components',
            country: {
                name: 'Japan',
                alpha_2: 'JP',
                alpha_3: 'JPN',
                numeric: '392',
            },
            contributor_name: 'Advanced Manufacturing Co',
            moderation_status: 'APPROVED',
            moderation_decision_date: '2024-10-16T13:25:40.317Z',
            updated_at: '2024-10-16T13:25:40.317Z',
            source: 'API',
        },
        {
            moderation_id: 15,
            created_at: '2024-10-17T07:18:50.327Z',
            name: 'Bio-Textile Solutions',
            country: {
                name: 'Sweden',
                alpha_2: 'SE',
                alpha_3: 'SWE',
                numeric: '752',
            },
            contributor_name: 'Eco-Friendly Fabrics',
            moderation_status: 'PENDING',
            moderation_decision_date: '2024-10-17T07:18:50.327Z',
            updated_at: '2024-10-17T07:18:50.327Z',
            source: 'SLC',
        },
        {
            moderation_id: 16,
            created_at: '2024-10-18T15:45:00.337Z',
            name: 'CleanTech Machinery',
            country: {
                name: 'Australia',
                alpha_2: 'AU',
                alpha_3: 'AUS',
                numeric: '036',
            },
            contributor_name: 'Sustainable Machines',
            moderation_status: 'APPROVED',
            moderation_decision_date: '2024-10-18T15:45:00.337Z',
            updated_at: '2024-10-18T15:45:00.337Z',
            source: 'API',
        },
    ];

    const defaultProps = {
        events: [],
        fetching: false,
    };

    const renderComponent = (props = {}) => renderWithProviders(
        <Router>
            <DashboardModerationQueueListTable {...defaultProps} {...props} />,
        </Router>
    );

    test('renders loading indicator when fetching', () => {
        const { getByRole } = renderComponent({ fetching: true });

        expect(getByRole('progressbar')).toBeInTheDocument();
    });

    test('renders event data in rows', () => {
        const { getByText } = renderComponent({ events: sampleModerationEvents });

        sampleModerationEvents.forEach(event => {
            expect(getByText(event.name)).toBeInTheDocument();
            expect(getByText(formatDate(event.created_at, DATE_FORMATS.LONG))).toBeInTheDocument();
            expect(getByText(event.country.name)).toBeInTheDocument();
            expect(getByText(event.contributor_name)).toBeInTheDocument();
            expect(getByText(event.source)).toBeInTheDocument();
            expect(getByText(event.moderation_status)).toBeInTheDocument();

            const decisionDate = event.moderation_decision_date
            ? formatDate(event.moderation_decision_date, DATE_FORMATS.LONG)
            : EMPTY_PLACEHOLDER;
            expect(getByText(decisionDate)).toBeInTheDocument();
        });
    });

    test('handles rows per page change', () => {
        const { getByText } = renderComponent({ events: paginatedModerationEvents });

        expect(getByText(/1-5 of 6/)).toBeInTheDocument();
        expect(getByText(/rows per page/i)).toBeInTheDocument();
        fireEvent.click(getByText('5'));
        fireEvent.click(getByText('10'));
        expect(getByText(/1-6 of 6/)).toBeInTheDocument();
    });

    test('handles page change', () => {
        const { getByText, getByRole} = renderComponent({ events: paginatedModerationEvents });

        expect(getByText(/1-5 of 6/)).toBeInTheDocument();
        const nextPageButton = getByRole('button', { name: /next page/i });
        fireEvent.click(nextPageButton);
        expect(getByText(/6-6 of 6/)).toBeInTheDocument();
        const previousPageButton = getByRole('button', { name: /previous page/i });
        fireEvent.click(previousPageButton);
        expect(getByText(/1-5 of 6/)).toBeInTheDocument();
    });

    test('handles empty state pagination', () => {
        const { getByText } = renderComponent({ events: [] });
        expect(getByText(/0-0 of 0/)).toBeInTheDocument();
    });
});
