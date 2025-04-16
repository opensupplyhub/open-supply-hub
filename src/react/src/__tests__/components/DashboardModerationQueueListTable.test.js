import React from 'react';
import { fireEvent } from '@testing-library/react';
import { BrowserRouter as Router } from 'react-router-dom';
import DashboardModerationQueueListTable from '../../components/Dashboard/DashboardModerationQueueListTable';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import { EMPTY_PLACEHOLDER, DATE_FORMATS } from '../../util/constants';
import { formatUTCDate } from '../../util/util';

describe('DashboardModerationQueueListTable component', () => {
    const sampleModerationEventsWithoutStatusChangeDate = [
        {
            moderation_id: 188,
            created_at: '2023-09-16T11:32:20.297Z',
            cleaned_data: {
                name: 'Plastic Test Eco',
                country: {
                    name: 'Greece',
                    alpha_2: 'GR',
                    alpha_3: 'GRC',
                    numeric: '300',
                }
            },
            contributor_name: 'Green Solutions Corp',
            status: 'PENDING',
            updated_at: '2024-10-17T11:31:20.287Z',
            source: 'SLC',
        },
        {
            moderation_id: 189,
            created_at: '2023-08-09T12:44:18.297Z',
            cleaned_data: {
                name: 'Winds Systems Energy Ltd',
                country: {
                    name: 'Greenland',
                    alpha_2: 'GL',
                    alpha_3: 'GRL',
                    numeric: '304',
                }
            },
            contributor_name: 'New Resources Corp',
            status: 'PENDING',
            updated_at: '2023-11-12T12:46:30.297Z',
            source: 'API',
        },
    ];

    const sampleModerationEvents = [
        {
            moderation_id: 11,
            created_at: '2024-10-17T11:30:20.287Z',
            cleaned_data: {
                name: 'Eco Friendly Plastics',
                country: {
                    name: 'Germany',
                    alpha_2: 'DE',
                    alpha_3: 'DEU',
                    numeric: '276',
                }
            },
            contributor_name: 'Green Solutions Corp',
            status: 'PENDING',
            updated_at: '2024-10-18T11:30:20.287Z',
            source: 'SLC',
        },
        {
            moderation_id: 12,
            created_at: '2024-10-10T12:45:30.297Z',
            cleaned_data: {
                name: 'Solar Energy Systems Ltd',
                country: {
                    name: 'France',
                    alpha_2: 'FR',
                    alpha_3: 'FRA',
                    numeric: '250',
                }
            },
            contributor_name: 'Renewable Resources Inc',
            status: 'APPROVED',
            status_change_date: '2024-10-12T12:45:30.297Z',
            updated_at: '2024-10-13T12:45:30.297Z',
            source: 'API',
        },
    ];

    const paginatedModerationEvents = [
        ...sampleModerationEvents,
        {
            moderation_id: 13,
            created_at: '2024-10-15T09:10:20.287Z',
            cleaned_data: {
                name: 'Organic Textiles',
                country: {
                    name: 'Spain',
                    alpha_2: 'ES',
                    alpha_3: 'ESP',
                    numeric: '724',
                }
            },
            contributor_name: 'Textile Innovations',
            status: 'REJECTED',
            status_change_date: '2024-10-15T09:10:20.287Z',
            updated_at: '2024-10-15T09:10:20.287Z',
            source: 'API',
        },
        {
            moderation_id: 14,
            created_at: '2024-10-16T13:25:40.317Z',
            cleaned_data: {
                name: 'High Tech Components',
                country: {
                    name: 'Japan',
                    alpha_2: 'JP',
                    alpha_3: 'JPN',
                    numeric: '392',
                }
            },
            contributor_name: 'Advanced Manufacturing Co',
            status: 'APPROVED',
            status_change_date: '2024-10-16T13:25:40.317Z',
            updated_at: '2024-10-16T13:25:40.317Z',
            source: 'API',
        },
        {
            moderation_id: 15,
            created_at: '2024-10-17T07:18:50.327Z',
            cleaned_data: {
                name: 'Bio-Textile Solutions',
                country: {
                    name: 'Sweden',
                    alpha_2: 'SE',
                    alpha_3: 'SWE',
                    numeric: '752',
                }
            },
            contributor_name: 'Eco-Friendly Fabrics',
            status: 'PENDING',
            status_change_date: '2024-10-17T07:18:50.327Z',
            updated_at: '2024-10-17T07:18:50.327Z',
            source: 'SLC',
        },
        {
            moderation_id: 16,
            created_at: '2024-10-18T15:45:00.337Z',
            cleaned_data: {
                name: 'CleanTech Machinery',
                country: {
                    name: 'Australia',
                    alpha_2: 'AU',
                    alpha_3: 'AUS',
                    numeric: '036',
                }
            },
            contributor_name: 'Sustainable Machines',
            status: 'APPROVED',
            status_change_date: '2024-10-18T15:45:00.337Z',
            updated_at: '2024-10-18T15:45:00.337Z',
            source: 'API',
        },
        {
            moderation_id: 17,
            created_at: '2024-10-20T06:03:00',
            cleaned_data: {
                name: 'Green Solutions 17',
                country: {
                    name: 'United States',
                    alpha_2: 'US',
                    alpha_3: 'USA',
                    numeric: '840',
                },
            },
            contributor_name: 'Green Manufacturing Ltd',
            status: 'APPROVED',
            status_change_date: '2024-10-20T06:03:00',
            updated_at: '2024-10-20T06:03:00',
            source: 'SLC',
        },
        {
            moderation_id: 18,
            created_at: '2024-10-20T10:51:00',
            cleaned_data: {
                name: 'AI-Driven Solutions 18',
                country: {
                    name: 'France',
                    alpha_2: 'FR',
                    alpha_3: 'FRA',
                    numeric: '250',
                },
            },
            contributor_name: 'AI-Driven Systems',
            status: 'REJECTED',
            status_change_date: '2024-10-20T10:51:00',
            updated_at: '2024-10-20T10:51:00',
            source: 'WEB',
        },
        {
            moderation_id: 19,
            created_at: '2024-10-21T22:51:00',
            cleaned_data: {
                name: 'AI-Driven Solutions 19',
                country: {
                    name: 'Canada',
                    alpha_2: 'CA',
                    alpha_3: 'CAN',
                    numeric: '124',
                },
            },
            contributor_name: 'AI-Driven Systems',
            status: 'REJECTED',
            status_change_date: '2024-10-21T22:51:00',
            updated_at: '2024-10-21T22:51:00',
            source: 'SLC',
        },
        {
            moderation_id: 20,
            created_at: '2024-10-23T04:04:00',
            cleaned_data: {
                name: 'Organic Solutions 20',
                country: {
                    name: 'India',
                    alpha_2: 'IN',
                    alpha_3: 'IND',
                    numeric: '356',
                },
            },
            contributor_name: 'Organic Innovations',
            status: 'APPROVED',
            status_change_date: '2024-10-23T04:04:00',
            updated_at: '2024-10-23T04:04:00',
            source: 'API',
        },
        {
            moderation_id: 21,
            created_at: '2024-10-23T12:34:00',
            cleaned_data: {
                name: 'Green Solutions 21',
                country: {
                    name: 'Germany',
                    alpha_2: 'DE',
                    alpha_3: 'DEU',
                    numeric: '276',
                },
            },
            contributor_name: 'Green Manufacturing Ltd',
            status: 'PENDING',
            status_change_date: '2024-10-23T12:34:00',
            updated_at: '2024-10-23T12:34:00',
            source: 'API',
        },
        {
            moderation_id: 22,
            created_at: '2024-10-24T08:12:00',
            cleaned_data: {
                name: 'Futuristic Solutions 22',
                country: {
                    name: 'China',
                    alpha_2: 'CN',
                    alpha_3: 'CHN',
                    numeric: '156',
                },
            },
            contributor_name: 'Futuristic Textiles',
            status: 'APPROVED',
            status_change_date: '2024-10-24T08:12:00',
            updated_at: '2024-10-24T08:12:00',
            source: 'WEB',
        },
        {
            moderation_id: 23,
            created_at: '2024-10-25T09:45:00',
            cleaned_data: {
                name: 'Eco Solutions 23',
                country: {
                    name: 'Brazil',
                    alpha_2: 'BR',
                    alpha_3: 'BRA',
                    numeric: '076',
                },
            },
            contributor_name: 'Eco Innovations',
            status: 'REJECTED',
            status_change_date: '2024-10-25T09:45:00',
            updated_at: '2024-10-25T09:45:00',
            source: 'API',
        },
        {
            moderation_id: 24,
            created_at: '2024-10-26T11:33:00',
            cleaned_data: {
                name: 'Smart Solutions 24',
                country: {
                    name: 'South Korea',
                    alpha_2: 'KR',
                    alpha_3: 'KOR',
                    numeric: '410',
                },
            },
            contributor_name: 'Smart Machinery Inc',
            status: 'PENDING',
            status_change_date: '2024-10-26T11:33:00',
            updated_at: '2024-10-26T11:33:00',
            source: 'SLC',
        },
        {
            moderation_id: 25,
            created_at: '2024-11-01T09:30:00',
            cleaned_data: {
                name: 'Eco Growth 25',
                country: {
                    name: 'Japan',
                    alpha_2: 'JP',
                    alpha_3: 'JPN',
                    numeric: '392',
                },
            },
            contributor_name: 'Eco-Friendly Fabrics',
            status: 'APPROVED',
            status_change_date: '2024-11-01T09:30:00',
            updated_at: '2024-11-01T09:30:00',
            source: 'API',
        },
        {
            moderation_id: 26,
            created_at: '2024-11-02T11:45:00',
            cleaned_data: {
                name: 'Green Tech 26',
                country: {
                    name: 'Germany',
                    alpha_2: 'DE',
                    alpha_3: 'DEU',
                    numeric: '276',
                },
            },
            contributor_name: 'Green Manufacturing Ltd',
            status: 'REJECTED',
            status_change_date: '2024-11-02T11:45:00',
            updated_at: '2024-11-02T11:45:00',
            source: 'WEB',
        },
        {
            moderation_id: 27,
            created_at: '2024-11-03T13:20:00',
            cleaned_data: {
                name: 'Tech Innovations 27',
                country: {
                    name: 'United Kingdom',
                    alpha_2: 'GB',
                    alpha_3: 'GBR',
                    numeric: '826',
                },
            },
            contributor_name: 'NextGen Components',
            status: 'PENDING',
            status_change_date: '2024-11-03T13:20:00',
            updated_at: '2024-11-03T13:20:00',
            source: 'SLC',
        },
        {
            moderation_id: 28,
            created_at: '2024-11-04T15:00:00',
            cleaned_data: {
                name: 'Solar Tech 28',
                country: {
                    name: 'China',
                    alpha_2: 'CN',
                    alpha_3: 'CHN',
                    numeric: '156',
                },
            },
            contributor_name: 'SolarTech Solutions',
            status: 'APPROVED',
            status_change_date: '2024-11-04T15:00:00',
            updated_at: '2024-11-04T15:00:00',
            source: 'API',
        },
        {
            moderation_id: 29,
            created_at: '2024-11-05T18:25:00',
            cleaned_data: {
                name: 'Futuristic Tech 29',
                country: {
                    name: 'Brazil',
                    alpha_2: 'BR',
                    alpha_3: 'BRA',
                    numeric: '076',
                },
            },
            contributor_name: 'Futuristic Textiles',
            status: 'REJECTED',
            status_change_date: '2024-11-05T18:25:00',
            updated_at: '2024-11-05T18:25:00',
            source: 'SLC',
        },
        {
            moderation_id: 30,
            created_at: '2024-11-06T08:40:00',
            cleaned_data: {
                name: 'CleanTech Machines 30',
                country: {
                    name: 'Australia',
                    alpha_2: 'AU',
                    alpha_3: 'AUS',
                    numeric: '036',
                },
            },
            contributor_name: 'Sustainable Machines',
            status: 'PENDING',
            status_change_date: '2024-11-06T08:40:00',
            updated_at: '2024-11-06T08:40:00',
            source: 'WEB',
        },
        {
            moderation_id: 31,
            created_at: '2024-11-07T10:00:00',
            cleaned_data: {
                name: 'Next Level Growth 31',
                country: {
                    name: 'United States',
                    alpha_2: 'US',
                    alpha_3: 'USA',
                    numeric: '840',
                },
            },
            contributor_name: 'Green Manufacturing Ltd',
            status: 'APPROVED',
            status_change_date: '2024-11-07T10:00:00',
            updated_at: '2024-11-07T10:00:00',
            source: 'API',
        },
        {
            moderation_id: 32,
            created_at: '2024-11-08T12:15:00',
            cleaned_data: {
                name: 'Advanced Tech 32',
                country: {
                    name: 'Canada',
                    alpha_2: 'CA',
                    alpha_3: 'CAN',
                    numeric: '124',
                },
            },
            contributor_name: 'Advanced Manufacturing Co',
            status: 'PENDING',
            status_change_date: '2024-11-08T12:15:00',
            updated_at: '2024-11-08T12:15:00',
            source: 'SLC',
        },
        {
            moderation_id: 33,
            created_at: '2024-11-09T14:50:00',
            cleaned_data: {
                name: 'Future Innovations 33',
                country: {
                    name: 'India',
                    alpha_2: 'IN',
                    alpha_3: 'IND',
                    numeric: '356',
                },
            },
            contributor_name: 'AI-Driven Systems',
            status: 'REJECTED',
            status_change_date: '2024-11-09T14:50:00',
            updated_at: '2024-11-09T14:50:00',
            source: 'WEB',
        },
        {
            moderation_id: 34,
            created_at: '2024-11-10T16:05:00',
            cleaned_data: {
                name: 'Eco Innovations 34',
                country: {
                    name: 'South Korea',
                    alpha_2: 'KR',
                    alpha_3: 'KOR',
                    numeric: '410',
                },
            },
            contributor_name: 'Eco Innovations',
            status: 'APPROVED',
            status_change_date: '2024-11-10T16:05:00',
            updated_at: '2024-11-10T16:05:00',
            source: 'API',
        },
        {
            moderation_id: 35,
            created_at: '2024-11-11T18:45:00',
            cleaned_data: {
                name: 'Tech Forward 35',
                country: {
                    name: 'France',
                    alpha_2: 'FR',
                    alpha_3: 'FRA',
                    numeric: '250',
                },
            },
            contributor_name: 'Futuristic Textiles',
            status: 'REJECTED',
            status_change_date: '2024-11-11T18:45:00',
            updated_at: '2024-11-11T18:45:00',
            source: 'SLC',
        },
        {
            moderation_id: 36,
            created_at: '2024-11-11T18:45:00',
            cleaned_data: {
                name: 'Tech Forward 36',
                country: {
                    name: 'France',
                    alpha_2: 'FR',
                    alpha_3: 'FRA',
                    numeric: '250',
                },
            },
            contributor_name: 'Futuristic Textiles',
            status: 'REJECTED',
            status_change_date: '2024-11-11T18:45:00',
            updated_at: '2024-11-11T18:45:00',
            source: 'SLC',
        }
    ];

    const defaultProps = {
        events: [],
        count: 0,
        fetching: false,
        fetchEvents: jest.fn(),
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
        const { getByText } = renderComponent({ moderationEventsList: sampleModerationEvents, count: 2 });

        sampleModerationEvents.forEach(event => {
            expect(getByText(event.cleaned_data.name)).toBeInTheDocument();
            expect(getByText(formatUTCDate(event.created_at, DATE_FORMATS.LONG))).toBeInTheDocument();
            expect(getByText(event.cleaned_data.country.name)).toBeInTheDocument();
            expect(getByText(event.contributor_name)).toBeInTheDocument();
            expect(getByText(event.source)).toBeInTheDocument();
            expect(getByText(event.status)).toBeInTheDocument();

            const decisionDate = event.status_change_date
            ? formatUTCDate(event.status_change_date, DATE_FORMATS.LONG)
            : EMPTY_PLACEHOLDER;
            expect(getByText(decisionDate)).toBeInTheDocument();
        });
    });

    test('if no status_change_date displays N/A', () => {
        const { getAllByText } = renderComponent({ moderationEventsList: sampleModerationEventsWithoutStatusChangeDate, count: 2});

        const elements = getAllByText(EMPTY_PLACEHOLDER);
        expect(elements).toHaveLength(2);
    });

    test('handles rows per page change', () => {
        const { getByText, rerender } = renderComponent({ moderationEventsList: paginatedModerationEvents, count: 26 });

        expect(getByText(/1-25 of 26/)).toBeInTheDocument();
        expect(getByText(/rows per page/i)).toBeInTheDocument();

        fireEvent.click(getByText('25'));
        fireEvent.click(getByText('50'));

        rerender(
            <Router>
                <DashboardModerationQueueListTable moderationEventsList={paginatedModerationEvents} count={26} pageSize={50}/>,
            </Router>
        )
        expect(getByText(/1-26 of 26/)).toBeInTheDocument();
    });

    test('handles page change', () => {
        const { getByText, getByRole, rerender } = renderComponent({ events: paginatedModerationEvents.slice(0, 25), count: 26});
        expect(getByText(/1-25 of 26/)).toBeInTheDocument();

        const nextPageButton = getByRole('button', { name: /next page/i });
        fireEvent.click(nextPageButton);

        rerender(
            <Router>
                <DashboardModerationQueueListTable moderationEventsList={paginatedModerationEvents} count={26} page={1} fetchEvents={jest.fn()}/>,
            </Router>
        )
        expect(getByText(/26-26 of 26/)).toBeInTheDocument();

        const previousPageButton = getByRole('button', { name: /previous page/i });
        fireEvent.click(previousPageButton);

        rerender(
            <Router>
                <DashboardModerationQueueListTable moderationEventsList={paginatedModerationEvents} count={26} page={0} fetchEvents={jest.fn()}/>,
            </Router>
        )
        expect(getByText(/1-25 of 26/)).toBeInTheDocument();
    });

    test('handles empty state pagination', () => {
        const { getByText } = renderComponent({ moderationEventsList: [] });
        expect(getByText(/0-0 of 0/)).toBeInTheDocument();
    });
});
