import apiRequest from '../../util/apiRequest';
import {
    dismissedWarningsFor,
    fetchClaimQualityWarnings,
    makeDismissal,
    nameAddressUnchanged,
    toDismissedWarnings,
} from '../../util/claimQualityCheck';

jest.mock('../../util/apiRequest', () => ({
    post: jest.fn(),
}));

const warnings = [
    {
        type: 'name_quality',
        title: 'Name May Not Look Like a Facility Name',
        message: 'Looks like test data.',
    },
    {
        type: 'different_location',
        title: 'Details May Describe a Different Location',
        message: null,
    },
];

describe('claimQualityCheck util', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    describe('nameAddressUnchanged', () => {
        it('ignores case and surrounding whitespace', () => {
            expect(
                nameAddressUnchanged(
                    { name: '  Blue Horizon ', address: '1 Main St' },
                    { name: 'blue horizon', address: ' 1 Main St ' },
                ),
            ).toBe(true);
        });

        it('is false when either value differs', () => {
            const baseline = { name: 'Blue Horizon', address: '1 Main St' };
            expect(
                nameAddressUnchanged(
                    { name: 'Blue Horizon Ltd', address: '1 Main St' },
                    baseline,
                ),
            ).toBe(false);
            expect(
                nameAddressUnchanged(
                    { name: 'Blue Horizon', address: '2 Main St' },
                    baseline,
                ),
            ).toBe(false);
        });

        it('treats a missing baseline as different from any value', () => {
            expect(
                nameAddressUnchanged({ name: 'x', address: 'y' }, null),
            ).toBe(false);
            expect(
                nameAddressUnchanged({ name: '', address: '' }, undefined),
            ).toBe(true);
        });
    });

    describe('fetchClaimQualityWarnings', () => {
        it('posts the pair to the check endpoint and returns the warnings', async () => {
            apiRequest.post.mockResolvedValue({ data: { warnings } });

            const result = await fetchClaimQualityWarnings('OS123', {
                name: 'Test test',
                address: 'asdf',
            });

            expect(apiRequest.post).toHaveBeenCalledWith(
                '/api/facilities/OS123/claim/quality-check/',
                { facility_name_english: 'Test test', facility_address: 'asdf' },
            );
            expect(result).toEqual(warnings);
        });

        it('sends blanks for missing values', async () => {
            apiRequest.post.mockResolvedValue({ data: { warnings: [] } });

            await fetchClaimQualityWarnings('OS123', {});

            expect(apiRequest.post).toHaveBeenCalledWith(
                '/api/facilities/OS123/claim/quality-check/',
                { facility_name_english: '', facility_address: '' },
            );
        });

        it('fails open on a request error', async () => {
            apiRequest.post.mockRejectedValue(new Error('network'));

            await expect(
                fetchClaimQualityWarnings('OS123', { name: 'x', address: 'y' }),
            ).resolves.toEqual([]);
        });

        it('fails open on an unexpected response shape', async () => {
            apiRequest.post.mockResolvedValue({ data: 'not an object' });

            await expect(
                fetchClaimQualityWarnings('OS123', { name: 'x', address: 'y' }),
            ).resolves.toEqual([]);
        });
    });

    describe('dismissals', () => {
        it('reports type and message only, with an empty message for null', () => {
            expect(toDismissedWarnings(warnings)).toEqual([
                { type: 'name_quality', message: 'Looks like test data.' },
                { type: 'different_location', message: '' },
            ]);
        });

        it('remembers the values a dismissal was granted for', () => {
            expect(
                makeDismissal({ name: ' Test test ', address: 'asdf' }, warnings),
            ).toEqual({
                name: 'Test test',
                address: 'asdf',
                warnings: toDismissedWarnings(warnings),
            });
        });

        it('applies a dismissal only while the values are unchanged', () => {
            const dismissal = makeDismissal(
                { name: 'Test test', address: 'asdf' },
                warnings,
            );

            expect(
                dismissedWarningsFor(
                    { name: 'test test', address: 'asdf ' },
                    dismissal,
                ),
            ).toEqual(dismissal.warnings);
            expect(
                dismissedWarningsFor(
                    { name: 'Real Name', address: 'asdf' },
                    dismissal,
                ),
            ).toEqual([]);
            expect(
                dismissedWarningsFor({ name: 'x', address: 'y' }, null),
            ).toEqual([]);
        });
    });
});
