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

describe('Profile step schema: ISIC selections', () => {
    const profile = getValidationSchemaForStep(CLAIM_FORM_STEPS.PROFILE);
    const codes = n =>
        Array.from({ length: n }, (_, i) => ({
            value: `class:${1000 + i}`,
            label: `Class ${i}`,
        }));

    it('accepts up to 15 codes per revision', async () => {
        await expect(
            profile.validate({ isic4: codes(15), isic5: codes(15) }),
        ).resolves.toBeTruthy();
    });

    it('rejects more than 15 codes, matching the API limit', async () => {
        await expect(profile.validate({ isic4: codes(16) })).rejects.toThrow(
            'Select up to 15 ISIC Rev. 4 codes',
        );
        await expect(profile.validate({ isic5: codes(16) })).rejects.toThrow(
            'Select up to 15 ISIC Rev. 5 codes',
        );
    });
});

describe('Contact step schema: claimant name and title length', () => {
    const contact = getValidationSchemaForStep(CLAIM_FORM_STEPS.CONTACT);

    it('rejects a name or title over 200 characters, matching the API limit', async () => {
        await expect(
            contact.validateAt('yourName', { yourName: 'a'.repeat(201) }),
        ).rejects.toThrow('Your full name must be 200 characters or fewer');
        await expect(
            contact.validateAt('yourTitle', { yourTitle: 'a'.repeat(201) }),
        ).rejects.toThrow('Your job title must be 200 characters or fewer');
    });

    it('accepts a name and title of 200 characters', async () => {
        await expect(
            contact.validateAt('yourName', { yourName: 'a'.repeat(200) }),
        ).resolves.toBeTruthy();
        await expect(
            contact.validateAt('yourTitle', { yourTitle: 'a'.repeat(200) }),
        ).resolves.toBeTruthy();
    });
});
