import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter as Router, useHistory } from 'react-router-dom';
import ProductionLocationDialog from '../../components/Contribute/ProductionLocationDialog';
import ProductionLocationDialogCloseButton from '../../components/Contribute/ProductionLocationDialogCloseButton';


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
            listen: jest.fn(() => jest.fn()),
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

    test.each([
        ['PENDING', 'unclaimed', false],
        ['PENDING', 'pending', true],
        ['PENDING', 'claimed', true],
        ['REJECTED', 'claimed', true],
        ['REJECTED', 'pending', true],
        ['REJECTED', 'unclaimed', false],
        ['REJECTED', undefined, true],
        ['APPROVED', 'unclaimed', false],
        ['APPROVED', 'pending', true],
        ['APPROVED', 'claimed', true]
    ])('handles moderation status %s and claim status %s correctly', (moderationStatus, claimStatus, shouldBeDisabled) => {
        const { getByRole } = render(
            <Router>
                <ProductionLocationDialog
                    classes={{}}
                    data={defaultProps.data}
                    osID={defaultProps.osID}
                    moderationStatus={moderationStatus}
                    claimStatus={claimStatus}
                />
            </Router>
        );

        const claimButton = getByRole('button', { name: /Continue to Claim/i });
        expect(window.getComputedStyle(claimButton).pointerEvents).toBe(shouldBeDisabled ? 'none' : '');
    });

    test('check link to the claim flow for specific production location', () => {
        const { getByRole } = render(
            <Router>
                <ProductionLocationDialog
                    classes={{}}
                    data={defaultProps.data}
                    osID={defaultProps.osID}
                    moderationStatus='APPROVED'
                    claimStatus='unclaimed'
                />
            </Router>
        );

        const claimButton = getByRole('button', { name: /Continue to Claim/i });
        expect(claimButton).toHaveAttribute('href', `/facilities/${defaultProps.osID}/claim`);
    });

    test('Search OS Hub button should link to the main page', () => {
        const { getByRole } = render(
            <Router>
                <ProductionLocationDialog
                    classes={{}}
                    data={defaultProps.data}
                    osID={defaultProps.osID}
                    moderationStatus='APPROVED'
                    claimStatus='unclaimed'
                />
            </Router>
        );

        const searchOSHubButton = getByRole('button', { name: /Search OS Hub/i });
        fireEvent.click(searchOSHubButton);

        expect(mockHistoryPush).toHaveBeenCalledWith('/');
    });

    test('Submit another Location button should link to the SLC search page', () => {
        const { getByRole } = render(
            <Router>
                <ProductionLocationDialog
                    classes={{}}
                    data={defaultProps.data}
                    osID={defaultProps.osID}
                    moderationStatus='APPROVED'
                    claimStatus='unclaimed'
                />
            </Router>
        );

        const submitAnotherLocationButton = getByRole('button', { name: /Submit another Location/i });
        fireEvent.click(submitAnotherLocationButton);

        expect(mockHistoryPush).toHaveBeenCalledWith('/contribute/single-location?tab=name-address');
    });

    test('redirect to the main page when clicking close button', () => {
        render(
            <Router>
                <ProductionLocationDialog
                    classes={{}}
                    data={defaultProps.data}
                    osID={defaultProps.osID}
                    moderationStatus={defaultProps.moderationStatus}
                    isOpen
                >
                    <ProductionLocationDialogCloseButton
                        isMobile={false}
                    />
                </ProductionLocationDialog>
            </Router>
        );

        expect(screen.getByText(/Continue to Claim/i)).toBeInTheDocument();

        const closeButton = screen.getByRole('button', { name: /close/i });

        fireEvent.click(closeButton);
        expect(mockHistoryPush).toHaveBeenCalledWith('/');
    });
});
