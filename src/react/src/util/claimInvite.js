import apiRequest from './apiRequest';
import { makeClaimInviteURL } from './util';

// Claim invites: a registered user emails someone at an unclaimed
// production location a link to claim it. The link carries
// ?invite=<code>, which the claim form sends back with the claim so the
// claim can be traced to the invite.

export const CLAIM_INVITE_NOTE_MAX_LENGTH = 500;

const storageKey = osID => `claim-invite-${osID}`;

// Kept in localStorage, not sessionStorage: an invitee who registers
// confirms their email from a link that opens a new tab, and the code
// should still be there when they come back to claim. Storage can be
// unavailable (private windows, blocked site data); the claim must work
// regardless, so every access fails quietly.
export const rememberClaimInviteCode = (osID, search) => {
    try {
        const code = new URLSearchParams(search).get('invite');
        if (osID && code) {
            localStorage.setItem(storageKey(osID), code);
        }
    } catch (e) {
        // Attribution is best effort.
    }
};

export const getClaimInviteCode = osID => {
    try {
        return localStorage.getItem(storageKey(osID));
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
