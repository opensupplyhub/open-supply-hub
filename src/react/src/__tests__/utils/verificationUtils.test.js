/* eslint-env jest */

import { claimantOrganization } from '../../components/ClaimsV2/verificationUtils';

describe('claimantOrganization', () => {
    it('prefers the claim-stated company, then the account name', () => {
        expect(
            claimantOrganization({
                company_name: 'Example Winery SARL',
                contributor: { name: 'Example Holdings' },
            }),
        ).toBe('Example Winery SARL');
        expect(
            claimantOrganization({
                company_name: '',
                contributor: { name: 'Example Holdings' },
            }),
        ).toBe('Example Holdings');
    });

    it('is empty when neither is known', () => {
        expect(claimantOrganization({ company_name: '' })).toBe('');
        expect(claimantOrganization({})).toBe('');
        expect(claimantOrganization(undefined)).toBe('');
    });
});
