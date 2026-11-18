/*
 * Pure helpers for the organization level: labels, query strings and
 * the shaping of API payloads for display. Kept free of React so they
 * can be unit-tested directly.
 */

export const ROLES = Object.freeze({
    ADMIN: 'ADMIN',
    MEMBER: 'MEMBER',
});

export const ROLE_LABELS = Object.freeze({
    [ROLES.ADMIN]: 'Admin',
    [ROLES.MEMBER]: 'Member',
});

export const roleLabel = role => ROLE_LABELS[role] || role || '';

export const CONTRIBUTION_TYPES = Object.freeze({
    LISTS: 'lists',
    CONTRIBUTIONS: 'contributions',
    CLAIMS: 'claims',
});

export const CONTRIBUTION_TYPE_LABELS = Object.freeze({
    [CONTRIBUTION_TYPES.LISTS]: 'Lists',
    [CONTRIBUTION_TYPES.CONTRIBUTIONS]: 'Single contributions',
    [CONTRIBUTION_TYPES.CLAIMS]: 'Claims',
});

export const CLAIMED_FILTER = Object.freeze({
    ALL: 'all',
    CLAIMED: 'true',
    UNCLAIMED: 'false',
});

export const DASHBOARD_PAGE_SIZE = 20;

export const DEFAULT_DASHBOARD_FILTERS = Object.freeze({
    member: '',
    dateFrom: '',
    dateTo: '',
    claimed: CLAIMED_FILTER.ALL,
});

export const seatsLabel = (seatsUsed, seatLimit) =>
    `${seatsUsed} of ${seatLimit} seats used`;

/*
 * The first human-readable message in a DRF error response, which can
 * be {detail: '...'}, {field: ['...']}, ['...'] or a bare string.
 */
export const extractErrorMessage = (error, fallback) => {
    const data = error && error.response && error.response.data;
    if (!data) return fallback;
    if (typeof data === 'string') return data;
    if (Array.isArray(data)) return data.length ? String(data[0]) : fallback;
    if (data.detail) return String(data.detail);

    const first = Object.values(data).find(
        value => value && (typeof value === 'string' || value.length),
    );
    if (!first) return fallback;
    return Array.isArray(first) ? String(first[0]) : String(first);
};

/* Query string for the dashboard endpoints; empty filters are left out. */
export const buildDashboardQueryString = (filters = {}, page) => {
    const params = new URLSearchParams();
    if (filters.member) params.set('member', filters.member);
    if (filters.dateFrom) params.set('date_from', filters.dateFrom);
    if (filters.dateTo) params.set('date_to', filters.dateTo);
    if (filters.claimed && filters.claimed !== CLAIMED_FILTER.ALL) {
        params.set('claimed', filters.claimed);
    }
    if (page) {
        params.set('page', page);
        params.set('pageSize', DASHBOARD_PAGE_SIZE);
    }
    return params.toString();
};

export const buildContributionsQueryString = (type, page) => {
    const params = new URLSearchParams();
    params.set('type', type);
    params.set('page', page);
    params.set('pageSize', DASHBOARD_PAGE_SIZE);
    return params.toString();
};

export const percentOf = (part, total) =>
    total > 0 ? Math.round((part / total) * 100) : 0;

/* Width of a bar relative to the largest value in its chart. */
export const barPercent = (value, max) =>
    max > 0 ? Math.max(2, Math.round((value / max) * 100)) : 0;

const MONTH_NAMES = Object.freeze([
    'Jan',
    'Feb',
    'Mar',
    'Apr',
    'May',
    'Jun',
    'Jul',
    'Aug',
    'Sep',
    'Oct',
    'Nov',
    'Dec',
]);

/* '2026-11' -> 'Nov 2026' */
export const monthLabel = month => {
    const [year, monthNumber] = String(month).split('-');
    const name = MONTH_NAMES[Number(monthNumber) - 1];
    return name ? `${name} ${year}` : String(month);
};

