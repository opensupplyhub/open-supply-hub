import React from 'react';
import { fireEvent, screen } from '@testing-library/react';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import EligibilityStep from '../../components/InitialClaimFlow/ClaimForm/Steps/EligibilityStep/EligibilityStep';
import { mainRoute } from '../../util/constants';

const mockHistoryPush = jest.fn();

jest.mock('react-router-dom', () => {
    const actual = jest.requireActual('react-router-dom');
    return {
        ...actual,
        useHistory: () => ({
            push: mockHistoryPush,
        }),
        useLocation: () => ({
            pathname: '/claim/test-os-id',
            search: '',
            hash: '',
            state: null,
        }),
    };
});

jest.mock('../../components/Filters/StyledSelect', () => {
    // eslint-disable-next-line global-require
    const mockPropTypes = require('prop-types');
    const MockStyledSelect = ({
        options,
        value,
        onChange,
        onBlur,
        placeholder,
        name,
    }) => (
        <select
            data-testid="relationship-select"
            name={name}
            value={value ? value.value : ''}
            onChange={e => {
                const selectedOption = options.find(
                    opt => opt.value === e.target.value,
                );
                onChange(selectedOption);
            }}
            onBlur={onBlur}
        >
            <option value="">{placeholder}</option>
            {options.map(opt => (
                <option key={opt.value} value={opt.value}>
                    {opt.label}
                </option>
            ))}
        </select>
    );

    MockStyledSelect.propTypes = {
        options: mockPropTypes.arrayOf(
            mockPropTypes.shape({
                value: mockPropTypes.string.isRequired,
                label: mockPropTypes.string.isRequired,
            }),
        ).isRequired,
        value: mockPropTypes.oneOfType([
            mockPropTypes.shape({
                value: mockPropTypes.string,
                label: mockPropTypes.string,
            }),
            mockPropTypes.oneOf([null]),
        ]),
        onChange: mockPropTypes.func.isRequired,
        onBlur: mockPropTypes.func,
        placeholder: mockPropTypes.string,
        name: mockPropTypes.string,
    };

    MockStyledSelect.defaultProps = {
        value: null,
        onBlur: () => {},
        placeholder: '',
        name: 'claimantLocationRelationship',
    };

    return MockStyledSelect;
});

// jsdom does not implement scrollTo; stub to avoid errors in hooks.
beforeAll(() => {
    // eslint-disable-next-line no-underscore-dangle
    if (!window._scrollToStubbed) {
        window.scrollTo = jest.fn();
        // eslint-disable-next-line no-underscore-dangle
        window._scrollToStubbed = true;
    }
});

