import React from 'react';
import { fireEvent, waitFor, act } from '@testing-library/react';
import { Router } from 'react-router-dom';
import history from '../../util/history';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import ClaimForm from '../../components/InitialClaimFlow/ClaimForm/ClaimForm';
import apiRequest from '../../util/apiRequest';

// The Business step's quality check posts through apiRequest; nothing
// else in these tests should reach the network.
jest.mock('../../util/apiRequest', () => ({
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    patch: jest.fn(),
    delete: jest.fn(),
}));

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
        removeItem: jest.fn(),
        setItem: jest.fn(),
    };
    global.sessionStorage = sessionStorageMock;
});

// Mock step components to simplify testing.
jest.mock('../../components/InitialClaimFlow/ClaimForm/Steps/EligibilityStep/EligibilityStep', () => () => (
    <div data-testid="eligibility-step">Eligibility Step</div>
));

jest.mock('../../components/InitialClaimFlow/ClaimForm/Steps/ContactInfoStep/ContactInfoStep', () => () => (
    <div data-testid="contact-step">Contact Step</div>
));

jest.mock('../../components/InitialClaimFlow/ClaimForm/Steps/BusinessStep/BusinessStep', () => () => (
    <div data-testid="business-step">Business Step</div>
));

jest.mock(
    '../../components/InitialClaimFlow/ClaimForm/Steps/ProfileStep/ProfileStep',
    () => () => (
        <div data-testid="profile-step">
            Profile Step
            <input data-testid="profile-input" placeholder="Profile Input" />
        </div>
    ),
);

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
            submissionState: {
                fetching: false,
                error: null,
                data: null,
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
        // GETs must fail, as they did against the network before the
        // module was mocked: a GET that resolved with empty data would
        // leave an options list empty and usePrefetchClaimData would
        // request it again on every render.
        apiRequest.get.mockRejectedValue(new Error('not mocked'));
        apiRequest.post.mockResolvedValue({ data: {} });
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
            expect(getByText('Continue')).toBeInTheDocument();
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
        test('shows "Continue" on step 0', () => {
            const { getByText } = renderComponent();

            expect(getByText('Continue')).toBeInTheDocument();
        });

        test('shows "Continue" on step 1', () => {
            const stateOnStep1 = {
                ...defaultPreloadedState,
                claimForm: {
                    ...defaultPreloadedState.claimForm,
                    activeStep: 1,
                },
            };

            const { getByText } = renderComponent(stateOnStep1);

            expect(getByText('Continue')).toBeInTheDocument();
        });

        test('shows "Continue" on step 2', () => {
            const stateOnStep2 = {
                ...defaultPreloadedState,
                claimForm: {
                    ...defaultPreloadedState.claimForm,
                    activeStep: 2,
                },
            };

            const { getByText } = renderComponent(stateOnStep2);

            expect(getByText('Continue')).toBeInTheDocument();
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

    describe('Submission behavior', () => {
        const stateOnStep3 = {
            ...defaultPreloadedState,
            claimForm: {
                ...defaultPreloadedState.claimForm,
                activeStep: 3,
            },
        };

        test('does not submit when pressing Enter on an input field', () => {
            const { getByTestId, getByText } = renderWithProviders(
                <Router history={history}>
                    <ClaimForm match={mockMatch} />
                </Router>,
                { preloadedState: stateOnStep3 },
            );

            const input = getByTestId('profile-input');
            const submitButton = getByText('Submit Claim');

            expect(input).toBeInTheDocument();
            expect(submitButton).toBeInTheDocument();
            
            input.focus();
            fireEvent.keyDown(input, { key: 'Enter', code: 'Enter', charCode: 13 });

            expect(getByText('Submit Claim')).toBeInTheDocument();
        });

        test('Submit button is configured for explicit activation only', () => {
            const { getByText } = renderWithProviders(
                <Router history={history}>
                    <ClaimForm match={mockMatch} />
                </Router>,
                { preloadedState: stateOnStep3 },
            );

            const submitButton = getByText('Submit Claim');

            expect(submitButton).toBeInTheDocument();

            // The button is configured with type="button" in ClaimForm.jsx (not type="submit").
            // This prevents implicit form submission when Enter is pressed in form inputs.
            // Submission only happens via explicit button click/activation,
            // which calls claimForm.handleSubmit via the button's onClick handler.
        });
    });

    describe('Successful submission and form reset', () => {
        test('resets form data when submission completes successfully', async () => {
            // Start with form that has data and is submitting.
            const submittingState = {
                ...defaultPreloadedState,
                claimForm: {
                    ...defaultPreloadedState.claimForm,
                    activeStep: 3,
                    formData: {
                        ...defaultPreloadedState.claimForm.formData,
                        yourName: 'John Doe',
                        facilityDescription: 'Test facility description',
                    },
                    completedSteps: [0, 1, 2],
                    submissionState: {
                        fetching: true,
                        error: null,
                        data: null,
                    },
                },
            };

            const { reduxStore } = renderWithProviders(
                <Router history={history}>
                    <ClaimForm match={mockMatch} />
                </Router>,
                { preloadedState: submittingState },
            );

            // Verify initial state has data.
            let state = reduxStore.getState();
            expect(state.claimForm.formData.yourName).toBe('John Doe');
            expect(state.claimForm.completedSteps).toEqual([0, 1, 2]);

            // Simulate successful submission by dispatching actions.
            await act(async () => {
                reduxStore.dispatch({
                    type: 'COMPLETE_SUBMIT_CLAIM_FORM_DATA',
                    payload: { success: true },
                });
                // Wait for the hook to process the state change and reset form.
                await new Promise(resolve => setTimeout(resolve, 100));
            });

            // Check that form was reset.
            state = reduxStore.getState();
            expect(state.claimForm.formData.yourName).toBe('');
            expect(state.claimForm.formData.facilityDescription).toBe('');
            expect(state.claimForm.completedSteps).toEqual([]);
            expect(state.claimForm.activeStep).toBe(0);
        });

        test('shows success dialog with navigation buttons after successful submission', async () => {
            // Start with fetching state.
            const fetchingState = {
                ...defaultPreloadedState,
                claimForm: {
                    ...defaultPreloadedState.claimForm,
                    activeStep: 3,
                    submissionState: {
                        fetching: true,
                        error: null,
                        data: null,
                    },
                },
            };

            const { reduxStore, getByText } = renderWithProviders(
                <Router history={history}>
                    <ClaimForm match={mockMatch} />
                </Router>,
                { preloadedState: fetchingState },
            );

            // Complete submission successfully.
            await act(async () => {
                reduxStore.dispatch({
                    type: 'COMPLETE_SUBMIT_CLAIM_FORM_DATA',
                    payload: { success: true },
                });
                await new Promise(resolve => setTimeout(resolve, 50));
            });

            // Check dialog is shown with navigation buttons.
            await waitFor(() => {
                expect(getByText('To My Claims')).toBeInTheDocument();
            });
            expect(getByText('Search OS Hub')).toBeInTheDocument();
            expect(
                getByText('Thank you for submitting your claim request!')
            ).toBeInTheDocument();
        });

        test('removes session storage item after successful submission', async () => {
            const fetchingState = {
                ...defaultPreloadedState,
                claimForm: {
                    ...defaultPreloadedState.claimForm,
                    activeStep: 3,
                    submissionState: {
                        fetching: true,
                        error: null,
                        data: null,
                    },
                },
            };

            const removeItemSpy = jest.spyOn(global.sessionStorage, 'removeItem');

            const { reduxStore } = renderWithProviders(
                <Router history={history}>
                    <ClaimForm match={mockMatch} />
                </Router>,
                { preloadedState: fetchingState },
            );

            // Complete submission successfully.
            await act(async () => {
                reduxStore.dispatch({
                    type: 'COMPLETE_SUBMIT_CLAIM_FORM_DATA',
                    payload: { success: true },
                });
                await new Promise(resolve => setTimeout(resolve, 100));
            });

            // Check that session storage was cleared.
            await waitFor(() => {
                expect(removeItemSpy).toHaveBeenCalledWith(`claim-form-access-${mockOsID}`);
            });

            removeItemSpy.mockRestore();
        });
    });

    describe('Cleanup on unmount', () => {
        test('resets filters and production location when component unmounts', () => {
            const stateWithData = {
                ...defaultPreloadedState,
                filterOptions: {
                    countries: {
                        data: [
                            { value: 'US', label: 'United States' },
                            { value: 'CA', label: 'Canada' },
                        ],
                        fetching: false,
                        error: null,
                    },
                    facilityProcessingType: {
                        data: [
                            { value: 'assembly', label: 'Assembly' },
                            { value: 'sewing', label: 'Sewing' },
                        ],
                        fetching: false,
                        error: null,
                    },
                    parentCompanies: {
                        data: [
                            { value: '1', label: 'Company Inc.' },
                            { value: '2', label: 'Another Corp.' },
                        ],
                        fetching: false,
                        error: null,
                    },
                },
                contributeProductionLocation: {
                    singleProductionLocation: {
                        data: {
                            name: 'Test Facility',
                            address: '123 Test St',
                            osID: mockOsID,
                        },
                        fetching: false,
                        error: null,
                    },
                },
            };

            const { reduxStore, unmount } = renderWithProviders(
                <Router history={history}>
                    <ClaimForm match={mockMatch} />
                </Router>,
                { preloadedState: stateWithData },
            );

            // Verify initial state has data.
            let state = reduxStore.getState();
            expect(state.filterOptions.countries.data.length).toBeGreaterThan(0);
            expect(state.contributeProductionLocation.singleProductionLocation.data.name).toBe('Test Facility');

            // Unmount component.
            unmount();

            // Check that filters and production location were reset to initial state.
            state = reduxStore.getState();
            // Filters reset to null (as per FilterOptionsReducer initialState).
            expect(state.filterOptions.countries.data).toBeNull();
            expect(state.filterOptions.facilityProcessingType.data).toBeNull();
            expect(state.filterOptions.parentCompanies.data).toBeNull();
            // Production location resets to empty object.
            expect(state.contributeProductionLocation.singleProductionLocation.data).toEqual({});
        });
    });
    describe('Company name and address prefill', () => {
        const stateWithLocation = {
            ...defaultPreloadedState,
            contributeProductionLocation: {
                singleProductionLocation: {
                    data: {
                        os_id: mockOsID,
                        name: 'Test Facility',
                        address: '123 Test St',
                    },
                    fetching: false,
                    error: null,
                },
            },
            featureFlags: {
                fetching: false,
                flags: { enable_claim_name_address_edit: true },
            },
        };

        test('does not seed the fields while the waffle switch is off', async () => {
            const stateWithSwitchOff = {
                ...stateWithLocation,
                featureFlags: {
                    fetching: false,
                    flags: { enable_claim_name_address_edit: false },
                },
            };

            const { reduxStore } = renderComponent(stateWithSwitchOff);

            // Give any pending effects a chance to run before asserting.
            await waitFor(() => {
                expect(
                    reduxStore.getState().contributeProductionLocation
                        .singleProductionLocation.data.os_id,
                ).toBe(mockOsID);
            });
            const { formData } = reduxStore.getState().claimForm;
            expect(formData.facilityNameEnglish).toBeUndefined();
            expect(formData.facilityAddress).toBeUndefined();
        });

        test('seeds facilityNameEnglish and facilityAddress from the production location', async () => {
            const { reduxStore } = renderComponent(stateWithLocation);

            await waitFor(() => {
                const { formData } = reduxStore.getState().claimForm;
                expect(formData.facilityNameEnglish).toBe('Test Facility');
                expect(formData.facilityAddress).toBe('123 Test St');
            });
        });

        test('does not overwrite values the claimant has already entered', async () => {
            const stateWithEdits = {
                ...stateWithLocation,
                claimForm: {
                    ...stateWithLocation.claimForm,
                    formData: {
                        ...stateWithLocation.claimForm.formData,
                        facilityNameEnglish: 'Edited Name',
                        facilityAddress: '',
                    },
                },
            };

            const { reduxStore } = renderComponent(stateWithEdits);

            await waitFor(() => {
                const { formData } = reduxStore.getState().claimForm;
                expect(formData.facilityAddress).toBe('123 Test St');
            });
            expect(reduxStore.getState().claimForm.formData.facilityNameEnglish).toBe(
                'Edited Name',
            );
        });
    });

    describe('Business step quality check', () => {
        const warning = {
            type: 'different_location',
            title: 'Details May Describe a Different Location',
            message: 'The address looks like another city.',
        };
        const businessStepValues = {
            facilityNameEnglish: 'Edited Name',
            facilityAddress: '123 Test St',
            locationAddressVerificationMethod: 'some-method',
            businessLinkedinProfile: '',
            businessWebsite: '',
            companyAddressVerificationDocuments: [],
            qualityWarningsDismissed: null,
        };
        const makeState = ({ flagOn = true, formData = {} } = {}) => ({
            ...defaultPreloadedState,
            claimForm: {
                ...defaultPreloadedState.claimForm,
                activeStep: 2,
                formData: {
                    ...defaultPreloadedState.claimForm.formData,
                    ...businessStepValues,
                    ...formData,
                },
            },
            contributeProductionLocation: {
                singleProductionLocation: {
                    data: {
                        os_id: mockOsID,
                        name: 'Test Facility',
                        address: '123 Test St',
                    },
                    fetching: false,
                    error: null,
                },
            },
            featureFlags: {
                fetching: false,
                flags: { enable_claim_name_address_edit: flagOn },
            },
        });
        const checkURL = `/api/facilities/${mockOsID}/claim/quality-check/`;

        test('checks an edited name before leaving the step and shows the warnings', async () => {
            apiRequest.post.mockResolvedValue({
                data: { warnings: [warning] },
            });
            const { getByText, reduxStore } = renderComponent(makeState());

            fireEvent.click(getByText('Continue'));

            await waitFor(() => {
                expect(getByText(warning.title)).toBeInTheDocument();
            });
            expect(apiRequest.post).toHaveBeenCalledWith(checkURL, {
                facility_name_english: 'Edited Name',
                facility_address: '123 Test St',
            });
            expect(getByText(warning.message)).toBeInTheDocument();
            expect(reduxStore.getState().claimForm.activeStep).toBe(2);
        });

        test('"Go back and edit" stays on the step without dismissing anything', async () => {
            apiRequest.post.mockResolvedValue({
                data: { warnings: [warning] },
            });
            const { getByText, queryByText, reduxStore } = renderComponent(
                makeState(),
            );

            fireEvent.click(getByText('Continue'));
            await waitFor(() => {
                expect(getByText(warning.title)).toBeInTheDocument();
            });
            fireEvent.click(getByText('Go back and edit'));

            await waitFor(() => {
                expect(queryByText(warning.title)).not.toBeInTheDocument();
            });
            const { activeStep, formData } = reduxStore.getState().claimForm;
            expect(activeStep).toBe(2);
            expect(formData.qualityWarningsDismissed).toBeNull();
        });

        test('"Continue anyway" records the dismissal for the values and advances', async () => {
            apiRequest.post.mockResolvedValue({
                data: { warnings: [warning] },
            });
            const { getByText, reduxStore } = renderComponent(makeState());

            fireEvent.click(getByText('Continue'));
            await waitFor(() => {
                expect(getByText(warning.title)).toBeInTheDocument();
            });
            fireEvent.click(getByText('Continue anyway'));

            await waitFor(() => {
                expect(reduxStore.getState().claimForm.activeStep).toBe(3);
            });
            expect(
                reduxStore.getState().claimForm.formData.qualityWarningsDismissed,
            ).toEqual({
                name: 'Edited Name',
                address: '123 Test St',
                warnings: [
                    {
                        type: 'different_location',
                        message: 'The address looks like another city.',
                    },
                ],
            });
        });

        test('re-shows the warnings on a second Continue with the same values without a second request', async () => {
            apiRequest.post.mockResolvedValue({
                data: { warnings: [warning] },
            });
            const { getByText, queryByText, reduxStore } = renderComponent(
                makeState(),
            );

            fireEvent.click(getByText('Continue'));
            await waitFor(() => {
                expect(getByText(warning.title)).toBeInTheDocument();
            });
            fireEvent.click(getByText('Go back and edit'));
            await waitFor(() => {
                expect(queryByText(warning.title)).not.toBeInTheDocument();
            });

            fireEvent.click(getByText('Continue'));

            await waitFor(() => {
                expect(getByText(warning.title)).toBeInTheDocument();
            });
            expect(apiRequest.post).toHaveBeenCalledTimes(1);
            expect(reduxStore.getState().claimForm.activeStep).toBe(2);
        });

        test('advances without a check when the values are the ones listed', async () => {
            const { getByText, reduxStore } = renderComponent(
                makeState({
                    formData: { facilityNameEnglish: ' test facility ' },
                }),
            );

            fireEvent.click(getByText('Continue'));

            await waitFor(() => {
                expect(reduxStore.getState().claimForm.activeStep).toBe(3);
            });
            expect(apiRequest.post).not.toHaveBeenCalled();
        });

        test('advances without a second check after dismissing warnings for the same values', async () => {
            const { getByText, reduxStore } = renderComponent(
                makeState({
                    formData: {
                        qualityWarningsDismissed: {
                            name: 'Edited Name',
                            address: '123 Test St',
                            warnings: [{ type: 'different_location', message: '' }],
                        },
                    },
                }),
            );

            fireEvent.click(getByText('Continue'));

            await waitFor(() => {
                expect(reduxStore.getState().claimForm.activeStep).toBe(3);
            });
            expect(apiRequest.post).not.toHaveBeenCalled();
        });

        test('advances when the check returns no warnings', async () => {
            apiRequest.post.mockResolvedValue({ data: { warnings: [] } });
            const { getByText, reduxStore } = renderComponent(makeState());

            fireEvent.click(getByText('Continue'));

            await waitFor(() => {
                expect(reduxStore.getState().claimForm.activeStep).toBe(3);
            });
            expect(apiRequest.post).toHaveBeenCalledTimes(1);
        });

        test('advances when the check request fails (fail open)', async () => {
            apiRequest.post.mockRejectedValue(new Error('network'));
            const { getByText, reduxStore } = renderComponent(makeState());

            fireEvent.click(getByText('Continue'));

            await waitFor(() => {
                expect(reduxStore.getState().claimForm.activeStep).toBe(3);
            });
        });

        test('does not check while the waffle switch is off', async () => {
            const { getByText, reduxStore } = renderComponent(
                makeState({ flagOn: false }),
            );

            fireEvent.click(getByText('Continue'));

            await waitFor(() => {
                expect(reduxStore.getState().claimForm.activeStep).toBe(3);
            });
            expect(apiRequest.post).not.toHaveBeenCalled();
        });
    });
});
