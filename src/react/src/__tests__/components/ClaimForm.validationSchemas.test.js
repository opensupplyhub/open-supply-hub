import {
    getBusinessStepSchema,
    getValidationSchemaForStep,
} from '../../components/InitialClaimFlow/ClaimForm/validationSchemas';
import { CLAIM_FORM_STEPS } from '../../components/InitialClaimFlow/ClaimForm/constants';

const validBusinessValues = {
    locationAddressVerificationMethod:
        'Company website showing the production location address (e.g., Contact Us, Locations page)',
    businessWebsite: 'https://company.com/contact-us',
    businessLinkedinProfile: '',
    companyAddressVerificationDocuments: [],
};

describe('Business step schema: company name and address', () => {
    it('ignores company name and address when editing is disabled', async () => {
        const schema = getBusinessStepSchema({ isNameAddressEditable: false });

        expect(Object.keys(schema.describe().fields)).not.toContain(
            'facilityNameEnglish',
        );
        await expect(
            schema.validate({
                ...validBusinessValues,
                facilityNameEnglish: '',
                facilityAddress: '',
            }),
        ).resolves.toBeTruthy();
    });

    it('requires non-empty company name and address when editing is enabled', async () => {
        const schema = getBusinessStepSchema({ isNameAddressEditable: true });

        expect(Object.keys(schema.describe().fields)).toEqual(
            expect.arrayContaining(['facilityNameEnglish', 'facilityAddress']),
        );
        await expect(
            schema.validate(
                { ...validBusinessValues, facilityNameEnglish: '', facilityAddress: '   ' },
                { abortEarly: false },
            ),
        ).rejects.toMatchObject({
            errors: expect.arrayContaining([
                'Company name is required',
                'Company address is required',
            ]),
        });
        await expect(
            schema.validate({
                ...validBusinessValues,
                facilityNameEnglish: 'Factory',
                facilityAddress: '1 Main St',
            }),
        ).resolves.toBeTruthy();
    });

    it('caps company name and address length when editing is enabled', async () => {
        const schema = getBusinessStepSchema({ isNameAddressEditable: true });

        await expect(
            schema.validate({
                ...validBusinessValues,
                facilityNameEnglish: 'a'.repeat(201),
                facilityAddress: '1 Main St',
            }),
        ).rejects.toThrow('Company name must be 200 characters or fewer');
    });

    it('getValidationSchemaForStep passes the option through for the business step only', () => {
        const business = getValidationSchemaForStep(CLAIM_FORM_STEPS.BUSINESS, {
            isNameAddressEditable: true,
        });
        const businessDefault = getValidationSchemaForStep(
            CLAIM_FORM_STEPS.BUSINESS,
        );
        const contact = getValidationSchemaForStep(CLAIM_FORM_STEPS.CONTACT, {
            isNameAddressEditable: true,
        });

        expect(Object.keys(business.describe().fields)).toContain('facilityNameEnglish');
        expect(Object.keys(businessDefault.describe().fields)).not.toContain(
            'facilityNameEnglish',
        );
        expect(Object.keys(contact.describe().fields)).not.toContain(
            'facilityNameEnglish',
        );
    });
});
