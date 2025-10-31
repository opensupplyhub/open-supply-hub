import React from 'react';
import { fireEvent, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import BusinessStep from '../../components/InitialClaimFlow/ClaimForm/Steps/BusinessStep/BusinessStep';

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
            data-testid="verification-select"
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
        name: 'locationAddressVerificationMethod',
    };

    return MockStyledSelect;
});

jest.mock('../../components/ClaimAttachmentsUploader', () => {
    // eslint-disable-next-line global-require
    const mockPropTypes = require('prop-types');
    const MockClaimAttachmentsUploader = ({
        inputId,
        title,
        files,
        updateUploadFiles,
    }) => (
        <div data-testid="attachments-uploader">
            <p>{title}</p>
            <input
                type="file"
                data-testid={inputId}
                onChange={e => {
                    const mockFiles = Array.from(e.target.files || []);
                    updateUploadFiles(mockFiles);
                }}
            />
            <div data-testid="uploaded-files-count">
                {files.length} file(s) uploaded
            </div>
        </div>
    );

    MockClaimAttachmentsUploader.propTypes = {
        inputId: mockPropTypes.string.isRequired,
        title: mockPropTypes.string.isRequired,
        files: mockPropTypes.array.isRequired,
        updateUploadFiles: mockPropTypes.func.isRequired,
    };

    return MockClaimAttachmentsUploader;
});

beforeAll(() => {
    window.scrollTo = jest.fn();
});

