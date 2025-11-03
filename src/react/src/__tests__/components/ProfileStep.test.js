import React from 'react';
import { screen } from '@testing-library/react';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import ProfileStep from '../../components/InitialClaimFlow/ClaimForm/Steps/ProfileStep/ProfileStep';

jest.mock('react-router-dom', () => {
    const actual = jest.requireActual('react-router-dom');
    return {
        ...actual,
        useLocation: () => ({
            pathname: '/claim/test-os-id/details',
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
        options = [],
        value,
        onChange = () => {},
        onBlur = () => {},
        placeholder = '',
        name = 'select',
        isMulti = false,
        creatable = false,
        // eslint-disable-next-line no-unused-vars
        styles,
        // eslint-disable-next-line no-unused-vars
        ...rest
    }) => {
        if (!onChange) return null;
        
        return (
            <select
                data-testid={`styled-select-${name}`}
                name={name}
                value={isMulti ? (value || []).map(v => v?.value || v) : (value?.value || value || '')}
                onChange={e => {
                    if (isMulti) {
                        const selectedValues = Array.from(e.target.selectedOptions).map(
                            option => options.find(opt => opt.value === option.value),
                        ).filter(Boolean);
                        onChange(selectedValues);
                    } else {
                        const selectedOption = options.find(
                            opt => opt.value === e.target.value,
                        );
                        onChange(selectedOption);
                    }
                }}
                onBlur={onBlur}
                multiple={isMulti}
            >
                {!isMulti && <option value="">{placeholder}</option>}
                {options && options.map(opt => (
                    <option key={opt.value} value={opt.value}>
                        {opt.label}
                    </option>
                ))}
            </select>
        );
    };

    MockStyledSelect.propTypes = {
        options: mockPropTypes.arrayOf(
            mockPropTypes.shape({
                value: mockPropTypes.string.isRequired,
                label: mockPropTypes.string.isRequired,
            }),
        ),
        value: mockPropTypes.oneOfType([
            mockPropTypes.shape({
                value: mockPropTypes.string,
                label: mockPropTypes.string,
            }),
            mockPropTypes.arrayOf(mockPropTypes.shape({
                value: mockPropTypes.string,
                label: mockPropTypes.string,
            })),
            mockPropTypes.oneOf([null]),
        ]),
        onChange: mockPropTypes.func,
        onBlur: mockPropTypes.func,
        placeholder: mockPropTypes.string,
        name: mockPropTypes.string,
        isMulti: mockPropTypes.bool,
        creatable: mockPropTypes.bool,
        styles: mockPropTypes.object,
    };

    MockStyledSelect.defaultProps = {
        options: [],
        value: null,
        onChange: () => {},
        onBlur: () => {},
        placeholder: '',
        name: 'select',
        isMulti: false,
        creatable: false,
        styles: {},
    };

    return MockStyledSelect;
});

jest.mock('../../components/InputSection', () => {
    // eslint-disable-next-line global-require
    const mockPropTypes = require('prop-types');
    const MockInputSection = ({
        options = [],
        value = '',
        onChange = () => {},
        onBlur = () => {},
        label = '',
        name = 'input',
        // eslint-disable-next-line no-unused-vars
        menuPlacement,
        // eslint-disable-next-line no-unused-vars
        ...rest
    }) => {
        if (!options || options.length === 0) {
            return <div data-testid={`input-section-${name}`}>No options</div>;
        }

        return (
            <div>
                {label && <label htmlFor={name}>{label}</label>}
                <select
                    data-testid={`input-section-${name}`}
                    name={name}
                    id={name}
                    value={value || ''}
                    onChange={e => onChange(e.target.value)}
                    onBlur={onBlur}
                >
                    <option value="">Select...</option>
                    {options.map(opt => (
                        <option key={opt.value} value={opt.value}>
                            {opt.label}
                        </option>
                    ))}
                </select>
            </div>
        );
    };

    MockInputSection.propTypes = {
        options: mockPropTypes.arrayOf(
            mockPropTypes.shape({
                value: mockPropTypes.string.isRequired,
                label: mockPropTypes.string.isRequired,
            }),
        ),
        value: mockPropTypes.string,
        onChange: mockPropTypes.func,
        onBlur: mockPropTypes.func,
        label: mockPropTypes.string,
        name: mockPropTypes.string,
        menuPlacement: mockPropTypes.string,
    };

    MockInputSection.defaultProps = {
        options: [],
        value: '',
        onChange: () => {},
        onBlur: () => {},
        label: '',
        name: 'input',
        menuPlacement: 'auto',
    };

    return MockInputSection;
});

jest.mock('../../components/InitialClaimFlow/ClaimForm/ClaimEmissionsEstimate/ClaimEmissionsEstimate', () => () => (
    <div data-testid="emissions-estimate">Emissions Estimate</div>
));

beforeAll(() => {
    // eslint-disable-next-line no-underscore-dangle
    if (!window._scrollToStubbed) {
        window.scrollTo = jest.fn();
        // eslint-disable-next-line no-underscore-dangle
        window._scrollToStubbed = true;
    }
});

describe('ProfileStep component', () => {
    const mockHandleChange = jest.fn();
    const mockHandleBlur = jest.fn();
    const mockUpdateFieldWithoutTouch = jest.fn();
    const mockOnEmissionsValidationChange = jest.fn();

    const defaultProps = {
        formData: {
            localLanguageName: '',
            officePhoneNumber: '',
            businessWebsite: '',
            facilityDescription: '',
            parentCompanyName: '',
            officeOfficialName: '',
            officeAddress: '',
            officeCountryCode: '',
            sectors: [],
            facilityType: [],
            facilityProductionTypes: [],
            facilityProductTypes: [],
            numberOfWorkers: '',
            facilityFemaleWorkersPercentage: '',
            facilityMinimumOrderQuantity: '',
            facilityAverageLeadTime: '',
            facilityAffiliations: [],
            facilityCertifications: [],
        },
        handleChange: mockHandleChange,
        handleBlur: mockHandleBlur,
        updateFieldWithoutTouch: mockUpdateFieldWithoutTouch,
        touched: {},
        errors: {},
        countryOptions: [
            { value: 'US', label: 'United States' },
            { value: 'CN', label: 'China' },
        ],
        processingTypeOptions: [
            { value: 'assembly', label: 'Assembly' },
            { value: 'cutting', label: 'Cutting' },
        ],
        parentCompanyOptions: [
            { value: '1', label: 'Parent Company Inc.' },
        ],
        onEmissionsValidationChange: mockOnEmissionsValidationChange,
    };

    const preloadedState = {};

    const renderComponent = (props = {}, state = preloadedState) =>
        renderWithProviders(<ProfileStep {...defaultProps} {...props} />, {
            preloadedState: state,
        });

    afterEach(() => {
        jest.clearAllMocks();
    });

    test('renders all four expansion panel sections', () => {
        renderComponent();

        expect(screen.getByText('Production Location Overview')).toBeInTheDocument();
        expect(screen.getByText('Company Information')).toBeInTheDocument();
        expect(screen.getByText('Operations & Capabilities')).toBeInTheDocument();
        expect(screen.getByText('Compliance & Partnerships')).toBeInTheDocument();
    });

    test('renders emissions estimate section', () => {
        renderComponent();

        expect(screen.getByText('Environmental Data')).toBeInTheDocument();
        expect(screen.getByTestId('emissions-estimate')).toBeInTheDocument();
    });

    test('displays beta labels on premium fields', () => {
        renderComponent();

        const betaLabels = screen.getAllByText('BETA');
        expect(betaLabels.length).toBeGreaterThan(0);
    });

    test('hides business website field when already provided', () => {
        renderComponent({
            formData: {
                ...defaultProps.formData,
                businessWebsite: 'https://company.com',
            },
        });

        const websiteInputs = screen.queryAllByPlaceholderText('https://company.com');
        expect(websiteInputs.length).toBe(0);
    });

    test('shows business website field when not provided', () => {
        renderComponent();

        expect(screen.getByPlaceholderText('https://company.com')).toBeInTheDocument();
    });
});

