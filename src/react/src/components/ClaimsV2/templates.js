/*
 * Message-claimant templates for claims dashboard v2 (OSDEV-3355).
 *
 * Shipped as frontend constants initially (SPEC.md §4); move to a
 * config endpoint if the moderation team wants to edit wording without
 * deploys. Each builder takes the claim context and returns the full
 * message body; composeMessage combines selected templates and dedupes
 * the shared sensitive-information notice so it appears exactly once.
 */

export const SENSITIVE_INFO_NOTICE =
    'Important: We do NOT require and you should NOT submit documents ' +
    'containing sensitive personal information such as salary ' +
    'information, personal phone numbers, home addresses, or personal ' +
    'ID numbers.';

export const MESSAGE_TEMPLATES = Object.freeze({
    location: {
        label: 'Location verification',
        build: ({ facilityName }) =>
            [
                'In order to complete your claim, we need to verify the ',
                'specific name and address for each production location ',
                'you wish to claim.\n\n',
                'Please share a document or website that lists the name ',
                `and address of ${facilityName} (e.g. utility bill, `,
                'business website, registration document, or LinkedIn ',
                'profile). A scan or screenshot would be just fine.\n\n',
                SENSITIVE_INFO_NOTICE,
            ].join(''),
    },
    person: {
        label: 'Person verification',
        build: ({ facilityName, jobTitle }) =>
            [
                'As per our claim policy ',
                '(https://info.opensupplyhub.org/resources/claim-a-facility), ',
                'the claim needs to be submitted by a senior manager or ',
                'owner.\n\n',
                `You listed yourself as a "${jobTitle}". At this point, `,
                "we'll need to verify your title and affiliation with the ",
                'company. Please provide a document or website that shows ',
                `your role at ${facilityName} (e.g. business website, `,
                'employment badge, letter of employment, or other relevant ',
                'employment documentation).\n\n',
                SENSITIVE_INFO_NOTICE,
            ].join(''),
    },
    relationship: {
        label: 'Relationship verification',
        build: ({ facilityName, emailDomain }) =>
            [
                'Your company email extension and the production location ',
                "for which you submitted a claim request don't match. To ",
                'proceed with your claim, we need documentation or a link ',
                'confirming the relationship (like ownership or parent ',
                `company) between ${emailDomain} and ${facilityName}.\n\n`,
                'Please note that the claim request will only be approved ',
                'when it is submitted by an owner or senior management ',
                'associated with the production location in question.\n\n',
                SENSITIVE_INFO_NOTICE,
            ].join(''),
    },
    addressUpdate: {
        label: 'Address update (SLC)',
        build: ({ facilityAddress, osID }) =>
            [
                'The address listed on Open Supply Hub needs to be updated ',
                'before we can proceed with approving your claim.\n\n',
                'Click on this link and update the address in the form, ',
                "then click 'Submit': ",
                `https://opensupplyhub.org/contribute/single-location/${osID}/info/\n\n`,
                'The address should match the information listed on your ',
                'document:\n\n',
                `${facilityAddress}\n\n`,
                'Please let us know once you have submitted the updated ',
                'address so we can prioritize your request.',
            ].join(''),
    },
});

/*
 * Combine the selected templates into one message, keeping the
 * sensitive-information notice exactly once at the end (it is stripped
 * from each template that carries it, then re-appended).
 */
export const composeMessage = (templateKeys, context) => {
    const ordered = Object.keys(MESSAGE_TEMPLATES).filter(key =>
        templateKeys.includes(key),
    );
    let hasNotice = false;
    const parts = ordered.map(key => {
        let text = MESSAGE_TEMPLATES[key].build(context);
        if (text.includes(SENSITIVE_INFO_NOTICE)) {
            hasNotice = true;
            text = text.replace(SENSITIVE_INFO_NOTICE, '').trim();
        }
        return text;
    });
    if (hasNotice && parts.length > 0) {
        parts.push(SENSITIVE_INFO_NOTICE);
    }
    return parts.join('\n\n');
};
