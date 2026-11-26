/* eslint-env jest */
import {
    CLAIMED_FILTER,
    DASHBOARD_PAGE_SIZE,
    apiLimitLabel,
    barPercent,
    buildContributionsQueryString,
    buildDashboardQueryString,
    claimedDataRows,
    extractErrorMessage,
    formatCount,
    isOnboardingComplete,
    monthLabel,
    onboardingSteps,
    pageRangeLabel,
    percentOf,
    roleLabel,
    seatsLabel,
} from '../../components/Organization/utils';

describe('labels', () => {
    test('roleLabel names the two roles and passes anything else through', () => {
        expect(roleLabel('ADMIN')).toBe('Admin');
        expect(roleLabel('MEMBER')).toBe('Member');
        expect(roleLabel('OWNER')).toBe('OWNER');
        expect(roleLabel(undefined)).toBe('');
    });

    test('seatsLabel', () => {
        expect(seatsLabel(2, 10)).toBe('2 of 10 seats used');
    });

    test('monthLabel turns a year-month into words', () => {
        expect(monthLabel('2026-11')).toBe('Nov 2026');
        expect(monthLabel('2026-01')).toBe('Jan 2026');
        expect(monthLabel('nonsense')).toBe('nonsense');
    });

    test('pageRangeLabel', () => {
        expect(pageRangeLabel(1, 20, 45)).toBe('1–20 of 45');
        expect(pageRangeLabel(3, 20, 45)).toBe('41–45 of 45');
        expect(pageRangeLabel(1, 20, 0)).toBe('0 of 0');
    });
});

describe('numbers', () => {
    test('percentOf is safe when the total is zero', () => {
        expect(percentOf(1, 4)).toBe(25);
        expect(percentOf(0, 0)).toBe(0);
    });

    test('barPercent keeps a small value visible', () => {
        expect(barPercent(50, 100)).toBe(50);
        expect(barPercent(1, 1000)).toBe(2);
        expect(barPercent(5, 0)).toBe(0);
    });
});

describe('extractErrorMessage', () => {
    const errorWith = data => ({ response: { data } });

    test('reads a field error', () => {
        expect(
            extractErrorMessage(
                errorWith({ email: ['No confirmed OS Hub account.'] }),
                'fallback',
            ),
        ).toBe('No confirmed OS Hub account.');
    });

    test('reads a detail message, a list and a bare string', () => {
        expect(extractErrorMessage(errorWith({ detail: 'Nope.' }), 'x')).toBe(
            'Nope.',
        );
        expect(extractErrorMessage(errorWith(['Expired.']), 'x')).toBe(
            'Expired.',
        );
        expect(extractErrorMessage(errorWith('Plain.'), 'x')).toBe('Plain.');
    });

    test('falls back when there is nothing to read', () => {
        expect(extractErrorMessage(new Error('network'), 'fallback')).toBe(
            'fallback',
        );
        expect(extractErrorMessage(errorWith({}), 'fallback')).toBe('fallback');
        expect(extractErrorMessage(errorWith([]), 'fallback')).toBe('fallback');
    });
});

describe('query strings', () => {
    test('dashboard filters leave out what is not set', () => {
        expect(
            buildDashboardQueryString({
                member: '',
                dateFrom: '',
                dateTo: '',
                claimed: CLAIMED_FILTER.ALL,
            }),
        ).toBe('');
    });

    test('dashboard filters and paging', () => {
        expect(
            buildDashboardQueryString(
                {
                    member: '7',
                    dateFrom: '2026-01-01',
                    dateTo: '2026-06-30',
                    claimed: CLAIMED_FILTER.CLAIMED,
                },
                2,
            ),
        ).toBe(
            `member=7&date_from=2026-01-01&date_to=2026-06-30&claimed=true&page=2&pageSize=${DASHBOARD_PAGE_SIZE}`,
        );
    });

    test('contributions', () => {
        expect(buildContributionsQueryString('claims', 3)).toBe(
            `type=claims&page=3&pageSize=${DASHBOARD_PAGE_SIZE}`,
        );
    });
});

describe('claimedDataRows', () => {
    test('is empty without a claim', () => {
        expect(claimedDataRows(null)).toEqual([]);
    });

    test('leaves out what the claimant did not publish', () => {
        const rows = claimedDataRows({
            claimed_by: 'Example Mill',
            facility: {
                description: 'A mill',
                website: null,
                phone_number: null,
                workers_count: '120',
                sector: ['Apparel', 'Textiles'],
                certifications: [],
                parent_company: { id: 5, name: 'Example Group' },
            },
            contact: null,
            office: null,
        });

        expect(rows).toEqual([
            { label: 'Claimed by', value: 'Example Mill' },
            { label: 'Description', value: 'A mill' },
            { label: 'Parent company', value: 'Example Group' },
            { label: 'Number of workers', value: '120' },
            { label: 'Sector', value: 'Apparel, Textiles' },
        ]);
    });

    test('shows contact and office details that were published', () => {
        const rows = claimedDataRows({
            facility: {},
            contact: { name: 'Ana', email: 'ana@mill.example' },
            office: { name: 'HQ', country: 'IN' },
        });

        expect(rows.map(row => row.label)).toEqual([
            'Contact name',
            'Contact email',
            'Office name',
            'Office country',
        ]);
    });
});

describe('onboardingSteps', () => {
    test('marks each step from the progress the API reports', () => {
        const steps = onboardingSteps(
            {
                has_contributions: true,
                has_colleagues: false,
                has_claims: false,
            },
            true,
        );

        expect(steps.map(step => [step.key, step.done])).toEqual([
            ['contribute', true],
            ['invite', false],
            ['claim', false],
        ]);
        expect(isOnboardingComplete(steps)).toBe(false);
    });

    test('is complete once every step is done', () => {
        const steps = onboardingSteps(
            { has_contributions: true, has_colleagues: true, has_claims: true },
            false,
        );

        expect(isOnboardingComplete(steps)).toBe(true);
    });

    test('tells an Admin to invite and a Member to ask an Admin', () => {
        const invite = isAdmin =>
            onboardingSteps({}, isAdmin).find(step => step.key === 'invite')
                .hint;

        expect(invite(true)).toMatch(/Invite people/);
        expect(invite(false)).toMatch(/An Admin of your organization/);
    });

    test('treats missing progress as nothing done', () => {
        expect(
            onboardingSteps(null, false).every(step => step.done === false),
        ).toBe(true);
    });
});

describe('usage formatting', () => {
    test('formatCount groups digits and shows a dash for unknown', () => {
        expect(formatCount(0)).toBe('0');
        expect(formatCount(4860)).toBe('4,860');
        expect(formatCount(null)).toBe('–');
        expect(formatCount(undefined)).toBe('–');
    });

    test('apiLimitLabel covers no access, no limit and a limit in use', () => {
        expect(apiLimitLabel(null)).toBe('No API access');
        expect(
            apiLimitLabel({
                calls: 3,
                limit: null,
                renewal_period: null,
                calls_this_period: null,
            }),
        ).toBe('No limit set');
        expect(
            apiLimitLabel({
                calls: 3,
                limit: 5000,
                renewal_period: 'MONTHLY',
                calls_this_period: 120,
            }),
        ).toBe('120 of 5,000 monthly');
        expect(
            apiLimitLabel({
                calls: 3,
                limit: 5000,
                renewal_period: null,
                calls_this_period: null,
            }),
        ).toBe('5,000');
    });
});
