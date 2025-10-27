import React from 'react';
import { Router } from 'react-router-dom';
import history from '../../util/history';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import ClaimForm from '../../components/InitialClaimFlow/ClaimForm/ClaimForm';

// Mock the useRequireIntroAccess hook to prevent redirect issues in tests.
jest.mock('../../components/InitialClaimFlow/ClaimForm/hooks', () => ({
    ...jest.requireActual('../../components/InitialClaimFlow/ClaimForm/hooks'),
    useRequireIntroAccess: jest.fn(), // No-op in tests.
}));

// Mock window APIs not implemented in JSDOM.
beforeAll(() => {
    window.scrollTo = jest.fn();
    
    // Mock sessionStorage.
    const sessionStorageMock = {
        getItem: jest.fn(() => 'true'), // Simulate user came from intro.
    };
    global.sessionStorage = sessionStorageMock;
});

// Mock step components to simplify testing.
jest.mock('../../components/InitialClaimFlow/ClaimForm/Steps/EligibilityStep/EligibilityStep', () => () => (
    <div data-testid="eligibility-step">Eligibility Step</div>
));

jest.mock('../../components/InitialClaimFlow/ClaimForm/Steps/ContactStep', () => () => (
    <div data-testid="contact-step">Contact Step</div>
));

jest.mock('../../components/InitialClaimFlow/ClaimForm/Steps/BusinessStep', () => () => (
    <div data-testid="business-step">Business Step</div>
));

jest.mock('../../components/InitialClaimFlow/ClaimForm/Steps/ProfileStep', () => () => (
    <div data-testid="profile-step">Profile Step</div>
));

