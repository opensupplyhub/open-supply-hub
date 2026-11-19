// Tags shown beside the choices in the claim form's verification
// dropdowns. A tag is display only: it is never part of the option's
// `label`, which is the text saved on the claim.
export const VERIFICATION_OPTION_TAGS = Object.freeze({
    PREFERRED: 'preferred',
    CAN_DELAY: 'can-delay',
});

export const VERIFICATION_OPTION_TAG_TEXT = Object.freeze({
    [VERIFICATION_OPTION_TAGS.PREFERRED]: 'Preferred',
    [VERIFICATION_OPTION_TAGS.CAN_DELAY]: 'Can delay review',
});
