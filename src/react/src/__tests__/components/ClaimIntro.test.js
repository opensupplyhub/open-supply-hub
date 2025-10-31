import React from 'react';
import { Router } from 'react-router-dom';
import { fireEvent } from '@testing-library/react';
import history from '../../util/history';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import ClaimIntro from '../../components/InitialClaimFlow/ClaimIntro/ClaimIntro';
import { facilityDetailsRoute, claimDetailsRoute } from '../../util/constants';

beforeAll(() => {
    window.scrollTo = jest.fn();
});

jest.mock('../../components/InitialClaimFlow/ClaimIntro/ClaimInfoSection', () => ({ children }) => (
    <div data-testid="claim-info-section">{children}</div>
));

describe('ClaimIntro component', () => {
    const mockOsID = 'TEST123';
    const mockMatch = {
        params: { osID: mockOsID },
    };

    const renderComponent = (userHasSignedIn = true) => {
        const preloadedState = {
            auth: {
                user: {
                    user: {
                        isAnon: !userHasSignedIn,
                    },
                },
            },
        };

        return renderWithProviders(
            <Router history={history}>
                <ClaimIntro match={mockMatch} />
            </Router>,
            { preloadedState }
        );
    };

    beforeEach(() => {
        jest.clearAllMocks();
        history.push('/');
    });

    describe('Authentication checks', () => {
        test('renders RequireAuthNotice when user is not signed in', () => {
            const { getByText } = renderComponent(false);

            expect(getByText('Claim this production location')).toBeInTheDocument();
            expect(
                getByText('Log in to claim a production location on Open Supply Hub')
            ).toBeInTheDocument();
        });

        test('renders main content when user is signed in', () => {
            const { getByText, getByTestId } = renderComponent(true);

            expect(getByText('Claim a Production Location')).toBeInTheDocument();
            expect(getByTestId('claim-info-section')).toBeInTheDocument();
        });
    });

    describe('Component rendering', () => {
        test('renders without crashing', () => {
            renderComponent();
        });

        test('displays the correct title', () => {
            const { getByText } = renderComponent();

            expect(getByText('Claim a Production Location')).toBeInTheDocument();
        });

        test('displays the subtitle text', () => {
            const { getByText } = renderComponent();

            expect(
                getByText(/In order to submit a claim request/)
            ).toBeInTheDocument();
        });

        test('renders both action buttons', () => {
            const { getByText } = renderComponent();

            expect(getByText('Go Back')).toBeInTheDocument();
            expect(getByText('Continue')).toBeInTheDocument();
        });

        test('renders ClaimInfoSection component', () => {
            const { getByTestId } = renderComponent();

            expect(getByTestId('claim-info-section')).toBeInTheDocument();
        });
    });

    describe('Navigation functionality', () => {
        test('navigates back when Go Back button is clicked', () => {
            const { getByText } = renderComponent();
            const backButton = getByText('Go Back');

            fireEvent.click(backButton);

            expect(history.location.pathname).toBe(facilityDetailsRoute.replace(':osID', mockOsID));
        });

        test('navigates to claim details when Continue button is clicked', () => {
            const { getByText } = renderComponent();
            const sessionStorageMock = {
                setItem: jest.fn(),
            };
            global.sessionStorage = sessionStorageMock;

            const continueButton = getByText('Continue');
            fireEvent.click(continueButton);

            const expectedPath = claimDetailsRoute.replace(':osID', mockOsID);
            expect(history.location.pathname).toBe(expectedPath);
        });
    });

    describe('Props validation', () => {
        test('receives osID from route params', () => {
            const { container } = renderComponent();

            expect(container.firstChild).toBeInTheDocument();
        });
    });
});
