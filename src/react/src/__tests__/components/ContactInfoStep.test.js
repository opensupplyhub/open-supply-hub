import React from 'react';
import { fireEvent, screen } from '@testing-library/react';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import ContactInfoStep from '../../components/InitialClaimFlow/ClaimForm/Steps/ContactInfoStep/ContactInfoStep';
import { EMPLOYMENT_VERIFICATION_OPTIONS } from '../../components/InitialClaimFlow/ClaimForm/Steps/ContactInfoStep/constants';

jest.mock('../../components/Filters/StyledSelect', () => {
    // eslint-disable-next-line global-require
    const mockPropTypes = require('prop-types');
    const MockStyledSelect = ({ options, value, onChange, onBlur, placeholder, name }) => (
        <select
            data-testid="employment-verification-select"
            name={name}
            value={value ? value.value : ''}
            onChange={e => {
                const selectedOption = options.find(opt => opt.value === e.target.value);
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
            mockPropTypes.shape({ value: mockPropTypes.string.isRequired, label: mockPropTypes.string.isRequired })
        ).isRequired,
        value: mockPropTypes.oneOfType([
            mockPropTypes.shape({ value: mockPropTypes.string, label: mockPropTypes.string }),
            mockPropTypes.oneOf([null]),
        ]),
        onChange: mockPropTypes.func.isRequired,
        onBlur: mockPropTypes.func,
        placeholder: mockPropTypes.string,
        name: mockPropTypes.string,
    };

    MockStyledSelect.defaultProps = { value: null, onBlur: () => {}, placeholder: '', name: 'claimantEmploymentVerificationMethod' };

    return MockStyledSelect;
});

// Some HOCs/hooks call window.scrollTo; stub it.
beforeAll(() => {
    // eslint-disable-next-line no-underscore-dangle
    if (!window._scrollToStubbed) {
        window.scrollTo = jest.fn();
        // eslint-disable-next-line no-underscore-dangle
        window._scrollToStubbed = true;
    }
});

// Mock routing hooks used by withScrollReset HOC.
const mockHistoryPush = jest.fn();
jest.mock('react-router-dom', () => {
    const actual = jest.requireActual('react-router-dom');
    return {
        ...actual,
        useHistory: () => ({ push: mockHistoryPush }),
        useLocation: () => ({ pathname: '/claim/test-os-id', search: '', hash: '', state: null }),
    };
});

describe('ContactInfoStep component', () => {
    const mockHandleChange = jest.fn();
    const mockHandleBlur = jest.fn();
    const mockUpdateFieldWithoutTouch = jest.fn();

    const defaultProps = {
        formData: {
            pointOfContactPubliclyVisible: false,
            yourName: 'Alice Smith',
            yourTitle: 'Manager',
            claimantEmploymentVerificationMethod: '',
            claimantLinkedinProfileUrl: '',
            employmentVerificationDocuments: [],
            pointOfcontactPersonName: '',
            pointOfContactEmail: '',
        },
        handleChange: mockHandleChange,
        handleBlur: mockHandleBlur,
        updateFieldWithoutTouch: mockUpdateFieldWithoutTouch,
        errors: {},
        touched: {},
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
        renderWithProviders(
            <ContactInfoStep {...defaultProps} {...props} />,
            { preloadedState: state },
        );

    afterEach(() => {
        jest.clearAllMocks();
    });

    test('renders and shows user email', () => {
        renderComponent();

        // The read-only email TextField should have the user email value.
        const emailInputs = screen.getAllByDisplayValue('test@example.com');
        expect(emailInputs.length).toBeGreaterThan(0);
    });

    test('enabling public contact prefills contactName and contactEmail', () => {
        renderComponent();

        const publicSwitch = screen.getByRole('checkbox');
        fireEvent.click(publicSwitch);

        // First call toggles the flag, then prefill name and email
        expect(mockHandleChange).toHaveBeenCalledWith(
            'pointOfContactPubliclyVisible',
            true,
        );
        expect(mockHandleChange).toHaveBeenCalledWith(
            'pointOfcontactPersonName',
            'Alice Smith',
        );
        expect(mockHandleChange).toHaveBeenCalledWith(
            'pointOfContactEmail',
            'test@example.com',
        );
    });

    test('does not prefill contactName when claimantName is empty', () => {
        const props = {
            formData: { ...defaultProps.formData, yourName: '' },
        };
        renderComponent(props);

        const publicSwitch = screen.getByRole('checkbox');
        fireEvent.click(publicSwitch);

        expect(mockHandleChange).toHaveBeenCalledWith(
            'pointOfContactPubliclyVisible',
            true,
        );
        // No call with contactName when claimantName is empty.
        expect(mockHandleChange).not.toHaveBeenCalledWith(
            'pointOfcontactPersonName',
            expect.anything(),
        );
        expect(mockHandleChange).toHaveBeenCalledWith(
            'pointOfContactEmail',
            'test@example.com',
        );
    });

    test('selecting URL-based verification shows URL input with placeholder and updates value', () => {
        // Simulate parent updating formData after selection.
        const linkedinLabel = EMPLOYMENT_VERIFICATION_OPTIONS.find(opt => opt.value === 'linkedin-page').label;
        const { rerender } = renderComponent();

        const select = screen.getByTestId('employment-verification-select');
        fireEvent.change(select, { target: { value: 'linkedin-page' } });

        rerender(
            <ContactInfoStep
                {...defaultProps}
                formData={{
                    ...defaultProps.formData,
                    claimantEmploymentVerificationMethod: linkedinLabel,
                }}
                handleChange={mockHandleChange}
                handleBlur={mockHandleBlur}
                updateFieldWithoutTouch={mockUpdateFieldWithoutTouch}
            />
        );

        const urlInput = screen.getByPlaceholderText('https://linkedin.com/in/yourprofile');
        expect(urlInput).toBeInTheDocument();

        fireEvent.change(urlInput, { target: { value: 'https://linkedin.com/in/alice' } });
        expect(mockHandleChange).toHaveBeenCalledWith(
            'claimantLinkedinProfileUrl',
            'https://linkedin.com/in/alice',
        );
    });

    test('selecting document-based verification shows attachments uploader', () => {
        // Simulate parent updating formData after selection.
        const letterLabel = EMPLOYMENT_VERIFICATION_OPTIONS.find(opt => opt.value === 'employment-letter').label;
        const { rerender } = renderComponent();

        const select = screen.getByTestId('employment-verification-select');
        fireEvent.change(select, { target: { value: 'employment-letter' } });

        rerender(
            <ContactInfoStep
                {...defaultProps}
                formData={{
                    ...defaultProps.formData,
                    claimantEmploymentVerificationMethod: letterLabel,
                }}
                handleChange={mockHandleChange}
                handleBlur={mockHandleBlur}
                updateFieldWithoutTouch={mockUpdateFieldWithoutTouch}
            />
        );

        expect(screen.getByTestId('claim-attachments-uploader')).toBeInTheDocument();
    });

    test('displays validation errors for employment verification and URL', () => {
        const linkedinLabel = EMPLOYMENT_VERIFICATION_OPTIONS.find(opt => opt.value === 'linkedin-page').label;
        const props = {
            touched: {
                claimantEmploymentVerificationMethod: true,
                claimantLinkedinProfileUrl: true,
            },
            errors: {
                claimantEmploymentVerificationMethod: 'Please select one option',
                claimantLinkedinProfileUrl: 'Enter a valid URL',
            },
            formData: {
                ...defaultProps.formData,
                claimantEmploymentVerificationMethod: linkedinLabel,
            },
        };

        renderComponent(props);

        // URL field present; errors should render.
        expect(screen.getByText('Please select one option')).toBeInTheDocument();
        expect(screen.getByText('Enter a valid URL')).toBeInTheDocument();
    });
});


