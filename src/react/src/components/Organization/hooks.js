/*
 * Data hooks for the organization level.
 *
 * No Redux plumbing, following the claims dashboard v2: nothing here is
 * global state, so these are plain hooks over the existing apiRequest
 * client and URL builders.
 */

import { useCallback, useEffect, useRef, useState } from 'react';

import apiRequest from '../../util/apiRequest';
import {
    makeCurrentOrganizationURL,
    makeOrganizationMembersURL,
    makeOrganizationMemberURL,
    makeOrganizationInvitationsURL,
    makeOrganizationInvitationURL,
    makeOrganizationContributionsURL,
    makeOrganizationDashboardSummaryURL,
    makeOrganizationDashboardFacilitiesURL,
    makeOrganizationDashboardFacilityURL,
    makeOrganizationDashboardListsURL,
    makeOrganizationDashboardUsageURL,
    makeOrganizationOnboardingURL,
    makeOrganizationDomainAccountsURL,
    makeMyOrganizationInvitationsURL,
    makeAcceptOrganizationInvitationURL,
    makeDeclineOrganizationInvitationURL,
} from '../../util/util';
import {
    buildContributionsQueryString,
    buildDashboardQueryString,
    extractErrorMessage,
} from './utils';

const HTTP_NOT_FOUND = 404;

/*
 * GET a URL and keep its payload. A null url skips the request, which
 * lets callers wait for something the URL depends on. The fetch lives
 * in the effect so it can be cancelled: without the `cancelled` guard a
 * slow response for a previous url would overwrite newer state.
 */
export const useApiGet = (url, { errorMessage, notFoundValue } = {}) => {
    const [data, setData] = useState(null);
    const [fetching, setFetching] = useState(false);
    const [loaded, setLoaded] = useState(false);
    const [error, setError] = useState(null);
    const [fetchCount, setFetchCount] = useState(0);

    // The options describe how to read a response, not what to fetch,
    // so they are kept in a ref: a caller passing a new options object
    // on every render must not trigger a new request.
    const optionsRef = useRef();
    optionsRef.current = { errorMessage, notFoundValue };

    useEffect(() => {
        if (!url) return undefined;

        let cancelled = false;
        setFetching(true);
        setError(null);
        apiRequest
            .get(url)
            .then(response => {
                if (!cancelled) {
                    setData(response.data);
                    setLoaded(true);
                }
            })
            .catch(err => {
                if (cancelled) return;
                const options = optionsRef.current;
                const status = err && err.response && err.response.status;
                if (
                    options.notFoundValue !== undefined &&
                    status === HTTP_NOT_FOUND
                ) {
                    setData(options.notFoundValue);
                    setLoaded(true);
                    return;
                }
                setError(
                    extractErrorMessage(
                        err,
                        options.errorMessage || 'The data could not be loaded.',
                    ),
                );
            })
            .finally(() => {
                if (!cancelled) setFetching(false);
            });

        return () => {
            cancelled = true;
        };
    }, [url, fetchCount]);

    const refetch = useCallback(() => setFetchCount(n => n + 1), []);

    return { data, fetching, loaded, error, refetch };
};

/* The organization the signed-in user belongs to; null when none. */
export const useCurrentOrganization = () => {
    const { data, fetching, loaded, error, refetch } = useApiGet(
        makeCurrentOrganizationURL(),
        {
            notFoundValue: null,
            errorMessage: 'Your organization could not be loaded.',
        },
    );
    return { organization: data, fetching, loaded, error, refetch };
};

export const useMyInvitations = () => {
    const { data, fetching, loaded, error, refetch } = useApiGet(
        makeMyOrganizationInvitationsURL(),
        {
            errorMessage: 'Your invitations could not be loaded.',
        },
    );
    return { invitations: data || [], fetching, loaded, error, refetch };
};

export const useOrganizationMembers = organizationUUID => {
    const {
        data,
        fetching,
        loaded,
        error,
        refetch,
    } = useApiGet(
        organizationUUID ? makeOrganizationMembersURL(organizationUUID) : null,
        { errorMessage: 'The members could not be loaded.' },
    );
    return {
        members: (data && data.members) || [],
        fetching,
        loaded,
        error,
        refetch,
    };
};

export const useOrganizationInvitations = (organizationUUID, enabled) => {
    const {
        data,
        fetching,
        loaded,
        error,
        refetch,
    } = useApiGet(
        organizationUUID && enabled
            ? makeOrganizationInvitationsURL(organizationUUID)
            : null,
        { errorMessage: 'The invitations could not be loaded.' },
    );
    return { invitations: data || [], fetching, loaded, error, refetch };
};

