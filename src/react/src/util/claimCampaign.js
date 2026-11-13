import apiRequest from './apiRequest';

// Claims campaigns: a brand sends each supplier a claim link carrying
// ?campaign=<code>. The claim form sends the code back with the claim so
// the claim counts as coming from the campaign link.

// Same rules as ClaimCampaign.code on the backend: upper-case letters,
// digits and hyphens, starting with a letter or digit, at most 50 long.
// Codes are stored upper-case, so a link typed in lower case still works.
const CAMPAIGN_CODE_PATTERN = /^[A-Z0-9][A-Z0-9-]*$/;
const CAMPAIGN_CODE_MAX_LENGTH = 50;

export const normalizeCampaignCode = value => {
    const code = (value || '').trim().toUpperCase();
    if (
        !code ||
        code.length > CAMPAIGN_CODE_MAX_LENGTH ||
        !CAMPAIGN_CODE_PATTERN.test(code)
    ) {
        return null;
    }
    return code;
};

// Kept like claim invite codes (see claimInvite.js): in localStorage, per
// OS ID, for a week. A supplier who has to log in or register after
// opening the link comes back without the query string, and the claim
// form's Back button reopens the intro without it too; the code must
// survive both. Storage can be unavailable (private windows, blocked
// site data), so every access fails quietly: attribution is best effort,
// and the backend can still attribute the claim from the brand's roster.
const storageKey = osID => `claim-campaign-${osID}`;
const CODE_LIFETIME_MS = 7 * 24 * 60 * 60 * 1000;

export const rememberClaimCampaignCode = (osID, code) => {
    try {
        if (osID && code) {
            localStorage.setItem(
                storageKey(osID),
                JSON.stringify({ code, savedAt: Date.now() }),
            );
        }
    } catch (e) {
        // Attribution is best effort.
    }
};

export const forgetClaimCampaignCode = osID => {
    try {
        localStorage.removeItem(storageKey(osID));
    } catch (e) {
        // Nothing to clean up.
    }
};

export const getClaimCampaignCode = osID => {
    try {
        const { code, savedAt } = JSON.parse(
            localStorage.getItem(storageKey(osID)),
        );
        if (Date.now() - savedAt > CODE_LIFETIME_MS) {
            forgetClaimCampaignCode(osID);
            return null;
        }
        return normalizeCampaignCode(code);
    } catch (e) {
        return null;
    }
};

export const makeClaimCampaignLookupURL = code =>
    `/api/claim-campaigns/lookup/?code=${encodeURIComponent(code)}`;

// Resolves to true or false when the backend says whether the code
// belongs to an active campaign, and to null when it couldn't be asked
// (network error, switch off, not logged in). Callers show the campaign
// banner only on true, and forget the code only on false.
export const isActiveClaimCampaign = code =>
    apiRequest
        .get(makeClaimCampaignLookupURL(code))
        .then(({ data }) => !!(data && data.active))
        .catch(() => null);
