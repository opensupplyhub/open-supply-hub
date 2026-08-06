import {
    mapSubmissionErrorsToFormFields,
    formatSubmissionErrorForDisplay,
    getTouchedFieldsFromErrors,
} from '../../components/InitialClaimFlow/ClaimForm/utils';
import { profileStepSchema } from '../../components/InitialClaimFlow/ClaimForm/validationSchemas';

describe('ClaimForm submission error helpers', () => {
    it('maps snake_case API field errors to Formik field errors', () => {
        const { fieldErrors, formErrors } = mapSubmissionErrorsToFormFields([
            'facility_product_types: Ensure this field has no more than 50 characters.',
            'facility_production_types: Ensure this field has no more than 50 characters.',
            'business_website: Ensure this field has no more than 200 characters.',
            'There is already a pending claim on this facility.',
        ]);

        expect(fieldErrors).toEqual({
            facilityProductTypes:
                'Ensure this field has no more than 50 characters.',
            facilityProductionTypes:
                'Ensure this field has no more than 50 characters.',
            businessWebsite:
                'Ensure this field has no more than 200 characters.',
        });
        expect(formErrors).toEqual([
            'There is already a pending claim on this facility.',
        ]);
    });

    it('joins multiple distinct errors for the same field', () => {
        const { fieldErrors } = mapSubmissionErrorsToFormFields([
            'business_website: Enter a valid URL for \'business_website\'.',
            'business_website: Ensure this field has no more than 200 characters.',
        ]);

        expect(fieldErrors.businessWebsite).toBe(
            "Enter a valid URL for 'business_website'.; Ensure this field has no more than 200 characters.",
        );
    });

    it('does not treat capitalized bare messages as API field errors', () => {
        const { fieldErrors, formErrors } = mapSubmissionErrorsToFormFields([
            'Error: try again later',
        ]);

        expect(fieldErrors).toEqual({});
        expect(formErrors).toEqual(['Error: try again later']);
    });

    it('formats field-prefixed errors for banner display using UI labels', () => {
        expect(
            formatSubmissionErrorForDisplay(
                'facility_product_types: Ensure this field has no more than 50 characters.',
            ),
        ).toBe(
            'Product Types: Ensure this field has no more than 50 characters.',
        );
        expect(
            formatSubmissionErrorForDisplay(
                'facility_type: Ensure this field has no more than 300 characters.',
            ),
        ).toBe(
            'Location Type(s): Ensure this field has no more than 300 characters.',
        );
        expect(
            formatSubmissionErrorForDisplay(
                'facility_production_types: Ensure this field has no more than 50 characters.',
            ),
        ).toBe(
            'Processing Type(s): Ensure this field has no more than 50 characters.',
        );
        expect(
            formatSubmissionErrorForDisplay(
                'There is already an approved claim on this facility.',
            ),
        ).toBe('There is already an approved claim on this facility.');
        expect(
            formatSubmissionErrorForDisplay('Error: try again later'),
        ).toBe('Error: try again later');
    });

    it('builds touched map from field errors', () => {
        expect(
            getTouchedFieldsFromErrors({
                facilityProductTypes: 'too long',
                businessWebsite: 'too long',
            }),
        ).toEqual({
            facilityProductTypes: true,
            businessWebsite: true,
        });
    });
});

describe('profileStepSchema select option length', () => {
    it('rejects product and processing types longer than 50 characters', async () => {
        const longValue =
            'printing , lamination , diecutting , hot stamping and etc';

        await expect(
            profileStepSchema.validateAt('facilityProductTypes', {
                facilityProductTypes: [{ value: longValue, label: longValue }],
            }),
        ).rejects.toThrow(/50 characters or fewer/);

        await expect(
            profileStepSchema.validateAt('facilityProductionTypes', {
                facilityProductionTypes: [
                    { value: longValue, label: longValue },
                ],
            }),
        ).rejects.toThrow(/50 characters or fewer/);
    });

    it('rejects location types whose pipe-joined value exceeds 300 characters', async () => {
        const options = [
            { value: 'a'.repeat(150), label: 'a'.repeat(150) },
            { value: 'b'.repeat(150), label: 'b'.repeat(150) },
        ];

        await expect(
            profileStepSchema.validateAt('facilityType', {
                facilityType: options,
            }),
        ).rejects.toThrow(/300 characters or fewer/);
    });

    it('allows a single location type longer than 50 characters when joined length is under 300', async () => {
        const longButUnderJoinedLimit = 'x'.repeat(80);

        await expect(
            profileStepSchema.validateAt('facilityType', {
                facilityType: [
                    {
                        value: longButUnderJoinedLimit,
                        label: longButUnderJoinedLimit,
                    },
                ],
            }),
        ).resolves.toBeDefined();
    });

    it('rejects website URLs longer than 200 characters', async () => {
        const longUrl = `https://${'a'.repeat(230)}.com`;

        await expect(
            profileStepSchema.validateAt('businessWebsite', {
                businessWebsite: longUrl,
            }),
        ).rejects.toThrow(/200 characters or fewer/);
    });
});
