import React from 'react';
import { fireEvent } from '@testing-library/react';
import { BrowserRouter as Router, useHistory } from 'react-router-dom';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import ProductionLocationDialog from '../../components/Contribute/ProductionLocationDialog';
import ProductionLocationDialogCloseButton from '../../components/Contribute/ProductionLocationDialogCloseButton';
import {
    MODERATION_STATUSES_ENUM,
    PRODUCTION_LOCATION_CLAIM_STATUSES_ENUM,
} from '../../util/constants';


jest.mock('react-router-dom', () => ({
    ...jest.requireActual('react-router-dom'),
    useHistory: jest.fn(),
}));

jest.mock("../../components/Contribute/DialogTooltip", () => {
    // eslint-disable-next-line no-shadow, global-require
    const React = require('react');
    return function MockDialogTooltip({ text, childComponent }) {
        const [open, setOpen] = React.useState(false);

        const handleMouseOver = () => {
            setOpen(true);
        };

        const handleMouseOut = () => {
            setOpen(false);
        };

        return (
            <div
                onMouseOver={handleMouseOver}
                onFocus={handleMouseOver}
                onMouseOut={handleMouseOut}
                onBlur={handleMouseOut}
            >
                {childComponent}
                {open && <div>{text}</div>}
            </div>
        );
    };
});

const mockHistoryPush = jest.fn();

