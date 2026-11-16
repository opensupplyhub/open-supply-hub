/*
Profile completeness prototype, shown only to users the
show_profile_completeness flag is on for. The indicator describes how
complete, recent and widely contributed-to a profile is. It does not check
whether the data is correct, so no copy here may call a profile verified,
trusted or accurate.
*/
export const PROFILE_COMPLETENESS_LABEL = 'Profile completeness';
export const PROFILE_COMPLETENESS_SECTION_ID = 'profile-completeness';
export const CALCULATION_SECTION_TITLE =
    'How profile completeness is calculated';
export const STRENGTHEN_SECTION_TITLE = 'How to strengthen this profile';
export const STRENGTHEN_SECTION_INTRO =
    'Next steps based on what this profile is missing. Not all of them are for the facility itself to act on.';
export const ADMIN_PREVIEW_LABEL = 'Admin preview';

export const MAX_STRENGTHEN_STEPS = 3;

/*
PLACEHOLDER rules mapping scorer components to a suggested next step, in
priority order. `applies` receives the component values keyed by the
scorer's component names. The 0.5 thresholds are provisional.
*/
export const STRENGTHEN_STEPS = Object.freeze([
    Object.freeze({
        key: 'claim',
        applies: c => c.claimed_status === 0,
        text: 'Claim this profile',
        detail:
            'Confirm you manage this location and add details only management can supply.',
    }),
    Object.freeze({
        key: 'fields',
        applies: c => c.completeness_score < 1,
        text: 'Add core profile fields',
        detail: 'Some core profile fields are not on file yet.',
    }),
    Object.freeze({
        key: 'claimed-detail',
        applies: c => c.claimed_status === 1 && c.claimed_only_score < 0.5,
        text: 'Add more detail to the claimed profile',
        detail:
            'Several of the fields only the claimant can supply are still empty.',
    }),
    Object.freeze({
        key: 'contributors',
        applies: c => c.contribution_count_score < 0.5,
        text: 'Ask the brands you supply to confirm this listing',
        detail: 'Another independent source strengthens what is already here.',
    }),
    Object.freeze({
        key: 'contributor-mix',
        applies: c => c.contribution_mix_score < 0.5,
        text:
            'Ask civil society or worker organizations to confirm relationships here',
        detail: 'Few types of contributor have added to this profile so far.',
    }),
    Object.freeze({
        key: 'recency',
        applies: c => c.recency_score < 0.5,
        text: 'Keep information current',
        detail: 'It has been a while since anything on this profile changed.',
    }),
    Object.freeze({
        key: 'assessments',
        applies: c => c.assessments_audits_score === 0,
        text: 'Link assessment or audit records, if any apply',
        detail:
            'No assessments or audits are currently linked to this location.',
    }),
    Object.freeze({
        key: 'certifications',
        applies: c => c.certifications_score === 0,
        text: 'Add certification records, if any apply',
        detail: 'No certifications are currently linked to this location.',
    }),
]);

export const CLASSIFIER_TITLE = 'Model classification';
export const CLASSIFIER_NOTE =
    'Shown next to the score for comparison. It is produced separately from the score and does not feed into it.';
export const CLASSIFIER_TIER_LABELS = Object.freeze({
    low: 'Low',
    medium: 'Middle',
    high: 'High',
    best: 'Best',
});

/*
The classification's two checks. Corroboration is how many contributors
there are and how far they agree. The second check only looks at whether
entries are placeholders or junk ("Site 2", "#N/A", a city for an address),
never at whether they are correct, and a missing field does not count.
*/
export const CORROBORATION_LABEL = 'Corroboration';
export const PLACEHOLDER_DATA_LABEL = 'Placeholder data';
export const PLACEHOLDER_DATA_VALUES = Object.freeze({
    high: 'Little or none',
    medium: 'In some fields',
    low: 'In name or address',
});
