import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter as Router, useHistory } from 'react-router-dom';
import ProductionLocationDialog from '../../components/Contribute/ProductionLocationDialog';

jest.mock('react-router-dom', () => ({
    ...jest.requireActual('react-router-dom'),
    useHistory: jest.fn(),
}));

const mockHistoryPush = jest.fn();

describe('ProductionLocationDialog', () => {
    const defaultProps = {
        osID: 'US2021250D1DTN7',
        moderationStatus: 'PENDING',
        data: {
            raw_json: {
                name: 'Production Location Name',
                address: '1234 Production Location St, City, State, 12345',
            },
            fields: {
                product_type: [
                    "Shirts",
                    "Pants"
                ],
                facility_type: {
                    raw_values: [
                        "Printing, Product Dyeing and Laundering"
                    ],
                    processed_values: [
                        "Product Dyeing and Laundering",
                        "Printing"
                    ]
                },
                processing_type: {
                    raw_values: [
                        "Assembly",
                        "Printing"
                    ],
                    processed_values: [
                        "Assembly",
                        "Printing"
                    ]
                },
                number_of_workers: {
                    min: 35,
                    max: 60
                },
                parent_company: [
                    "ParentCompany1",
                    "ParentCompany2"
                ],
                country: "BD"
            }
        }
    }

    beforeEach(() => {
        useHistory.mockReturnValue({
            push: mockHistoryPush,
        });
    });

    test('renders dialog content', () => {
        render(
            <Router>
                <ProductionLocationDialog 
                    classes={{}} 
                    data={defaultProps.data}
                    osID={defaultProps.osID}
                    moderationStatus={defaultProps.moderationStatus}
                />
            </Router>
        );

        expect(screen.getByText(/Thanks for adding data for this production location!/i)).toBeInTheDocument();

        expect(screen.getByText(/Facility name/i)).toBeInTheDocument();
        expect(screen.getByText(/Production Location Name/i)).toBeInTheDocument();

        expect(screen.getByText(/Address/i)).toBeInTheDocument();
        expect(screen.getByText(/1234 Production Location St, City, State, 12345/i)).toBeInTheDocument();

        expect(screen.getByText(/OS ID/i)).toBeInTheDocument();
        expect(screen.getByText(/US2021250D1DTN7/i)).toBeInTheDocument();

        expect(screen.getByText(/Pending/i)).toBeInTheDocument();

        expect(screen.getByText(/Number of workers/i)).toBeInTheDocument();
        expect(screen.getByText(/35 - 60/i)).toBeInTheDocument();

        expect(screen.getByText(/Processing Type/i)).toBeInTheDocument();
        expect(screen.getByText(/Assembly, Printing/i)).toBeInTheDocument();

        expect(screen.getByText(/Parent Company/i)).toBeInTheDocument();
        expect(screen.getByText(/ParentCompany1, ParentCompany2/i)).toBeInTheDocument();

        expect(screen.getByText(/Country/i)).toBeInTheDocument();
        expect(screen.getByText(/BD/i)).toBeInTheDocument();

        expect(screen.getByText(/Product Type/i)).toBeInTheDocument();
        expect(screen.getByText(/Shirts, Pants/i)).toBeInTheDocument();
    });

    test('Continue to Claim button should be active if production location is unclaimed', () => {
        const { getByRole } = render(
            <Router>
                <ProductionLocationDialog 
                    classes={{}}
                    data={defaultProps.data}
                    osID={defaultProps.osID}
                    moderationStatus={defaultProps.moderationStatus}
                    claimStatus='unclaimed'
                />
            </Router>
        );

        const claimButton = getByRole('button', { name: /Continue to Claim/i });

        expect(window.getComputedStyle(claimButton).pointerEvents).not.toBe('none');

        expect(claimButton).toHaveAttribute('href', `/facilities/${defaultProps.osID}/claim`);
    });

    test('Continue to Claim button should be disabled if production location has been claimed', () => {
        const { getByRole } = render(
            <Router>
                <ProductionLocationDialog 
                    classes={{}} 
                    data={defaultProps.data}
                    osID={defaultProps.osID}
                    moderationStatus={defaultProps.moderationStatus}
                    claimStatus='claimed'
                />
            </Router>
        );

        const claimButton = getByRole('button', { name: /Continue to Claim/i });

        expect(window.getComputedStyle(claimButton).pointerEvents).toBe('none');
    });
});
