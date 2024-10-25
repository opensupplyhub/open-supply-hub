import React from 'react';
import { fireEvent } from '@testing-library/react';
import { BrowserRouter as Router } from 'react-router-dom';
import DashboardModerationQueueListTable from '../../components/Dashboard/DashboardModerationQueueListTable';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import { EMPTY_PLACEHOLDER } from '../../util/constants';
import { formatDate } from '../../util/util';

describe('DashboardModerationQueueListTable component', () => {
    const sampleModerationEvents = [
        {
            moderation_id: 1,
            created_at: '2024-09-12T10:26:10.277Z',
            name: 'Generic Soft Inc',
            country: {
                name: 'United States',
                alpha_2: 'US',
                alpha_3: 'USA',
                numeric: '840',
            },
            contributor_name: 'International Business Machines',
            moderation_status: 'RESOLVED',
            moderation_decision_date: '2024-09-13T10:26:10.277Z',
            updated_at: '2024-09-14T10:26:10.277Z',
            source: 'API',
        },
        {
            moderation_id: 3,
            created_at: '2024-10-14T10:26:10.277Z',
            name: 'Printing materials factory',
            country: {
                name: 'Italy',
                alpha_2: 'IT',
                alpha_3: 'ITA',
                numeric: '380',
            },
            contributor_name: 'Global Printing',
            moderation_status: 'PENDING',
            moderation_decision_date: null,
            updated_at: '2024-10-15T10:26:10.277Z',
            source: 'SLC',
        },
    ];

    const paginatedModerationEvents = [
        {
            moderation_id: 1,
            created_at: '2024-10-17T10:26:10.277Z',
            name: 'Generic Soft Inc',
            country: {
                name: 'United States',
                alpha_2: 'US',
                alpha_3: 'USA',
                numeric: '840',
            },
            contributor_name: 'International Business Machines',
            moderation_status: 'RESOLVED',
            moderation_decision_date: '2024-10-17T10:26:10.277Z',
            updated_at: '2024-10-17T10:26:10.277Z',
            source: 'API',
        },
        {
            moderation_id: 2,
            created_at: '2024-10-17T10:26:10.277Z',
            name: 'Sporting Goods Manufacturer',
            country: {
                name: 'United States',
                alpha_2: 'US',
                alpha_3: 'USA',
                numeric: '840',
            },
            contributor_name: 'General Services',
            moderation_status: 'PENDING',
            moderation_decision_date: '2024-10-17T10:26:10.277Z',
            updated_at: '2024-10-17T10:26:10.277Z',
            source: 'SLC',
        },
        {
            moderation_id: 3,
            created_at: '2024-10-17T10:26:10.277Z',
            name: 'Printing materials factory',
            country: {
                name: 'Italy',
                alpha_2: 'IT',
                alpha_3: 'ITA',
                numeric: '380',
            },
            contributor_name: 'Global Printing',
            moderation_status: 'PENDING',
            moderation_decision_date: '2024-10-17T10:26:10.277Z',
            updated_at: '2024-10-17T10:26:10.277Z',
            source: 'API',
        },
        {
            moderation_id: 4,
            created_at: '2024-10-17T10:26:10.277Z',
            name: 'Textile Machinery',
            country: {
                name: 'Canada',
                alpha_2: 'CA',
                alpha_3: 'CAN',
                numeric: '124',
            },
            contributor_name: 'International Business Machines',
            moderation_status: 'RESOLVED',
            moderation_decision_date: '2024-10-17T10:26:10.277Z',
            updated_at: '2024-10-17T10:26:10.277Z',
            source: 'SLC',
        },
        {
            moderation_id: 5,
            created_at: '2024-10-17T10:26:10.277Z',
            name: 'Sporting Goods and Equipment Inc',
            country: {
                name: 'United States',
                alpha_2: 'US',
                alpha_3: 'USA',
                numeric: '840',
            },
            contributor_name: 'Sport Services',
            moderation_status: 'PENDING',
            moderation_decision_date: '2024-10-17T10:26:10.277Z',
            updated_at: '2024-10-17T10:26:10.277Z',
            source: 'API',
        },
        {
            moderation_id: 6,
            created_at: '2024-10-17T10:26:10.277Z',
            name: 'Printing materials factory',
            country: {
                name: 'Italy',
                alpha_2: 'IT',
                alpha_3: 'ITA',
                numeric: '380',
            },
            contributor_name: 'Global Printing',
            moderation_status: 'PENDING',
            moderation_decision_date: '2024-10-17T10:26:10.277Z',
            updated_at: '2024-10-17T10:26:10.277Z',
            source: 'SLC',
        },
    ];


    const defaultProps = {
        events: [],
        fetching: false,
    };

    const renderComponent = (props = {}) => {
        return renderWithProviders(
            <Router>
                <DashboardModerationQueueListTable {...defaultProps} {...props} />,
            </Router>
        );
    }

    test('renders loading indicator when fetching', () => {
        const { getByRole } = renderComponent({ fetching: true });

        expect(getByRole('progressbar')).toBeInTheDocument();
    });

    test('renders event data in rows', () => {
        const { getByText } = renderComponent({ events: sampleModerationEvents });

        sampleModerationEvents.forEach(event => {
            expect(getByText(event.name)).toBeInTheDocument();
            expect(getByText(formatDate(event.created_at, 'LL'))).toBeInTheDocument();
            expect(getByText(event.country.name)).toBeInTheDocument();
            expect(getByText(event.contributor_name)).toBeInTheDocument();
            expect(getByText(event.source)).toBeInTheDocument();
            expect(getByText(event.moderation_status)).toBeInTheDocument();

            const decisionDate = event.moderation_decision_date
            ? formatDate(event.moderation_decision_date, 'LL')
            : EMPTY_PLACEHOLDER;
            expect(getByText(decisionDate)).toBeInTheDocument();
        });
    });

    test('handles rows per page change', () => {
        const { getByText } = renderComponent({ events: paginatedModerationEvents });

        expect(getByText(/1-5 of \d+/)).toBeInTheDocument();
        expect(getByText(/rows per page/i)).toBeInTheDocument();
        
        fireEvent.click(getByText('5'));
        fireEvent.click(getByText('10'));
        expect(getByText(/1-\d+ of \d+/)).toBeInTheDocument();
    });

    test('handles page change', () => {
        const { getByText, getByRole} = renderComponent({ events: paginatedModerationEvents });

        expect(getByText(/1-5 of \d+/)).toBeInTheDocument();
        const nextPageButton = getByRole('button', { name: /next page/i });
        fireEvent.click(nextPageButton);
        expect(getByText(/6-\d+ of \d+/)).toBeInTheDocument();
        const previousPageButton = getByRole('button', { name: /previous page/i });
        fireEvent.click(previousPageButton);
        expect(getByText(/1-5 of \d+/)).toBeInTheDocument();
    });
});
