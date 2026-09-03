/*
 * Deep links into the Claims Tracker Jira board, where claim assignment
 * and SLA tracking live (see OSDEV-3261 for the design decision).
 *
 * The frontend never knows Jira ticket keys — there is no sync-back in
 * v1 — so links are JQL searches on the board's Claim ID custom field,
 * which land on the claim's ticket without any backend support.
 */

export const CLAIMS_TRACKER_JIRA_BASE = 'https://opensupplyhub.atlassian.net';

export const CLAIMS_TRACKER_PROJECT_KEY = 'CT';

export const makeClaimTrackerBoardURL = () =>
    `${CLAIMS_TRACKER_JIRA_BASE}/jira/core/projects/` +
    `${CLAIMS_TRACKER_PROJECT_KEY}/board`;

export const makeClaimTrackerTicketSearchURL = claimID => {
    const id = parseInt(claimID, 10);
    if (!Number.isFinite(id)) {
        return makeClaimTrackerBoardURL();
    }
    const jql = `project = ${CLAIMS_TRACKER_PROJECT_KEY} AND "Claim ID[Short text]" ~ "${id}"`;
    return `${CLAIMS_TRACKER_JIRA_BASE}/issues/?jql=${encodeURIComponent(
        jql,
    )}`;
};
