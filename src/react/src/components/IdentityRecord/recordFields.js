/*
 * Reading a Digital Facility Record for display.
 *
 * The credential is passed through from the API unmapped, because the
 * backend deliberately does not flatten it: which fields are shown, and
 * under what labels, is this page's decision rather than the service's.
 * These helpers are where that decision lives.
 *
 * Nothing here may assume a shape. The backend checks only that the
 * document is an object carrying credentialSubject, so every value below
 * is an issuer's to choose, and JSON-LD compaction routinely turns a
 * one-element list into a bare object. A `.map` on such a value throws
 * during render, and the boundary that catches it wraps the whole
 * application rather than this page, so a single odd record would take
 * the site down for the visitor. Hence asArray and asText.
 */

// A list the issuer may have written as a single value, or as nothing.
export const asArray = value => {
    if (Array.isArray(value)) {
        return value;
    }
    return value === null || value === undefined ? [] : [value];
};

/*
 * A value that has to render as text. Objects and arrays are dropped
 * rather than coerced: React throws on an object child, and
 * "[object Object]" is worse than an absent row.
 */
export const asText = value => {
    if (typeof value === 'string') {
        return value || null;
    }
    if (typeof value === 'number' || typeof value === 'boolean') {
        return String(value);
    }
    return null;
};

export const formatAddress = address => {
    if (!address) {
        return null;
    }

    // An issuer may send one address or a list of them; read the first.
    const [first] = asArray(address);
    if (!first) {
        return null;
    }
    if (typeof first === 'string') {
        return first || null;
    }

    const country = first.addressCountry || {};
    const parts = [
        asText(first.streetAddress),
        asText(first.addressLocality),
        asText(first.addressRegion),
        asText(first.postalCode),
        asText(country.countryName) || asText(country.countryCode),
    ].filter(Boolean);

    return parts.length ? parts.join(', ') : null;
};

export const getSubject = credential => {
    // credentialSubject is a list in JSON-LD as often as it is an object.
    const [subject] = asArray(credential?.credentialSubject);
    return subject && typeof subject === 'object' ? subject : {};
};

export const getProcessCategories = credential =>
    asArray(getSubject(credential).processCategory)
        .map(category =>
            typeof category === 'string'
                ? category
                : asText(category?.name) || asText(category?.code),
        )
        .filter(Boolean);

/*
 * The claims carried on the record.
 *
 * Worth being careful with these. Every claim observed on the pilot
 * records is self-declared, with a score of "Declared" rather than the
 * result of an on-site assessment. Presenting them as assessments would
 * overstate what the issuer is saying, so the score is surfaced alongside
 * each one rather than being dropped.
 */
export const getClaims = credential =>
    asArray(getSubject(credential).performanceClaim).map((claim, index) => ({
        key: asText(claim?.id) || `claim-${index}`,
        name: asText(claim?.name) || 'Claim',
        claimDate: asText(claim?.claimDate),
        scores: asArray(claim?.claimedPerformance)
            .map(performance => asText(performance?.score?.code))
            .filter(Boolean),
        topics: asArray(claim?.conformityTopic)
            .map(topic => asText(topic?.name))
            .filter(Boolean),
        criteria: asArray(claim?.referenceCriteria)
            .map(criterion => asText(criterion?.name))
            .filter(Boolean),
    }));

export const getOperator = credential => {
    const parties = asArray(getSubject(credential).relatedParty);
    const operator = parties.find(party => party?.role === 'operator');
    return asText(operator?.party?.name);
};

/*
 * Messages for each failure the retrieval service can report.
 *
 * Deliberately one per typed reason rather than a single generic string:
 * a record that exists and is briefly unreachable is a different thing
 * from one we are not allowed to read, and a visitor who is told which
 * can decide whether to come back.
 */
export const FAILURE_MESSAGES = {
    not_registered: 'No record is registered against this identifier yet.',
    timeout:
        'The issuer did not respond in time. The record still exists and ' +
        'this is usually temporary.',
    unreachable:
        'The issuer could not be reached. The record still exists and ' +
        'this is usually temporary.',
    upstream_error:
        'The issuer returned an error. The record still exists and this ' +
        'is usually temporary.',
    malformed: 'The record could not be read in the format it was returned in.',
    encrypted:
        'This record is encrypted. Encrypted records are not shown here.',
    unsafe_uri: 'The registered address for this record cannot be opened.',
};

export const failureMessage = reason =>
    FAILURE_MESSAGES[reason] ||
    'The record is temporarily unavailable. The production location below ' +
        'is unaffected.';