describe('EligibilityStep component', () => {
    const mockHandleChange = jest.fn();
    const mockOnNext = jest.fn();
    const mockOnBack = jest.fn();

    const defaultProps = {
        formData: { claimantLocationRelationship: null },
        handleChange: mockHandleChange,
        onNext: mockOnNext,
        onBack: mockOnBack,
        errors: {},
        touched: {},
        handleBlur: () => {},
    };

    const preloadedState = {
        auth: {
            user: {
                user: {
                    email: 'test@example.com',
                    name: 'Test Organization',
                    isAnon: false,
                },
            },
        },
    };

    const renderComponent = (props = {}, state = preloadedState) =>
        renderWithProviders(<EligibilityStep {...defaultProps} {...props} />, {
            preloadedState: state,
        });

    afterEach(() => {
        jest.clearAllMocks();
    });

    test('renders without crashing', () => {
        const { container } = renderComponent();
        expect(container).toBeInTheDocument();
    });

    test('renders component with user information', () => {
        renderComponent();

        expect(screen.getByText('Email address:')).toBeInTheDocument();
        expect(screen.getByText('test@example.com')).toBeInTheDocument();
        expect(screen.getByText('Organization:')).toBeInTheDocument();
        expect(screen.getByText('Test Organization')).toBeInTheDocument();
    });

    test('renders select field with placeholder', () => {
        renderComponent();

        const elements = screen.getAllByText(
            'Select your relationship to this production location', { exact: false }
        );
        expect(elements.length).toBeGreaterThan(0);

        const selectField = screen.getByTestId('relationship-select');
        expect(selectField).toBeInTheDocument();
    });

    test('displays "Not available" when user email is not provided', () => {
        const stateWithoutEmail = {
            auth: {
                user: {
                    user: {
                        email: null,
                        name: null,
                        isAnon: true,
                    },
                },
            },
        };

        renderComponent({}, stateWithoutEmail);

        const notAvailableElements = screen.getAllByText('Not available');
        expect(notAvailableElements).toHaveLength(2);
    });

    test('ineligibility dialog is not shown by default', () => {
        renderComponent();

        expect(
            screen.queryByText('Not Eligible to File Claim')
        ).not.toBeInTheDocument();
    });

    test('shows ineligibility dialog when "partner" option is selected', () => {
        renderComponent();

        const selectField = screen.getByTestId('relationship-select');
        fireEvent.change(selectField, { target: { value: 'partner' } });

        expect(screen.getByText('Not Eligible to File Claim')).toBeInTheDocument();
        expect(
            screen.getByText(/You are not eligible to file a claim for this location/i)
        ).toBeInTheDocument();
    });

    test('shows ineligibility dialog when "other" option is selected', () => {
        renderComponent();

        const selectField = screen.getByTestId('relationship-select');
        fireEvent.change(selectField, { target: { value: 'other' } });

        expect(screen.getByText('Not Eligible to File Claim')).toBeInTheDocument();
        expect(
            screen.getByText(/You are not eligible to file a claim for this location/i)
        ).toBeInTheDocument();
    });

    test('ineligibility dialog contains correct message and buttons', () => {
        renderComponent();

        const selectField = screen.getByTestId('relationship-select');
        fireEvent.change(selectField, { target: { value: 'partner' } });

        expect(
            screen.getByText(/Only the owner, manager, authorized employee/i)
        ).toBeInTheDocument();
        expect(
            screen.getByRole('button', { name: /Go Back to Open Supply Hub/i })
        ).toBeInTheDocument();
        expect(
            screen.getByRole('button', { name: /Continue to Claim/i })
        ).toBeInTheDocument();
    });

    test('navigates to main page when "Go Back to Open Supply Hub" is clicked', () => {
        renderComponent();

        const selectField = screen.getByTestId('relationship-select');
        fireEvent.change(selectField, { target: { value: 'partner' } });

        const backButton = screen.getByRole('button', {
            name: /Go Back to Open Supply Hub/i,
        });
        backButton.click();

        expect(mockHistoryPush).toHaveBeenCalledTimes(1);
        expect(mockHistoryPush).toHaveBeenCalledWith(mainRoute);
    });

    test('closes dialog without resetting selection when "Continue to Claim" is clicked', () => {
        renderComponent();

        const selectField = screen.getByTestId('relationship-select');
        fireEvent.change(selectField, { target: { value: 'other' } });

        expect(screen.getByText('Not Eligible to File Claim')).toBeInTheDocument();

        const returnButton = screen.getByRole('button', {
            name: /Continue to Claim/i,
        });
        fireEvent.click(returnButton);

        // The dialog should close and NOT reset previously selected valid relationship
        expect(mockHandleChange).not.toHaveBeenCalledWith(
            'claimantLocationRelationship',
            null,
        );
        // And no change should be emitted at all for ineligible selections.
        expect(mockHandleChange).not.toHaveBeenCalled();
    });

    test('calls handleChange when eligible "owner" option is selected', () => {
        renderComponent();

        const selectField = screen.getByTestId('relationship-select');
        fireEvent.change(selectField, { target: { value: 'owner' } });

        expect(mockHandleChange).toHaveBeenCalledTimes(1);
        expect(mockHandleChange).toHaveBeenCalledWith(
            'claimantLocationRelationship',
            'I am the owner of this production location',
        );
        expect(
            screen.queryByText('Not Eligible to File Claim')
        ).not.toBeInTheDocument();
    });

    test('calls handleChange when eligible "manager" option is selected', () => {
        renderComponent();

        const selectField = screen.getByTestId('relationship-select');
        fireEvent.change(selectField, { target: { value: 'manager' } });

        expect(mockHandleChange).toHaveBeenCalledTimes(1);
        expect(mockHandleChange).toHaveBeenCalledWith(
            'claimantLocationRelationship',
            'I am a manager working at this production location',
        );
        expect(
            screen.queryByText('Not Eligible to File Claim')
        ).not.toBeInTheDocument();
    });

    test('calls handleChange when eligible "worker" option is selected', () => {
        renderComponent();

        const selectField = screen.getByTestId('relationship-select');
        fireEvent.change(selectField, { target: { value: 'worker' } });

        expect(mockHandleChange).toHaveBeenCalledTimes(1);
        expect(
            screen.queryByText('Not Eligible to File Claim')
        ).not.toBeInTheDocument();
    });

    test('calls handleChange when "parent_company_owner_or_manager" option is selected', () => {
        renderComponent();

        const selectField = screen.getByTestId('relationship-select');
        fireEvent.change(selectField, {
            target: { value: 'parent_company_owner_or_manager' },
        });

        expect(mockHandleChange).toHaveBeenCalledTimes(1);
        expect(
            screen.queryByText('Not Eligible to File Claim')
        ).not.toBeInTheDocument();
    });
});