describe('BusinessStep component', () => {
    const mockHandleChange = jest.fn();
    const mockHandleBlur = jest.fn();
    const mockUpdateFieldWithoutTouch = jest.fn();

    const defaultProps = {
        formData: {
            locationAddressVerificationMethod: '',
            businessWebsite: '',
            businessLinkedinProfile: '',
            companyAddressVerificationDocuments: [],
        },
        handleChange: mockHandleChange,
        handleBlur: mockHandleBlur,
        updateFieldWithoutTouch: mockUpdateFieldWithoutTouch,
        errors: {},
        touched: {},
    };

    const preloadedState = {
        contributeProductionLocation: {
            singleProductionLocation: {
                data: {
                    os_id: 'US2021250D1DTN7',
                    name: 'Test Production Location',
                    address: '1234 Production St, City, State, 12345',
                },
            },
        },
    };

    const renderComponent = (props = {}, state = preloadedState) =>
        renderWithProviders(
            <MemoryRouter>
                <BusinessStep {...defaultProps} {...props} />
            </MemoryRouter>,
            {
                preloadedState: state,
            }
        );

    afterEach(() => {
        jest.clearAllMocks();
    });

    test('renders without crashing', () => {
        const { container } = renderComponent();
        expect(container).toBeInTheDocument();
    });

    test('displays production location details', () => {
        renderComponent();

        expect(screen.getByText('Production Location Details')).toBeInTheDocument();
        expect(screen.getByText('US2021250D1DTN7')).toBeInTheDocument();
        expect(screen.getAllByText('Test Production Location').length).toBeGreaterThan(0);
        expect(screen.getAllByText('1234 Production St, City, State, 12345').length).toBeGreaterThan(0);
    });

    test('displays verification section with select field', () => {
        renderComponent();

        expect(screen.getByText(/Company Address Verification/)).toBeInTheDocument();
        expect(
            screen.getByText(
                'You need to select and provide one of the below items for company address verification.'
            )
        ).toBeInTheDocument();

        const selectField = screen.getByTestId('verification-select');
        expect(selectField).toBeInTheDocument();
    });

    test('displays important warning message', () => {
        renderComponent();

        expect(screen.getByText('IMPORTANT!')).toBeInTheDocument();
        expect(
            screen.getByText(
                /Verification documents must show the same name and address/
            )
        ).toBeInTheDocument();
    });

    test('does not show URL input when no verification method is selected', () => {
        renderComponent();

        expect(screen.queryByPlaceholderText(/https:\/\//)).not.toBeInTheDocument();
    });

    test('shows URL input when company-website-address is selected', () => {
        const propsWithUrlVerification = {
            formData: {
                locationAddressVerificationMethod:
                    'Company website showing the production location address (e.g., Contact Us, Locations page)',
                businessWebsite: '',
                businessLinkedinProfile: '',
                companyAddressVerificationDocuments: [],
            },
        };

        renderComponent(propsWithUrlVerification);

        const urlInput = screen.getByPlaceholderText('https://company.com/contact-us');
        expect(urlInput).toBeInTheDocument();
    });

    test('shows URL input when linkedin-address is selected', () => {
        const propsWithLinkedInVerification = {
            formData: {
                locationAddressVerificationMethod:
                    'Company LinkedIn page showing the production location address',
                businessWebsite: '',
                businessLinkedinProfile: '',
                companyAddressVerificationDocuments: [],
            },
        };

        renderComponent(propsWithLinkedInVerification);

        const urlInput = screen.getByPlaceholderText('https://linkedin.com/company/yourcompany');
        expect(urlInput).toBeInTheDocument();
    });

    test('shows document uploader when utility-bill is selected', () => {
        const propsWithDocumentVerification = {
            formData: {
                locationAddressVerificationMethod:
                    'Utility bill showing company name and address',
                businessWebsite: '',
                businessLinkedinProfile: '',
                companyAddressVerificationDocuments: [],
            },
        };

        renderComponent(propsWithDocumentVerification);

        expect(screen.getByTestId('attachments-uploader')).toBeInTheDocument();
        expect(screen.getByText('Upload your documents')).toBeInTheDocument();
    });

    test('calls handleChange when URL input value changes', () => {
        const propsWithUrlVerification = {
            formData: {
                locationAddressVerificationMethod:
                    'Company website showing the production location address (e.g., Contact Us, Locations page)',
                businessWebsite: '',
                businessLinkedinProfile: '',
                companyAddressVerificationDocuments: [],
            },
        };

        renderComponent(propsWithUrlVerification);

        const urlInput = screen.getByPlaceholderText('https://company.com/contact-us');
        fireEvent.change(urlInput, { target: { value: 'https://test.com' } });

        expect(mockHandleChange).toHaveBeenCalledWith(
            'businessWebsite',
            'https://test.com'
        );
    });

    test('calls handleBlur when URL input loses focus', () => {
        const propsWithUrlVerification = {
            formData: {
                locationAddressVerificationMethod:
                    'Company website showing the production location address (e.g., Contact Us, Locations page)',
                businessWebsite: '',
                businessLinkedinProfile: '',
                companyAddressVerificationDocuments: [],
            },
        };

        renderComponent(propsWithUrlVerification);

        const urlInput = screen.getByPlaceholderText('https://company.com/contact-us');
        fireEvent.blur(urlInput);

        expect(mockHandleBlur).toHaveBeenCalledWith(
            'businessWebsite'
        );
    });

    test('displays error message for verification method when touched and has error', () => {
        const propsWithError = {
            touched: {
                locationAddressVerificationMethod: true,
            },
            errors: {
                locationAddressVerificationMethod: 'Verification method is required',
            },
        };

        renderComponent(propsWithError);

        expect(screen.getByText('Verification method is required')).toBeInTheDocument();
    });

    test('displays error message for URL when touched and has error', () => {
        const propsWithUrlError = {
            formData: {
                locationAddressVerificationMethod:
                    'Company website showing the production location address (e.g., Contact Us, Locations page)',
                businessWebsite: 'invalid-url',
                businessLinkedinProfile: '',
                companyAddressVerificationDocuments: [],
            },
            touched: {
                businessWebsite: true,
            },
            errors: {
                businessWebsite: 'Please enter a valid URL',
            },
        };

        renderComponent(propsWithUrlError);

        expect(screen.getByText('Please enter a valid URL')).toBeInTheDocument();
    });

    test('displays error message for documents when touched and has error', () => {
        const propsWithDocError = {
            formData: {
                locationAddressVerificationMethod:
                    'Utility bill showing company name and address',
                businessWebsite: '',
                businessLinkedinProfile: '',
                companyAddressVerificationDocuments: [],
            },
            touched: {
                companyAddressVerificationDocuments: true,
            },
            errors: {
                companyAddressVerificationDocuments: 'At least one document is required',
            },
        };

        renderComponent(propsWithDocError);

        expect(screen.getByText('At least one document is required')).toBeInTheDocument();
    });

    test('handles missing production location data gracefully', () => {
        const stateWithoutLocationData = {
            contributeProductionLocation: {
                singleProductionLocation: {
                    data: null,
                },
            },
        };

        const { container } = renderComponent({}, stateWithoutLocationData);

        expect(container).toBeInTheDocument();
        expect(screen.getByText('Production Location Details')).toBeInTheDocument();
    });

    test('displays OS ID link with correct URL structure', () => {
        renderComponent();

        const osIdLink = screen.getByText('US2021250D1DTN7');
        expect(osIdLink.closest('a')).toHaveAttribute('href', '/facilities/US2021250D1DTN7');
        expect(osIdLink.closest('a')).toHaveAttribute('target', '_blank');
    });

    test('verification select calls handleChange with label when option is selected', () => {
        renderComponent();

        const selectField = screen.getByTestId('verification-select');
        fireEvent.change(selectField, { target: { value: 'company-website-address' } });

        expect(mockHandleChange).toHaveBeenCalledWith(
            'locationAddressVerificationMethod',
            'Company website showing the production location address (e.g., Contact Us, Locations page)'
        );
    });

    test('document uploader shows correct number of uploaded files', () => {
        const propsWithFiles = {
            formData: {
                locationAddressVerificationMethod:
                    'Utility bill showing company name and address',
                businessWebsite: '',
                businessLinkedinProfile: '',
                companyAddressVerificationDocuments: [
                    { name: 'file1.pdf' },
                    { name: 'file2.pdf' },
                ],
            },
        };

        renderComponent(propsWithFiles);

        expect(screen.getByText('2 file(s) uploaded')).toBeInTheDocument();
    });

    test('all document-based verification options show uploader', () => {
        const documentOptions = [
            'Utility bill showing company name and address',
            'Business registration document',
            'Tax document or business license',
            'Property lease or ownership document',
            'Upload other official documents (business registration, utility bills, etc.)',
        ];

        documentOptions.forEach(option => {
            const { unmount } = renderComponent({
                formData: {
                    locationAddressVerificationMethod: option,
                    businessWebsite: '',
                    businessLinkedinProfile: '',
                    companyAddressVerificationDocuments: [],
                },
            });

            expect(screen.getByTestId('attachments-uploader')).toBeInTheDocument();
            unmount();
        });
    });
});

