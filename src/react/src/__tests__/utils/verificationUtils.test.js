/* eslint-env jest */

import {
    scoreChip,
    normalizeOrgName,
    orgNamesConsistent,
    organizationRowStatus,
    CHIP_STATUS,
} from '../../components/ClaimsV2/verificationUtils';

const review = {
    scores: { name: 0.85, address: 0.55, affiliation: 0.61 },
    reasoning: { address: 'Street number missing from the profile.' },
};

describe('scoreChip', () => {
    it('renders a green clears-threshold chip at or above threshold', () => {
        const chip = scoreChip(review, 'name');
        expect(chip.status).toBe(CHIP_STATUS.PASS);
        expect(chip.text).toBe('✓ 0.85 ≥ 0.60 · clears threshold');
        expect(chip.reasoning).toBeNull();
    });

    it('renders advisory amber with reasoning below threshold', () => {
        const chip = scoreChip(review, 'address');
        expect(chip.status).toBe(CHIP_STATUS.CHECK);
        expect(chip.text).toBe('⚠ 0.55 < 0.60 · below threshold');
        expect(chip.reasoning).toBe(
            'Street number missing from the profile.',
        );
    });

    it('respects a per-criterion thresholds snapshot when present', () => {
        const strict = { ...review, thresholds: { name: 0.9 } };
        expect(scoreChip(strict, 'name').status).toBe(CHIP_STATUS.CHECK);
    });

    it('degrades to needs-your-judgement without automation data', () => {
        const chip = scoreChip(null, 'name');
        expect(chip.status).toBe(CHIP_STATUS.NONE);
        expect(chip.text).toBe(
            'No automated review — check the documents',
        );
        expect(scoreChip({ scores: {} }, 'person').status).toBe(
            CHIP_STATUS.NONE,
        );
    });
});

describe('normalizeOrgName / orgNamesConsistent', () => {
    it('normalizes case, punctuation, and spacing', () => {
        expect(normalizeOrgName('Karavela, SIA!')).toBe('karavelasia');
    });

    it('accepts containment in either direction', () => {
        expect(orgNamesConsistent('Karavela SIA', 'KARAVELA')).toBe(true);
        expect(orgNamesConsistent('Karavela', 'Karavela SIA Group')).toBe(
            true,
        );
        expect(orgNamesConsistent('Karavela SIA', 'Fromagerie')).toBe(false);
        expect(orgNamesConsistent('', 'Karavela')).toBe(false);
    });
});

describe('organizationRowStatus', () => {
    it('reads looks-consistent when the affiliation score passes', () => {
        const status = organizationRowStatus(
            review,
            'Karavela SIA',
            'Completely Different Org',
        );
        expect(status.status).toBe(CHIP_STATUS.PASS);
        expect(status.text).toBe('Looks consistent');
    });

    it('reads looks-consistent on a name match even without scores', () => {
        const status = organizationRowStatus(null, 'Karavela SIA', 'karavela');
        expect(status.status).toBe(CHIP_STATUS.PASS);
    });

    it('never renders a mismatch on string logic alone', () => {
        const failing = { scores: { affiliation: 0.2 } };
        const status = organizationRowStatus(
            failing,
            'Karavela SIA',
            'Different Org',
        );
        expect(status.status).toBe(CHIP_STATUS.CHECK);
        expect(status.reasoning).toContain('rebrands');
    });

    it('degrades to no-automation when there is neither signal', () => {
        const status = organizationRowStatus(null, 'Karavela SIA', 'Other');
        expect(status.status).toBe(CHIP_STATUS.NONE);
    });
});
