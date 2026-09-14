/* eslint-env jest */

import {
    parseAutomatedReview,
    getEvidenceText,
    getExtract,
    getSuggestedDraft,
    isPdfFile,
    P1_MARKER,
} from '../../components/ClaimsV2/automatedReviewUtils';

const block = payload =>
    `Automated review ran.\n\n${P1_MARKER}\n${JSON.stringify(payload)}`;

const validPayload = {
    v: 1,
    kind: 'automated_review',
    decision: 'NOT_VALIDATED',
    scores: { name: 0.85 },
    draft: 'Dear claimant, …',
    evidence: {
        'utility-bill.png': {
            original: 'Rēķins par elektroenerģiju',
            translated: 'Electricity invoice',
            lang: 'lv',
        },
        'no-text.png': {},
    },
};

const note = (text, createdAt = '2026-09-01T00:00:00Z') => ({
    note: text,
    created_at: createdAt,
    note_type: 'INTERNAL',
});

describe('parseAutomatedReview', () => {
    it('parses a valid v1 block out of the notes', () => {
        const review = parseAutomatedReview([note(block(validPayload))]);
        expect(review.decision).toBe('NOT_VALIDATED');
        expect(review.scores.name).toBe(0.85);
    });

    it('returns the newest valid block when the pipeline re-ran', () => {
        const older = block({ ...validPayload, decision: 'OLD' });
        const newer = block({ ...validPayload, decision: 'NEW' });
        const review = parseAutomatedReview([
            note(newer, '2026-09-10T00:00:00Z'),
            note(older, '2026-09-01T00:00:00Z'),
        ]);
        expect(review.decision).toBe('NEW');
    });

    it('degrades to null on absence, bad JSON, or wrong version', () => {
        expect(parseAutomatedReview([note('a plain note')])).toBeNull();
        expect(
            parseAutomatedReview([note(`${P1_MARKER}\n{not json`)]),
        ).toBeNull();
        expect(
            parseAutomatedReview([
                note(block({ ...validPayload, v: 2 })),
            ]),
        ).toBeNull();
        expect(
            parseAutomatedReview([
                note(block({ ...validPayload, kind: 'other' })),
            ]),
        ).toBeNull();
        expect(parseAutomatedReview(undefined)).toBeNull();
    });
});

describe('getEvidenceText', () => {
    const review = parseAutomatedReview([note(block(validPayload))]);

    it('returns original/translated/lang for a known file', () => {
        expect(getEvidenceText(review, 'utility-bill.png')).toEqual({
            original: 'Rēķins par elektroenerģiju',
            translated: 'Electricity invoice',
            lang: 'lv',
        });
    });

    it('returns null for unknown files, empty entries, or no review', () => {
        expect(getEvidenceText(review, 'missing.pdf')).toBeNull();
        expect(getEvidenceText(review, 'no-text.png')).toBeNull();
        expect(getEvidenceText(null, 'utility-bill.png')).toBeNull();
    });
});

describe('getSuggestedDraft', () => {
    it('returns the draft only when present and non-empty', () => {
        const review = parseAutomatedReview([note(block(validPayload))]);
        expect(getSuggestedDraft(review)).toBe('Dear claimant, …');
        expect(
            getSuggestedDraft(
                parseAutomatedReview([
                    note(block({ ...validPayload, draft: '  ' })),
                ]),
            ),
        ).toBeNull();
        expect(getSuggestedDraft(null)).toBeNull();
    });
});

describe('isPdfFile', () => {
    it('detects pdfs case-insensitively and rejects the rest', () => {
        expect(isPdfFile('doc.pdf')).toBe(true);
        expect(isPdfFile('DOC.PDF')).toBe(true);
        expect(isPdfFile('scan.png')).toBe(false);
        expect(isPdfFile(undefined)).toBe(false);
    });
});

describe('getExtract', () => {
    const review = {
        extracts: {
            address: {
                value: 'Atlantijas iela 15, Riga',
                source: 'utility-bill.png',
            },
            person: { value: 'Demo Claimant 1' },
            broken: { source: 'x.png' },
        },
    };

    it('returns the value and source for a present extract', () => {
        expect(getExtract(review, 'address')).toEqual({
            value: 'Atlantijas iela 15, Riga',
            source: 'utility-bill.png',
        });
    });

    it('tolerates a missing source', () => {
        expect(getExtract(review, 'person')).toEqual({
            value: 'Demo Claimant 1',
            source: null,
        });
    });

    it('returns null for absent/invalid extracts or no review', () => {
        expect(getExtract(review, 'name')).toBeNull();
        expect(getExtract(review, 'broken')).toBeNull();
        expect(getExtract(null, 'address')).toBeNull();
        expect(getExtract({}, 'address')).toBeNull();
    });
});
