import apiRequest from './apiRequest';
import { makeClaimInviteURL } from './util';

// Claim invites: a registered user emails someone at an unclaimed
// production location a link to claim it. The link carries
// ?invite=<code>, which the claim form sends back with the claim so the
// claim can be traced to the invite.

export const CLAIM_INVITE_NOTE_MAX_LENGTH = 500;

const storageKey = osID => `claim-invite-${osID}`;

// A code left behind on a shared computer must not be attached to
// someone else's claim of the same location later, so it lapses after
// a week; opening the invite link again stores it afresh.
const CODE_LIFETIME_MS = 7 * 24 * 60 * 60 * 1000;

// Kept in localStorage, not sessionStorage: an invitee who registers
// confirms their email from a link that opens a new tab, and the code
// should still be there when they come back to claim. Storage can be
// unavailable (private windows, blocked site data); the claim must work
// regardless, so every access fails quietly.
export const rememberClaimInviteCode = (osID, search) => {
    try {
        const code = new URLSearchParams(search).get('invite');
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

export const getClaimInviteCode = osID => {
    try {
        const { code, savedAt } = JSON.parse(
            localStorage.getItem(storageKey(osID)),
        );
        if (Date.now() - savedAt > CODE_LIFETIME_MS) {
            localStorage.removeItem(storageKey(osID));
            return null;
        }
        return code || null;
    } catch (e) {
        return null;
    }
};

export const forgetClaimInviteCode = osID => {
    try {
        localStorage.removeItem(storageKey(osID));
    } catch (e) {
        // Nothing to clean up.
    }
};

// The backend answers a rejected invite with DRF's error shapes: a list
// of messages, {field: [messages]} or {detail: message}.
const firstErrorMessage = data => {
    if (!data) return null;
    if (typeof data === 'string') return data;
    if (Array.isArray(data)) return firstErrorMessage(data[0]);
    if (data.detail) return data.detail;
    const [firstValue] = Object.values(data);
    return firstErrorMessage(firstValue);
};

export const sendClaimInvite = (osID, { recipientEmail, note }) =>
    apiRequest
        .post(makeClaimInviteURL(osID), {
            recipient_email: recipientEmail,
            note,
        })
        .catch(err => {
            const message =
                firstErrorMessage(err?.response?.data) ||
                'The invite could not be sent. Please try again later.';
            throw new Error(message);
        });
