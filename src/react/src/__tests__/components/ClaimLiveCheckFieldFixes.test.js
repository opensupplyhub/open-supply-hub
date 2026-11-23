import React from 'react';
import { MemoryRouter } from 'react-router-dom';

import renderWithProviders from '../../util/testUtils/renderWithProviders';
import ContactInfoStep from '../../components/InitialClaimFlow/ClaimForm/Steps/ContactInfoStep/ContactInfoStep';
import BusinessStep from '../../components/InitialClaimFlow/ClaimForm/Steps/BusinessStep/BusinessStep';
import {
    EMPLOYMENT_VERIFICATION_OPTIONS,
    EMPLOYMENT_DOCUMENT_BASED_VERIFICATION_OPTIONS,
} from '../../components/InitialClaimFlow/ClaimForm/Steps/ContactInfoStep/constants';
import {
    COMPANY_ADDRESS_VERIFICATION_OPTIONS,
    DOCUMENT_BASED_VERIFICATION_OPTIONS,
} from '../../components/InitialClaimFlow/ClaimForm/Steps/BusinessStep/constants';
import COLOURS from '../../util/COLOURS';

// The real selector is heavy. The stand-in shows whether the step
// asked for it to be outlined in red.
jest.mock('../../components/Filters/StyledSelect', () => ({ name, styles }) => (
    <select
        data-testid={name}
        aria-label={name}
        data-border={styles.control({}, { isFocused: false }).borderColor}
    />
));

const mockHistoryPush = jest.fn();
jest.mock('react-router-dom', () => {
    const actual = jest.requireActual('react-router-dom');
    return {
        ...actual,
        useHistory: () => ({ push: mockHistoryPush }),
        useLocation: () => ({
            pathname: '/claimed/pending/12',
            search: '',
            hash: '',
            state: null,
        }),
    };
});

const WHO_DOCUMENT =
    'Add a document that shows your name and your company. For example a business card, employment letter or ID badge.';
const UPLOAD =
    'Upload a document. Claims with a document are approved fastest.';
const COMPANY_NAME = 'Add an official document that shows the company name.';
const FLAGGED_BORDER = `2px solid ${COLOURS.RED.toLowerCase()}`;

const labelOf = (options, values) =>
    options.find(option => values.includes(option.value)).label;

const stepProps = {
    handleChange: jest.fn(),
    handleBlur: jest.fn(),
    updateFieldWithoutTouch: jest.fn(),
    errors: {},
    touched: {},
};

const preloadedState = {
    auth: { user: { user: { email: 'someone@gmail.com', isAnon: false } } },
    contributeProductionLocation: {
        singleProductionLocation: {
            data: { os_id: 'US2021250D1DTN7', name: 'Name', address: 'Address' },
        },
    },
};

const renderStep = (Step, formData, liveCheckFixes) =>
    renderWithProviders(
        <MemoryRouter>
            <Step
                {...stepProps}
                formData={formData}
                {...(liveCheckFixes ? { liveCheckFixes } : {})}
            />
        </MemoryRouter>,
        { preloadedState },
    );

const uploadArea = container =>
    container.querySelector('[data-testid="claim-attachments-uploader"] label');

describe('live check fixes on the claim form fields', () => {
    beforeAll(() => {
        window.scrollTo = jest.fn();
        global.URL.createObjectURL = jest.fn();
    });

    test('nothing is marked unless fixes are passed', () => {
        const contact = renderStep(ContactInfoStep, {});
        expect(contact.queryByTestId('live-check-field-fixes')).toBeNull();
        expect(
            contact.getByTestId('claimantEmploymentVerificationMethod'),
        ).not.toHaveAttribute('data-border', COLOURS.RED);
        contact.unmount();

        const business = renderStep(BusinessStep, {});
        expect(business.queryByTestId('live-check-field-fixes')).toBeNull();
        expect(
            business.getByTestId('locationAddressVerificationMethod'),
        ).not.toHaveAttribute('data-border', COLOURS.RED);
    });

    test('the employment selector is marked when no upload area is shown', () => {
        const { getByText, getByTestId, container } = renderStep(
            ContactInfoStep,
            {},
            { employment: ['name_and_company_document'] },
        );

        expect(getByText(WHO_DOCUMENT)).toBeInTheDocument();
        expect(
            getByTestId('claimantEmploymentVerificationMethod'),
        ).toHaveAttribute('data-border', COLOURS.RED);
        expect(uploadArea(container)).toBeNull();
    });

    test('the employment upload area is marked instead when it is shown', () => {
        const { getAllByText, getByTestId, container } = renderStep(
            ContactInfoStep,
            {
                claimantEmploymentVerificationMethod: labelOf(
                    EMPLOYMENT_VERIFICATION_OPTIONS,
                    EMPLOYMENT_DOCUMENT_BASED_VERIFICATION_OPTIONS,
                ),
            },
            { employment: ['name_and_company_document'] },
        );

        expect(getAllByText(WHO_DOCUMENT)).toHaveLength(1);
        expect(uploadArea(container).style.border).toBe(FLAGGED_BORDER);
        expect(
            getByTestId('claimantEmploymentVerificationMethod'),
        ).not.toHaveAttribute('data-border', COLOURS.RED);
    });

    test('several fixes about the address proof are listed under that one field', () => {
        const { getByText, getByTestId, container } = renderStep(
            BusinessStep,
            {},
            { address: ['upload_document', 'company_name_document'] },
        );

        const blocks = container.querySelectorAll(
            '[data-testid="live-check-field-fixes"]',
        );
        expect(blocks).toHaveLength(1);
        expect(blocks[0]).toContainElement(getByText(UPLOAD));
        expect(blocks[0]).toContainElement(getByText(COMPANY_NAME));
        expect(
            getByTestId('locationAddressVerificationMethod'),
        ).toHaveAttribute('data-border', COLOURS.RED);
    });

    test('the address upload area is marked instead when it is shown', () => {
        const { getAllByText, getByTestId, container } = renderStep(
            BusinessStep,
            {
                locationAddressVerificationMethod: labelOf(
                    COMPANY_ADDRESS_VERIFICATION_OPTIONS,
                    DOCUMENT_BASED_VERIFICATION_OPTIONS,
                ),
            },
            { address: ['upload_document'] },
        );

        expect(getAllByText(UPLOAD)).toHaveLength(1);
        expect(uploadArea(container).style.border).toBe(FLAGGED_BORDER);
        // The focus ring is kept clear of the red border.
        expect(uploadArea(container).style.outlineOffset).toBe('4px');
        expect(
            getByTestId('locationAddressVerificationMethod'),
        ).not.toHaveAttribute('data-border', COLOURS.RED);
    });
});
