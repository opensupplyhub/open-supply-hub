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
            'companyName',
        );
        await expect(
            schema.validate({
                ...validBusinessValues,
                companyName: '',
                companyAddress: '',
            }),
        ).resolves.toBeTruthy();
    });

    it('requires non-empty company name and address when editing is enabled', async () => {
        const schema = getBusinessStepSchema({ isNameAddressEditable: true });

        expect(Object.keys(schema.describe().fields)).toEqual(
            expect.arrayContaining(['companyName', 'companyAddress']),
        );
        await expect(
            schema.validate(
                { ...validBusinessValues, companyName: '', companyAddress: '   ' },
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
                companyName: 'Factory',
                companyAddress: '1 Main St',
            }),
        ).resolves.toBeTruthy();
    });

    it('caps company name and address length when editing is enabled', async () => {
        const schema = getBusinessStepSchema({ isNameAddressEditable: true });

        await expect(
            schema.validate({
                ...validBusinessValues,
                companyName: 'a'.repeat(201),
                companyAddress: '1 Main St',
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

        expect(Object.keys(business.describe().fields)).toContain('companyName');
        expect(Object.keys(businessDefault.describe().fields)).not.toContain(
            'companyName',
        );
        expect(Object.keys(contact.describe().fields)).not.toContain(
            'companyName',
        );
    });
});
