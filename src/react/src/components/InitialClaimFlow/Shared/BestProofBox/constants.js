// Wording for the "best proof" box at each proof question on the claim form.
// Two levels only: what is approved fastest, and what can delay approval.

export const EMAIL_BEST_PROOF = Object.freeze({
    title: 'Use your work email.',
    details: Object.freeze(['Example: name@yourcompany.com']),
    delays: Object.freeze([
        'A personal email may not be accepted and can significantly delay approval.',
        'No work email? Upload a document with your name and your company.',
    ]),
});

export const COMPANY_ADDRESS_BEST_PROOF = Object.freeze({
    title: 'Best: an official document.',
    details: Object.freeze([
        'Utility bill. Business registration. Tax document. Business license.',
    ]),
    delays: Object.freeze([
        'A company website link can delay approval.',
        'A LinkedIn page may not be accepted and can significantly delay approval.',
    ]),
});

export const EMPLOYMENT_BEST_PROOF = Object.freeze({
    title: 'Best: a document with your name and your company.',
    details: Object.freeze(['Business card. Employment letter. ID badge.']),
    delays: Object.freeze([
        'A LinkedIn link may not be accepted and can significantly delay approval.',
    ]),
});
