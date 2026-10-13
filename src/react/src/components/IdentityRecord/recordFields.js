/*
 * Reading a Digital Facility Record for display.
 *
 * The credential is passed through from the API unmapped, because the
 * backend deliberately does not flatten it: which fields are shown, and
 * under what labels, is this page's decision rather than the service's.
 * These helpers are where that decision lives.
 */

export const formatAddress = address => {
    if (!address) {
        return null;
    }

    const parts = [
        address.streetAddress,
        address.addressLocality,
        address.addressRegion,
        address.postalCode,
        address.addressCountry?.countryName ||
            address.addressCountry?.countryCode,
    ].filter(Boolean);

    return parts.length ? parts.join(', ') : null;
};

export const getSubject = credential => credential?.credentialSubject || {};

export const getIssuerId = credential => {
    const { issuer } = credential || {};
    if (!issuer) {
        return null;
    }
    return typeof issuer === 'string' ? issuer : issuer.id || null;
};

export const getProcessCategories = credential =>
    (getSubject(credential).processCategory || [])
        .map(category => category?.name || category?.code)
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
    (getSubject(credential).performanceClaim || []).map((claim, index) => ({
        key: claim?.id || `claim-${index}`,
        name: claim?.name || 'Claim',
        claimDate: claim?.claimDate || null,
        scores: (claim?.claimedPerformance || [])
            .map(performance => performance?.score?.code)
            .filter(Boolean),
        topics: (claim?.conformityTopic || [])
            .map(topic => topic?.name)
            .filter(Boolean),
        criteria: (claim?.referenceCriteria || [])
            .map(criterion => criterion?.name)
            .filter(Boolean),
    }));

export const getOperator = credential => {
    const parties = getSubject(credential).relatedParty || [];
    const operator = parties.find(party => party?.role === 'operator');
    const name = operator?.party?.name;
    return name || null;
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
    not_registered:
        'No record is registered against this identifier yet.',
    timeout:
        'The issuer did not respond in time. The record still exists and ' +
        'this is usually temporary.',
    unreachable:
        'The issuer could not be reached. The record still exists and ' +
        'this is usually temporary.',
    upstream_error:
        'The issuer returned an error. The record still exists and this ' +
        'is usually temporary.',
    malformed:
        'The record could not be read in the format it was returned in.',
    encrypted:
        'This record is encrypted. Encrypted records are not shown here.',
    unsafe_uri: 'The registered address for this record cannot be opened.',
};

export const failureMessage = reason =>
    FAILURE_MESSAGES[reason] ||
    'The record is temporarily unavailable. The production location below ' +
        'is unaffected.';
