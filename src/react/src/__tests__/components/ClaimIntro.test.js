import React from 'react';
import { Router } from 'react-router-dom';
import { fireEvent, waitFor } from '@testing-library/react';
import history from '../../util/history';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import ClaimIntro from '../../components/InitialClaimFlow/ClaimIntro/ClaimIntro';
import { facilityDetailsRoute, claimDetailsRoute } from '../../util/constants';
import { isActiveClaimCampaign } from '../../util/claimCampaign';

beforeAll(() => {
    window.scrollTo = jest.fn();
    // The test environment is node; setupTests.js provides a JSDOM
    // window, whose localStorage the campaign code storage uses.
    global.localStorage = window.localStorage;
});

afterAll(() => {
    delete global.localStorage;
});

jest.mock('../../components/InitialClaimFlow/ClaimIntro/ClaimInfoSection', () => ({ children }) => (
    <div data-testid="claim-info-section">{children}</div>
));

// The banner waits for the backend to confirm the campaign is active.
jest.mock('../../util/claimCampaign', () => ({
    ...jest.requireActual('../../util/claimCampaign'),
    isActiveClaimCampaign: jest.fn(),
}));

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
                getByText(/Review the steps below to confirm your eligibility/)
            ).toBeInTheDocument();
        });

        test('says which claims are approved fastest', () => {
            const { getByText } = renderComponent();

            expect(
                getByText(
                    'Claims with a work email and an official document are approved fastest.'
                )
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

    describe('OS ID tracking and form reset', () => {
        test('resets form and updates osIdToClaim when OS ID changes from a different production location', () => {
            // Initial render with first OS ID and some form data.
            const firstOsID = 'LOCATION_001';
            const preloadedState = {
                auth: {
                    user: {
                        user: {
                            isAnon: false,
                        },
                    },
                },
                claimForm: {
                    osIdToClaim: firstOsID,
                    formData: {
                        facilityDescription: 'Some description',
                        yourName: 'John Doe',
                    },
                    completedSteps: [0, 1],
                },
            };

            const { reduxStore, rerender } = renderWithProviders(
                <Router history={history}>
                    <ClaimIntro match={{ params: { osID: firstOsID } }} />
                </Router>,
                { preloadedState }
            );

            // Verify initial state has data.
            let state = reduxStore.getState();
            expect(state.claimForm.osIdToClaim).toBe(firstOsID);
            expect(state.claimForm.formData.yourName).toBe('John Doe');
            expect(state.claimForm.completedSteps).toContain(0);
            
            // Change to a different OS ID - this should trigger resetForm
            // and then updateOsId.
            const secondOsID = 'LOCATION_002';
            rerender(
                <Router history={history}>
                    <ClaimIntro match={{ params: { osID: secondOsID } }} />
                </Router>
            );

            // Check that the form was reset and osIdToClaim updated to
            // new location.
            state = reduxStore.getState();
            expect(state.claimForm.osIdToClaim).toBe(secondOsID);
            // Form data should be reset to initial values.
            expect(state.claimForm.formData.yourName).toBe('');
            expect(state.claimForm.completedSteps).toEqual([]);
        });

        const campaignState = (flagOn = true, isAnon = false) => ({
            auth: { user: { user: { isAnon } } },
            featureFlags: {
                fetching: false,
                flags: { claim_campaigns: flagOn },
            },
        });

        const renderCampaignIntro = state =>
            renderWithProviders(
                <Router history={history}>
                    <ClaimIntro match={mockMatch} />
                </Router>,
                { preloadedState: state }
            );

        const storedCampaign = () =>
            JSON.parse(localStorage.getItem(`claim-campaign-${mockOsID}`));

        beforeEach(() => {
            localStorage.clear();
            isActiveClaimCampaign.mockReset();
        });

        test('stores an active campaign code and shows the banner', async () => {
            isActiveClaimCampaign.mockResolvedValue(true);
            history.push(`/claim/${mockOsID}?campaign=example-fresh-26`);

            const { reduxStore, findByText, getByText } = renderCampaignIntro(
                campaignState()
            );

            expect(await findByText(/part of a claims campaign/)).toBeInTheDocument();
            expect(getByText('EXAMPLE-FRESH-26')).toBeInTheDocument();
            expect(isActiveClaimCampaign).toHaveBeenCalledWith('EXAMPLE-FRESH-26');
            expect(reduxStore.getState().claimForm.formData.campaign).toBe(
                'EXAMPLE-FRESH-26'
            );
            expect(storedCampaign().code).toBe('EXAMPLE-FRESH-26');
        });

        test('hides the banner and forgets a code that is not an active campaign', async () => {
            isActiveClaimCampaign.mockResolvedValue(false);
            history.push(`/claim/${mockOsID}?campaign=CLOSED-26`);

            const { reduxStore, queryByText } = renderCampaignIntro(
                campaignState()
            );

            await waitFor(() => {
                expect(isActiveClaimCampaign).toHaveBeenCalled();
                expect(storedCampaign()).toBeNull();
            });
            expect(queryByText(/part of a claims campaign/)).not.toBeInTheDocument();
            expect(reduxStore.getState().claimForm.formData.campaign).toBe('');
        });

        test('keeps the code but shows no banner when the lookup fails', async () => {
            isActiveClaimCampaign.mockResolvedValue(null);
            history.push(`/claim/${mockOsID}?campaign=EXAMPLE-FRESH-26`);

            const { queryByText } = renderCampaignIntro(campaignState());

            await waitFor(() => {
                expect(isActiveClaimCampaign).toHaveBeenCalled();
            });
            expect(queryByText(/part of a claims campaign/)).not.toBeInTheDocument();
            expect(storedCampaign().code).toBe('EXAMPLE-FRESH-26');
        });

        test('drops a malformed code without asking the backend', () => {
            localStorage.setItem(
                `claim-campaign-${mockOsID}`,
                JSON.stringify({ code: 'OLD-26', savedAt: Date.now() })
            );
            history.push(`/claim/${mockOsID}?campaign=${'x'.repeat(60)}`);

            const { reduxStore } = renderCampaignIntro(campaignState());

            expect(isActiveClaimCampaign).not.toHaveBeenCalled();
            expect(storedCampaign()).toBeNull();
            expect(reduxStore.getState().claimForm.formData.campaign).toBe('');
        });

        test('uses the remembered code when the page opens without the parameter', async () => {
            // e.g. after logging in, or Back from the claim form.
            isActiveClaimCampaign.mockResolvedValue(true);
            localStorage.setItem(
                `claim-campaign-${mockOsID}`,
                JSON.stringify({ code: 'EXAMPLE-FRESH-26', savedAt: Date.now() })
            );
            history.push(`/claim/${mockOsID}`);

            const { findByText } = renderCampaignIntro(campaignState());

            expect(await findByText(/part of a claims campaign/)).toBeInTheDocument();
        });

        test('never shows a code from an earlier visit for an invalid link', async () => {
            // The form still holds a code confirmed on an earlier visit.
            isActiveClaimCampaign.mockResolvedValue(false);
            history.push(`/claim/${mockOsID}?campaign=NOT-A-CAMPAIGN`);
            const state = {
                ...campaignState(),
                claimForm: {
                    osIdToClaim: mockOsID,
                    formData: { campaign: 'EXAMPLE-FRESH-26' },
                },
            };

            const { reduxStore, queryByText } = renderCampaignIntro(state);

            // Not while the new code is being checked...
            expect(queryByText(/part of a claims campaign/)).not.toBeInTheDocument();
            expect(queryByText('EXAMPLE-FRESH-26')).not.toBeInTheDocument();

            // ...nor after it turns out not to be a campaign.
            await waitFor(() => {
                expect(reduxStore.getState().claimForm.formData.campaign).toBe('');
            });
            expect(queryByText(/part of a claims campaign/)).not.toBeInTheDocument();
        });

        test('shows no banner while the code is still being checked', () => {
            isActiveClaimCampaign.mockReturnValue(new Promise(() => {}));
            history.push(`/claim/${mockOsID}?campaign=EXAMPLE-FRESH-26`);

            const { queryByText } = renderCampaignIntro(campaignState());

            expect(queryByText(/part of a claims campaign/)).not.toBeInTheDocument();
        });

        test('clears a stale form code when nothing is remembered', () => {
            history.push(`/claim/${mockOsID}`);
            const state = {
                ...campaignState(),
                claimForm: {
                    osIdToClaim: mockOsID,
                    formData: { campaign: 'STALE-26' },
                },
            };

            const { reduxStore, queryByText } = renderCampaignIntro(state);

            expect(isActiveClaimCampaign).not.toHaveBeenCalled();
            expect(reduxStore.getState().claimForm.formData.campaign).toBe('');
            expect(queryByText(/part of a claims campaign/)).not.toBeInTheDocument();
        });

        test('remembers the code before sign-in without looking it up', () => {
            history.push(`/claim/${mockOsID}?campaign=EXAMPLE-FRESH-26`);

            renderCampaignIntro(campaignState(true, true));

            expect(isActiveClaimCampaign).not.toHaveBeenCalled();
            expect(storedCampaign().code).toBe('EXAMPLE-FRESH-26');
        });

        test('ignores the campaign code when the flag is off', () => {
            history.push(`/claim/${mockOsID}?campaign=EXAMPLE-FRESH-26`);

            const { reduxStore, queryByText } = renderCampaignIntro(
                campaignState(false)
            );

            expect(isActiveClaimCampaign).not.toHaveBeenCalled();
            expect(reduxStore.getState().claimForm.formData.campaign).toBe('');
            expect(
                queryByText(/part of a claims campaign/)
            ).not.toBeInTheDocument();
        });

        test('shows no banner without a campaign parameter', () => {
            const { queryByText } = renderComponent();

            expect(
                queryByText(/part of a claims campaign/)
            ).not.toBeInTheDocument();
        });

        test('updates osIdToClaim when it is not set initially', () => {
            const testOsID = 'LOCATION_003';
            const preloadedState = {
                auth: {
                    user: {
                        user: {
                            isAnon: false,
                        },
                    },
                },
                claimForm: {
                    osIdToClaim: '', // Empty OS ID to claim.
                },
            };

            const { reduxStore } = renderWithProviders(
                <Router history={history}>
                    <ClaimIntro match={{ params: { osID: testOsID } }} />
                </Router>,
                { preloadedState }
            );

            // Check that osIdToClaim was updated in state.
            const state = reduxStore.getState();
            expect(state.claimForm.osIdToClaim).toBe(testOsID);
        });
    });
});