describe('ProductionLocationDialog', () => {
    const defaultProps = {
        osID: 'US2021250D1DTN7',
        moderationStatus: 'PENDING',
        data: {
            raw_json: {
                name: 'Production Location Name',
                address: '1234 Production Location St, City, State, 12345',
                product_type: [
                    "Shirts",
                    "Pants"
                ],
                facility_type: [
                    "Printing, Product Dyeing and Laundering"
                ],
                processing_type: [
                    "Assembly",
                    "Printing"
                ],
                number_of_workers: {
                    min: 35,
                    max: 60
                },
                parent_company: "ParentCompany1, ParentCompany2",
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
        const { getAllByText, getByText } = renderWithProviders(
            <Router>
                <ProductionLocationDialog 
                    classes={{}}
                    data={defaultProps.data}
                    osID={defaultProps.osID}
                    moderationStatus={defaultProps.moderationStatus}
                />
            </Router>
        );

        expect(getByText(/Thanks for adding data for this production location!/i)).toBeInTheDocument();

        expect(getAllByText(/Location name/i)).toHaveLength(2);
        expect(getByText(/Production Location Name/i)).toBeInTheDocument();

        expect(getByText(/Address/i)).toBeInTheDocument();
        expect(getByText(/1234 Production Location St, City, State, 12345/i)).toBeInTheDocument();

        expect(getByText(/OS ID/i)).toBeInTheDocument();
        expect(getByText(/US2021250D1DTN7/i)).toBeInTheDocument();

        expect(getByText(/Pending/i)).toBeInTheDocument();
        expect(getByText(/Location Type/i)).toBeInTheDocument();

        expect(getByText(/Number of workers/i)).toBeInTheDocument();
        expect(getByText(/35 - 60/i)).toBeInTheDocument();

        expect(getByText(/Processing Type/i)).toBeInTheDocument();
        expect(getByText(/Assembly, Printing/i)).toBeInTheDocument();

        expect(getByText(/Parent Company/i)).toBeInTheDocument();
        expect(getByText(/ParentCompany1, ParentCompany2/i)).toBeInTheDocument();

        expect(getByText(/Country/i)).toBeInTheDocument();
        expect(getByText(/BD/i)).toBeInTheDocument();

        expect(getByText(/Product Type/i)).toBeInTheDocument();
        expect(getByText(/Shirts, Pants/i)).toBeInTheDocument();
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
        const { getByRole } = renderWithProviders(
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

    test('check link to the old claim flow when feature flag is disabled', () => {
        const { getByRole } = renderWithProviders(
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

    test('check link to the new claim flow when feature flag is enabled', () => {
        const initialState = {
            featureFlags: {
                flags: {
                    enable_v1_claims_flow: true,
                },
                fetching: false,
            },
        };

        const { getByRole } = renderWithProviders(
            <Router>
                <ProductionLocationDialog
                    classes={{}}
                    data={defaultProps.data}
                    osID={defaultProps.osID}
                    moderationStatus='APPROVED'
                    claimStatus='unclaimed'
                />
            </Router>,
            { preloadedState: initialState }
        );

        const claimButton = getByRole('button', { name: /Continue to Claim/i });
        expect(claimButton).toHaveAttribute('href', `/claim/${defaultProps.osID}`);
    });

    test('Search OS Hub button should link to the main page', () => {
        const { getByRole } = renderWithProviders(
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
        const { getByRole } = renderWithProviders(
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
        const { getByText, getByRole } = renderWithProviders(
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

        expect(getByText(/Continue to Claim/i)).toBeInTheDocument();

        const closeButton = getByRole('button', { name: /close/i });

        fireEvent.click(closeButton);
        expect(mockHistoryPush).toHaveBeenCalledWith('/');
    });
});

describe('ProductionLocationDialog tooltip messages for PENDING, CLAIMED and UNCLAIMED production locations', () => {
    const defaultProps = {
        osID: 'US2021250D1DTN7',
        data: {
            raw_json: {
                name: 'Production Location Name',
                address: '1234 Production Location St, City, State, 12345',
                country: "BD"
            }
        }
    };

    beforeEach(() => {
        useHistory.mockReturnValue({
            push: mockHistoryPush,
            listen: jest.fn(() => jest.fn()),
        });
    });

    test.each([
        [PRODUCTION_LOCATION_CLAIM_STATUSES_ENUM.CLAIMED,
            'Your submission is being reviewed. You will receive an email confirming your OS ID once the review is complete.',
            'This location has already been claimed and therefore cannot be claimed again.'],
        [PRODUCTION_LOCATION_CLAIM_STATUSES_ENUM.PENDING,
            'Your submission is being reviewed. You will receive an email confirming your OS ID once the review is complete.',
            'This location cannot be claimed because a pending claim already exists.']
    ])(
        'renders claim button and pending badge tooltips when moderation event is pending and production location has status: %s',
        async (claimStatus, expectedPendingTooltip, expectedClaimTooltip) => {
            const { getAllByTestId, getByRole, findByText } = renderWithProviders(
                <Router>
                    <ProductionLocationDialog 
                        classes={{}}
                        data={defaultProps.data}
                        osID={defaultProps.osID}
                        moderationStatus={MODERATION_STATUSES_ENUM.PENDING}
                        claimStatus={claimStatus}
                    />
                </Router>
            );

            const tooltipIcons = getAllByTestId('tooltip-icon');

            // Pending icon tooltip message
            fireEvent.mouseOver(tooltipIcons[0]);

            const pendingTooltipText = await findByText(expectedPendingTooltip);
            expect(pendingTooltipText).toBeInTheDocument();

            fireEvent.mouseOut(tooltipIcons[0]);
            expect(pendingTooltipText).not.toBeInTheDocument();

            // Claim button tooltip message
            const claimButton = getByRole('button', { name: /Continue to Claim/i });
            expect(claimButton).toHaveAttribute('tabindex', '-1');

            fireEvent.mouseOver(claimButton);
            const claimTooltipText = await findByText(expectedClaimTooltip);
            expect(claimTooltipText).toBeInTheDocument();

            fireEvent.mouseOut(claimButton);
            expect(claimTooltipText).not.toBeInTheDocument();
        }
    );

    test('renders claim button and pending badge tooltips when moderation event is pending and production location is available for claim', async () => {
        const { getAllByTestId, getByRole, findByText } = renderWithProviders(
            <Router>
                <ProductionLocationDialog 
                    classes={{}}
                    data={defaultProps.data}
                    osID={defaultProps.osID}
                    moderationStatus={MODERATION_STATUSES_ENUM.PENDING}
                    claimStatus={PRODUCTION_LOCATION_CLAIM_STATUSES_ENUM.UNCLAIMED}
                />
            </Router>
        );

        // Pending icon tooltip message
        const tooltipIcons = getAllByTestId('tooltip-icon');

        fireEvent.mouseOver(tooltipIcons[0]);

        const pendingTooltipText = await findByText(
            'Your submission is under review. You will receive a notification once the production location is live on OS Hub. You can proceed to submit a claim while your request is pending.'
        );
        expect(pendingTooltipText).toBeInTheDocument();

        fireEvent.mouseOut(tooltipIcons[0]);
        expect(pendingTooltipText).not.toBeInTheDocument();

        // Claim button
        const claimButton = getByRole('button', { name: /Continue to Claim/i });
        expect(claimButton).toHaveAttribute('href', `/facilities/${defaultProps.osID}/claim`);
        expect(claimButton).not.toBeDisabled();
    });

    test('renders claim button and pending badge tooltips when moderation event is pending and production location has\'t been created yet', async () => {
        const { getAllByTestId, getByRole, findByText } = renderWithProviders(
            <Router>
                <ProductionLocationDialog 
                    classes={{}}
                    data={defaultProps.data}
                    moderationStatus={MODERATION_STATUSES_ENUM.PENDING}
                />
            </Router>
        );

        // Pending icon tooltip message
        const tooltipIcons = getAllByTestId('tooltip-icon');

        fireEvent.mouseOver(tooltipIcons[0]);

        const pendingTooltipText = await findByText(
            'Your submission is being reviewed. You will receive an email with your OS ID once the review is complete.'
        );
        expect(pendingTooltipText).toBeInTheDocument();

        fireEvent.mouseOut(tooltipIcons[0]);
        expect(pendingTooltipText).not.toBeInTheDocument();

        // Claim button tooltip message
        const claimButton = getByRole('button', { name: /Continue to Claim/i });
        expect(claimButton).toHaveAttribute('tabindex', '-1');

        fireEvent.mouseOver(claimButton);
        const claimTooltipText = await findByText(
            'You will be able to claim this location once the review is complete.'
        );
        expect(claimTooltipText).toBeInTheDocument();

        fireEvent.mouseOut(claimButton);
        expect(claimTooltipText).not.toBeInTheDocument();
    });
});