export const pageRangeLabel = (page, pageSize, count) => {
    if (!count) return '0 of 0';
    const first = (page - 1) * pageSize + 1;
    const last = Math.min(page * pageSize, count);
    return `${first}–${last} of ${count}`;
};

const joinList = value =>
    Array.isArray(value) ? value.filter(Boolean).join(', ') : value;

/*
 * The claimed data of a production location as label/value rows, in the
 * order the public profile presents it. Empty values are left out, so a
 * detail the claimant kept private (which the API returns as null)
 * simply does not appear.
 */
export const claimedDataRows = claim => {
    if (!claim) return [];
    const facility = claim.facility || {};
    const contact = claim.contact || {};
    const office = claim.office || {};
    const parentCompany = facility.parent_company || {};

    return [
        ['Claimed by', claim.claimed_by],
        ['Name (English)', facility.name_english],
        ['Name (native language)', facility.name_native_language],
        ['Address', facility.address],
        ['Description', facility.description],
        ['Website', facility.website],
        ['Phone number', facility.phone_number],
        ['Parent company', parentCompany.name],
        ['Number of workers', facility.workers_count],
        ['Percentage of female workers', facility.female_workers_percentage],
        ['Location type', joinList(facility.facility_type)],
        ['Sector', joinList(facility.sector)],
        ['Product types', joinList(facility.product_types)],
        ['Processing types', joinList(facility.production_types)],
        ['Certifications', joinList(facility.certifications)],
        ['Affiliations', joinList(facility.affiliations)],
        ['Minimum order', facility.minimum_order],
        ['Average lead time', facility.average_lead_time],
        ['Opening date', facility.opening_date],
        ['Estimated annual throughput', facility.estimated_annual_throughput],
        ['Contact name', contact.name],
        ['Contact email', contact.email],
        ['Office name', office.name],
        ['Office address', office.address],
        ['Office country', office.country],
        ['Office phone number', office.phone_number],
    ]
        .filter(
            ([, value]) =>
                value !== null && value !== undefined && value !== '',
        )
        .map(([label, value]) => ({ label, value: String(value) }));
};

/*
 * The first steps shown on the My Organization page, each marked done
 * from what the organization has already recorded. `progress` is the
 * onboarding payload; Admins and Members read the invite step
 * differently because only an Admin can invite.
 */
export const onboardingSteps = (progress, isAdmin) => [
    {
        key: 'contribute',
        done: Boolean(progress && progress.has_contributions),
        title: 'Contribute production location data',
        hint: 'Upload a list or add a single production location.',
    },
    {
        key: 'invite',
        done: Boolean(progress && progress.has_colleagues),
        title: 'Invite a colleague',
        hint: isAdmin
            ? 'Use "Invite people" below. They need an OS Hub account first.'
            : 'An Admin of your organization can invite colleagues who have an OS Hub account.',
    },
    {
        key: 'claim',
        done: Boolean(progress && progress.has_claims),
        title: 'Claim a production location',
        hint:
            'Find a production location your organization owns or manages and claim its profile.',
    },
];

export const isOnboardingComplete = steps => steps.every(step => step.done);

/* A count for a table cell: grouped digits, or a dash when unknown. */
export const formatCount = value =>
    value === null || value === undefined
        ? '–'
        : Number(value).toLocaleString('en-US');

/*
 * A member's API usage for the usage table: what they used of their
 * limit in its current period, or why there is nothing to show.
 */
export const apiLimitLabel = api => {
    if (!api) return 'No API access';
    if (api.limit === null || api.limit === undefined) return 'No limit set';
    const period = api.renewal_period
        ? ` ${api.renewal_period.toLowerCase()}`
        : '';
    if (api.calls_this_period === null || api.calls_this_period === undefined) {
        return `${formatCount(api.limit)}${period}`;
    }
    return `${formatCount(api.calls_this_period)} of ${formatCount(
        api.limit,
    )}${period}`;
};
