import claimedFacilityDetailsSchema, {
    CLAIMED_TEXT_MAX_LENGTH,
} from '../../components/ClaimedFacilitiesDetails/validationSchema';

const validate = values =>
    claimedFacilityDetailsSchema.validate(values, { abortEarly: false });

describe('Claimed facility details schema: English name and address', () => {
    it('accepts ordinary values', async () => {
        await expect(
            validate({
                facility_name_english: 'Factory',
                facility_address: '1 Main St, Springfield',
            }),
        ).resolves.toBeTruthy();
    });

    it('accepts blank, whitespace-only and null values', async () => {
        await expect(
            validate({ facility_name_english: '', facility_address: '   ' }),
        ).resolves.toBeTruthy();
        await expect(
            validate({ facility_name_english: null, facility_address: null }),
        ).resolves.toBeTruthy();
    });

    it('rejects values over the maximum length', async () => {
        await expect(
            validate({
                facility_name_english: 'a'.repeat(CLAIMED_TEXT_MAX_LENGTH + 1),
                facility_address: 'b'.repeat(CLAIMED_TEXT_MAX_LENGTH + 1),
            }),
        ).rejects.toMatchObject({
            errors: expect.arrayContaining([
                `Facility name must be ${CLAIMED_TEXT_MAX_LENGTH} characters or fewer`,
                `Facility address must be ${CLAIMED_TEXT_MAX_LENGTH} characters or fewer`,
            ]),
        });
    });

    it('rejects values made only of the punctuation the backend strips', async () => {
        await expect(
            validate({
                facility_name_english: '-- , /',
                facility_address: "':,-",
            }),
        ).rejects.toMatchObject({
            errors: expect.arrayContaining([
                'Facility name cannot consist solely of punctuation or whitespace',
                'Facility address cannot consist solely of punctuation or whitespace',
            ]),
        });
    });
});