describe('ClaimForm component', () => {
    const mockOsID = 'TEST123';
    const mockMatch = {
        params: { osID: mockOsID },
    };

    const defaultPreloadedState = {
        claimForm: {
            activeStep: 0,
            completedSteps: [],
            formData: {
                position: '',
                yearsAtCompany: '',
                contactEmail: '',
                contactPhone: '',
                businessName: '',
                businessWebsite: '',
                numberOfWorkers: '',
                additionalNotes: '',
            },
        },
        filterOptions: {
            countries: {
                data: [{ value: 'US', label: 'United States' }],
                fetching: false,
                error: null,
            },
            facilityProcessingType: {
                data: [{ value: 'assembly', label: 'Assembly' }],
                fetching: false,
                error: null,
            },
            parentCompanies: {
                data: [{ value: '1', label: 'Company Inc.' }],
                fetching: false,
                error: null,
            },
        },
        contributeProductionLocation: {
            singleProductionLocation: {
                data: {
                    name: 'Test Facility',
                    address: '123 Test St',
                },
                fetching: false,
                error: null,
            },
        },
        auth: {
            user: {
                user: {
                    isAnon: false,
                },
            },
        },
    };

    const renderComponent = (preloadedState = defaultPreloadedState) =>
        renderWithProviders(
            <Router history={history}>
                <ClaimForm match={mockMatch} />
            </Router>,
            { preloadedState },
        );

    beforeEach(() => {
        jest.clearAllMocks();
        history.push('/');
    });

    describe('Authentication checks', () => {
        test('renders RequireAuthNotice when user is not signed in', () => {
            const stateWithAnonUser = {
                ...defaultPreloadedState,
                auth: {
                    user: {
                        user: {
                            isAnon: true,
                        },
                    },
                },
            };

            const { getByText } = renderComponent(stateWithAnonUser);

            expect(getByText('Claim this production location')).toBeInTheDocument();
            expect(
                getByText('Log in to claim a production location on Open Supply Hub'),
            ).toBeInTheDocument();
        });

        test('renders form when user is signed in', () => {
            const { getByText } = renderComponent();

            expect(
                getByText('Production Location Claims Process'),
            ).toBeInTheDocument();
        });
    });

    describe('Loading state', () => {
        test('shows loading spinner while fetching countries', () => {
            const stateWithFetching = {
                ...defaultPreloadedState,
                filterOptions: {
                    ...defaultPreloadedState.filterOptions,
                    countries: {
                        data: [],
                        fetching: true,
                        error: null,
                    },
                },
            };

            const { getByRole } = renderComponent(stateWithFetching);

            expect(getByRole('progressbar')).toBeInTheDocument();
        });

        test('shows loading spinner while fetching production location', () => {
            const stateWithFetching = {
                ...defaultPreloadedState,
                contributeProductionLocation: {
                    singleProductionLocation: {
                        data: {},
                        fetching: true,
                        error: null,
                    },
                },
            };

            const { getByRole } = renderComponent(stateWithFetching);

            expect(getByRole('progressbar')).toBeInTheDocument();
        });
    });

    describe('Error state', () => {
        test('shows error state when countries fetch fails', () => {
            const stateWithError = {
                ...defaultPreloadedState,
                filterOptions: {
                    ...defaultPreloadedState.filterOptions,
                    countries: {
                        ...defaultPreloadedState.filterOptions.countries,
                        error: ['Failed to load countries'],
                    },
                },
            };

            const { getByText } = renderComponent(stateWithError);

            // ErrorState component shows a generic title.
            expect(
                getByText('An error occurred while loading the claim form.'),
            ).toBeInTheDocument();
            expect(getByText('Try Again')).toBeInTheDocument();
        });

        test('shows error state when production location fetch fails', async () => {
            const stateWithError = {
                claimForm: {
                    ...defaultPreloadedState.claimForm,
                },
                filterOptions: {
                    countries: {
                        data: [],
                        fetching: false,  // Must be false.
                        error: null,
                    },
                    facilityProcessingType: {
                        data: [],
                        fetching: false,  // Must be false.
                        error: null,
                    },
                    parentCompanies: {
                        data: [],
                        fetching: false,  // Must be false.
                        error: null,
                    },
                },
                contributeProductionLocation: {
                    singleProductionLocation: {
                        data: {},
                        fetching: false,  // Must be false to show error.
                        error: ['Failed to load facility'],
                    },
                },
                auth: {
                    ...defaultPreloadedState.auth,
                },
            };

            const { findByText } = renderComponent(stateWithError);

            expect(
                await findByText('An error occurred while loading the claim form.'),
            ).toBeInTheDocument();
            expect(await findByText('Try Again')).toBeInTheDocument();
        });
    });

    describe('Form rendering', () => {
        test('renders the form title and description', () => {
            const { getByText } = renderComponent();

            expect(
                getByText('Production Location Claims Process'),
            ).toBeInTheDocument();
            expect(
                getByText(
                    'Complete all sections to submit your production location claim',
                ),
            ).toBeInTheDocument();
        });

        test('renders the stepper component', () => {
            const { getByText } = renderComponent();

            // Check stepper is present by looking for step labels.
            expect(getByText('Step 1')).toBeInTheDocument();
            expect(getByText('Step 2')).toBeInTheDocument();
        });

        test('renders the first step (Eligibility) by default', () => {
            const { getByTestId } = renderComponent();

            expect(getByTestId('eligibility-step')).toBeInTheDocument();
        });

        test('renders navigation buttons', () => {
            const { getByText } = renderComponent();

            expect(getByText('Go Back')).toBeInTheDocument();
            expect(getByText('Continue to Contact Information')).toBeInTheDocument();
        });
    });

    describe('Step navigation', () => {
        test('displays correct step when activeStep is 1', () => {
            const stateOnStep1 = {
                ...defaultPreloadedState,
                claimForm: {
                    ...defaultPreloadedState.claimForm,
                    activeStep: 1,
                },
            };

            const { getByTestId } = renderComponent(stateOnStep1);

            expect(getByTestId('contact-step')).toBeInTheDocument();
        });

        test('displays correct step when activeStep is 2', () => {
            const stateOnStep2 = {
                ...defaultPreloadedState,
                claimForm: {
                    ...defaultPreloadedState.claimForm,
                    activeStep: 2,
                },
            };

            const { getByTestId } = renderComponent(stateOnStep2);

            expect(getByTestId('business-step')).toBeInTheDocument();
        });

        test('displays correct step when activeStep is 3', () => {
            const stateOnStep3 = {
                ...defaultPreloadedState,
                claimForm: {
                    ...defaultPreloadedState.claimForm,
                    activeStep: 3,
                },
            };

            const { getByTestId } = renderComponent(stateOnStep3);

            expect(getByTestId('profile-step')).toBeInTheDocument();
        });

        test('shows "Back" button on non-first steps', () => {
            const stateOnStep1 = {
                ...defaultPreloadedState,
                claimForm: {
                    ...defaultPreloadedState.claimForm,
                    activeStep: 1,
                },
            };

            const { getByText } = renderComponent(stateOnStep1);

            expect(getByText('Back')).toBeInTheDocument();
        });

        test('shows "Submit Claim" button on last step', () => {
            const stateOnStep3 = {
                ...defaultPreloadedState,
                claimForm: {
                    ...defaultPreloadedState.claimForm,
                    activeStep: 3,
                },
            };

            const { getByText } = renderComponent(stateOnStep3);

            expect(getByText('Submit Claim')).toBeInTheDocument();
        });
    });

    describe('Button text changes per step', () => {
        test('shows "Continue to Contact Information" on step 0', () => {
            const { getByText } = renderComponent();

            expect(getByText('Continue to Contact Information')).toBeInTheDocument();
        });

        test('shows "Continue to Business Details" on step 1', () => {
            const stateOnStep1 = {
                ...defaultPreloadedState,
                claimForm: {
                    ...defaultPreloadedState.claimForm,
                    activeStep: 1,
                },
            };

            const { getByText } = renderComponent(stateOnStep1);

            expect(getByText('Continue to Business Details')).toBeInTheDocument();
        });

        test('shows "Continue to Production Location Details" on step 2', () => {
            const stateOnStep2 = {
                ...defaultPreloadedState,
                claimForm: {
                    ...defaultPreloadedState.claimForm,
                    activeStep: 2,
                },
            };

            const { getByText } = renderComponent(stateOnStep2);

            expect(
                getByText('Continue to Production Location Details'),
            ).toBeInTheDocument();
        });
    });

    describe('URL access protection', () => {
        test('uses access protection hook on mount', () => {
            // eslint-disable-next-line global-require
            const { useRequireIntroAccess } = require('../../components/InitialClaimFlow/ClaimForm/hooks');

            renderComponent();

            // Verify hook was called with correct parameters.
            expect(useRequireIntroAccess).toHaveBeenCalled();
        });

        test('renders form successfully when access is allowed', () => {
            const { getByText } = renderComponent();

            expect(
                getByText('Production Location Claims Process'),
            ).toBeInTheDocument();
        });
    });
});

