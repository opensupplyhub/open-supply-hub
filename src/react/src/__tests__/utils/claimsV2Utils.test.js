import {
    businessDaysBetween,
    deriveClaimStage,
    CLAIM_STAGES,
} from '../../components/ClaimsV2/stageUtils';
import {
    composeMessage,
    MESSAGE_TEMPLATES,
    SENSITIVE_INFO_NOTICE,
} from '../../components/ClaimsV2/templates';
import {
    makeClaimTrackerTicketSearchURL,
    makeClaimTrackerBoardURL,
} from '../../components/ClaimsV2/jiraUtils';

const NOW = new Date('2026-09-01T12:00:00Z'); // a Tuesday

const note = (noteType, createdAt, text = 'note text') => ({
    note_type: noteType,
    created_at: createdAt,
    note: text,
});

describe('businessDaysBetween', () => {
    it('skips weekends', () => {
        // Friday -> Monday is one business day.
        expect(
            businessDaysBetween('2026-08-21T09:00:00Z', '2026-08-24T09:00:00Z'),
        ).toBe(1);
    });

    it('returns zero for same-day and invalid ranges', () => {
        expect(
            businessDaysBetween('2026-08-21T09:00:00Z', '2026-08-21T17:00:00Z'),
        ).toBe(0);
        expect(businessDaysBetween('not a date', NOW)).toBe(0);
    });
});

describe('deriveClaimStage', () => {
    it('returns "new" when no claimant message has been sent', () => {
        const result = deriveClaimStage(
            [note('INTERNAL', '2026-08-01T00:00:00Z')],
            { now: NOW },
        );
        expect(result.stage).toBe(CLAIM_STAGES.NEW);
        expect(result.lastMessagedAt).toBeNull();
    });

    it('degrades gracefully for legacy notes without note_type', () => {
        const legacyNote = { created_at: '2026-05-01T00:00:00Z', note: 'x' };
        expect(deriveClaimStage([legacyNote], { now: NOW }).stage).toBe(
            CLAIM_STAGES.NEW,
        );
        expect(deriveClaimStage(undefined, { now: NOW }).stage).toBe(
            CLAIM_STAGES.NEW,
        );
    });

    it('returns "awaiting" within the reply window', () => {
        // Messaged Tue 2026-08-25; five business days before NOW.
        const result = deriveClaimStage(
            [note('CLAIMANT_MESSAGE', '2026-08-25T09:00:00Z')],
            { now: NOW },
        );
        expect(result.stage).toBe(CLAIM_STAGES.AWAITING);
        expect(result.waitingBusinessDays).toBe(5);
    });

    it('returns "overdue" after more than 15 business days', () => {
        // Messaged Fri 2026-08-07; 17 business days before NOW.
        const result = deriveClaimStage(
            [note('CLAIMANT_MESSAGE', '2026-08-07T09:00:00Z')],
            { now: NOW },
        );
        expect(result.stage).toBe(CLAIM_STAGES.OVERDUE);
        expect(result.waitingBusinessDays).toBe(17);
    });

    it('uses the latest claimant message when several exist', () => {
        const result = deriveClaimStage(
            [
                note('CLAIMANT_MESSAGE', '2026-08-07T09:00:00Z'),
                note('CLAIMANT_MESSAGE', '2026-08-25T09:00:00Z'),
            ],
            { now: NOW },
        );
        expect(result.stage).toBe(CLAIM_STAGES.AWAITING);
    });

    it('returns "new" when the claimant updated after the last message', () => {
        const result = deriveClaimStage(
            [
                note('CLAIMANT_MESSAGE', '2026-08-07T09:00:00Z'),
                note('CLAIMANT_UPDATE', '2026-08-28T09:00:00Z'),
            ],
            { now: NOW },
        );
        expect(result.stage).toBe(CLAIM_STAGES.NEW);
        expect(result.reason).toContain('claimant updated');
    });
});

describe('composeMessage', () => {
    const context = {
        facilityName: 'Karavela SIA',
        facilityAddress: 'Atlantijas iela 15, Riga',
        jobTitle: 'Quality Manager',
        emailDomain: 'karavela.lv',
        osID: 'LV2023146T90PXR',
    };

    it('includes the sensitive-info notice exactly once when combining', () => {
        const message = composeMessage(['location', 'person'], context);
        const occurrences = message.split(SENSITIVE_INFO_NOTICE).length - 1;
        expect(occurrences).toBe(1);
        expect(message.endsWith(SENSITIVE_INFO_NOTICE)).toBe(true);
        expect(message).toContain('Karavela SIA');
        expect(message).toContain('Quality Manager');
    });

    it('does not append the notice for templates that lack it', () => {
        const message = composeMessage(['addressUpdate'], context);
        expect(message).not.toContain(SENSITIVE_INFO_NOTICE);
        expect(message).toContain('LV2023146T90PXR');
    });

    it('preserves template definition order regardless of selection order', () => {
        const message = composeMessage(['person', 'location'], context);
        const locationIndex = message.indexOf('verify the specific name');
        const personIndex = message.indexOf('claim policy');
        expect(locationIndex).toBeGreaterThan(-1);
        expect(personIndex).toBeGreaterThan(locationIndex);
    });

    it('every template builds against the shared context', () => {
        Object.keys(MESSAGE_TEMPLATES).forEach(key => {
            expect(MESSAGE_TEMPLATES[key].build(context)).toEqual(
                expect.any(String),
            );
        });
    });
});

describe('claim tracker Jira links', () => {
    it('builds a JQL search URL on the Claim ID field', () => {
        const url = makeClaimTrackerTicketSearchURL(5881);
        expect(url).toContain('opensupplyhub.atlassian.net/issues/?jql=');
        expect(decodeURIComponent(url)).toContain('project = CT');
        expect(decodeURIComponent(url)).toContain('"5881"');
    });

    it('falls back to the board URL for a non-numeric id', () => {
        expect(makeClaimTrackerTicketSearchURL('nope')).toBe(
            makeClaimTrackerBoardURL(),
        );
    });
});