export const useOrganizationContributions = (organizationUUID, type, page) => {
    const { data, fetching, loaded, error } = useApiGet(
        organizationUUID
            ? makeOrganizationContributionsURL(
                  organizationUUID,
                  buildContributionsQueryString(type, page),
              )
            : null,
        { errorMessage: 'The contributions could not be loaded.' },
    );
    return {
        rows: (data && data.results) || [],
        count: (data && data.count) || 0,
        fetching,
        loaded,
        error,
    };
};

export const useDashboardSummary = (organizationUUID, filters) => {
    const { data, fetching, loaded, error } = useApiGet(
        organizationUUID
            ? makeOrganizationDashboardSummaryURL(
                  organizationUUID,
                  buildDashboardQueryString(filters),
              )
            : null,
        { errorMessage: 'The dashboard totals could not be loaded.' },
    );
    return { summary: data, fetching, loaded, error };
};

export const useDashboardFacilities = (organizationUUID, filters, page) => {
    const { data, fetching, loaded, error } = useApiGet(
        organizationUUID
            ? makeOrganizationDashboardFacilitiesURL(
                  organizationUUID,
                  buildDashboardQueryString(filters, page),
              )
            : null,
        { errorMessage: 'The submitted locations could not be loaded.' },
    );
    return {
        rows: (data && data.results) || [],
        count: (data && data.count) || 0,
        fetching,
        loaded,
        error,
    };
};

export const useDashboardFacility = (organizationUUID, osID) => {
    const { data, fetching, error } = useApiGet(
        organizationUUID && osID
            ? makeOrganizationDashboardFacilityURL(organizationUUID, osID)
            : null,
        { errorMessage: 'The production location could not be loaded.' },
    );
    return { facility: data, fetching, error };
};

/* Which first steps the organization has taken; null until loaded. */
export const useOrganizationOnboarding = organizationUUID => {
    const { data, refetch } = useApiGet(
        organizationUUID
            ? makeOrganizationOnboardingURL(organizationUUID)
            : null,
    );
    return { progress: data, refetch };
};

/*
 * Admin only: existing OS Hub accounts on the Admin's email domain that
 * could be invited. A failure is not shown: the list is a suggestion,
 * and inviting by email works without it.
 */
export const useOrganizationDomainAccounts = (organizationUUID, enabled) => {
    const { data, refetch } = useApiGet(
        organizationUUID && enabled
            ? makeOrganizationDomainAccountsURL(organizationUUID)
            : null,
    );
    return {
        domain: (data && data.domain) || null,
        accounts: (data && data.accounts) || [],
        refetch,
    };
};

export const useDashboardListMatchReport = organizationUUID => {
    const { data, fetching, loaded, error } = useApiGet(
        organizationUUID
            ? makeOrganizationDashboardListsURL(organizationUUID)
            : null,
        { errorMessage: 'The list match report could not be loaded.' },
    );
    return { lists: (data && data.lists) || [], fetching, loaded, error };
};

export const useDashboardUsage = organizationUUID => {
    const { data, fetching, loaded, error } = useApiGet(
        organizationUUID
            ? makeOrganizationDashboardUsageURL(organizationUUID)
            : null,
        { errorMessage: 'The usage figures could not be loaded.' },
    );
    return { usage: data, fetching, loaded, error };
};

/*
 * Runs one organization action at a time and keeps its failure message.
 * `run` resolves with the response data, or rejects after recording the
 * error so callers can chain a refetch on success only.
 */
export const useOrganizationAction = () => {
    const [acting, setActing] = useState(false);
    const [actionError, setActionError] = useState(null);

    const run = useCallback(request => {
        setActing(true);
        setActionError(null);
        return request()
            .then(({ data }) => data)
            .catch(err => {
                setActionError(
                    extractErrorMessage(
                        err,
                        'The action could not be completed. Please retry.',
                    ),
                );
                throw err;
            })
            .finally(() => setActing(false));
    }, []);

    const clearActionError = useCallback(() => setActionError(null), []);

    return { run, acting, actionError, clearActionError };
};

export const organizationApi = Object.freeze({
    invite: (organizationUUID, email, role) =>
        apiRequest.post(makeOrganizationInvitationsURL(organizationUUID), {
            email,
            role,
        }),
    revokeInvitation: (organizationUUID, invitationUUID) =>
        apiRequest.delete(
            makeOrganizationInvitationURL(organizationUUID, invitationUUID),
        ),
    changeRole: (organizationUUID, membershipUUID, role) =>
        apiRequest.patch(
            makeOrganizationMemberURL(organizationUUID, membershipUUID),
            { role },
        ),
    removeMember: (organizationUUID, membershipUUID) =>
        apiRequest.delete(
            makeOrganizationMemberURL(organizationUUID, membershipUUID),
        ),
    acceptInvitation: invitationUUID =>
        apiRequest.post(makeAcceptOrganizationInvitationURL(invitationUUID)),
    declineInvitation: invitationUUID =>
        apiRequest.post(makeDeclineOrganizationInvitationURL(invitationUUID)),
});
