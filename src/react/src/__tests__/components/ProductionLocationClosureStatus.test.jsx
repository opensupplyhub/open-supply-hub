import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { screen } from '@testing-library/react';
import PropTypes from 'prop-types';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import ClosureStatus from '../../components/ProductionLocation/Heading/ClosureStatus/ClosureStatus';

jest.mock('../../components/FeatureFlag', () => {
    const MockFeatureFlag = ({ children }) => <>{children}</>;
    MockFeatureFlag.propTypes = { children: PropTypes.node };
    MockFeatureFlag.defaultProps = { children: null };
    return MockFeatureFlag;
});

describe('ProductionLocation ClosureStatus', () => {
    const clearFacility = jest.fn();

    afterEach(() => {
        jest.clearAllMocks();
    });

    test('returns null when there is no activity report', () => {
        const data = {
            properties: {},
        };

        renderWithProviders(
            <Router>
                <ClosureStatus data={data} clearFacility={clearFacility} />
            </Router>,
        );

        expect(screen.queryByText('Status pending')).not.toBeInTheDocument();
        expect(
            screen.queryByText(/This facility may be/),
        ).not.toBeInTheDocument();
    });

    test('returns null when report exists but not pending and not closed', () => {
        const data = {
            properties: {
                activity_reports: [{ status: 'RESOLVED' }],
                is_closed: false,
            },
        };

        renderWithProviders(
            <Router>
                <ClosureStatus data={data} clearFacility={clearFacility} />
            </Router>,
        );

        expect(screen.queryByText('Status pending')).not.toBeInTheDocument();
        expect(
            screen.queryByText(/This facility is closed/),
        ).not.toBeInTheDocument();
    });

    test('renders pending message when report status is PENDING', () => {
        const data = {
            properties: {
                activity_reports: [
                    { status: 'PENDING', closure_state: 'closed' },
                ],
                is_closed: false,
            },
        };

        renderWithProviders(
            <Router>
                <ClosureStatus data={data} clearFacility={clearFacility} />
            </Router>,
        );

        expect(
            screen.getByText(/This facility may be closed\./),
        ).toBeInTheDocument();
        expect(screen.getByText('Status pending')).toBeInTheDocument();
    });

    test('renders closed message when facility is closed and no new OS ID', () => {
        const data = {
            properties: {
                activity_reports: [{ status: 'RESOLVED' }],
                is_closed: true,
            },
        };

        renderWithProviders(
            <Router>
                <ClosureStatus data={data} clearFacility={clearFacility} />
            </Router>,
        );

        expect(
            screen.getByText(/This facility is closed\./),
        ).toBeInTheDocument();
    });

    test('renders moved-to link when closed with new_os_id', () => {
        const data = {
            properties: {
                activity_reports: [{ status: 'RESOLVED' }],
                is_closed: true,
                new_os_id: 'US2025123456ABCD',
            },
        };

        renderWithProviders(
            <Router>
                <ClosureStatus data={data} clearFacility={clearFacility} />
            </Router>,
        );

        const link = screen.getByRole('link', { name: 'US2025123456ABCD' });
        expect(link).toBeInTheDocument();
        expect(
            screen.getByText(/This facility has moved to/),
        ).toBeInTheDocument();
    });
});
