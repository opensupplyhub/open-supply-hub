/*
 * Data hooks for claims dashboard v2 (OSDEV-3355).
 *
 * Deliberately no new Redux plumbing (SPEC.md §4): the route needs no
 * new global state, so these are plain hooks over the existing
 * apiRequest client and URL builders.
 */

import { useCallback, useEffect, useState } from 'react';

import apiRequest from '../../util/apiRequest';
import {
    makeGetFacilityClaimsURLWithQueryString,
    makeGetFacilityClaimByClaimIDURL,
    makeMessageFacilityClaimantByClaimIDURL,
    makeApproveFacilityClaimByClaimIDURL,
    makeDenyFacilityClaimByClaimIDURL,
    makeAddNewFacilityClaimReviewNoteURL,
} from '../../util/util';

export const useClaimsList = (statuses = 'PENDING') => {
    const [claims, setClaims] = useState([]);
    const [fetching, setFetching] = useState(false);
    const [error, setError] = useState(null);
    const [fetchCount, setFetchCount] = useState(0);

    /*
     * The fetch lives in the effect so it can be cancelled: without
     * the `cancelled` guard, a slow response for a previous statuses
     * value (or an unmounted component) would overwrite newer state.
     */
    useEffect(() => {
        let cancelled = false;
        setFetching(true);
        setError(null);
        apiRequest
            .get(
                makeGetFacilityClaimsURLWithQueryString(`statuses=${statuses}`),
            )
            .then(({ data }) => {
                if (!cancelled) setClaims(data);
            })
            .catch(() => {
                if (!cancelled) {
                    setError('An error prevented fetching the claims list.');
                }
            })
            .finally(() => {
                if (!cancelled) setFetching(false);
            });
        return () => {
            cancelled = true;
        };
    }, [statuses, fetchCount]);

    const refetchClaims = useCallback(() => setFetchCount(n => n + 1), []);

    return { claims, fetching, error, refetchClaims };
};

export const useClaimDetail = claimID => {
    const [detail, setDetail] = useState(null);
    const [fetching, setFetching] = useState(false);
    const [error, setError] = useState(null);
    const [fetchCount, setFetchCount] = useState(0);

    /*
     * Cancellation matters most here: rapid queue navigation means a
     * slow response for the previously selected claim can arrive after
     * the current claim rendered — without the guard it would replace
     * the workspace with the wrong claim's data.
     */
    useEffect(() => {
        if (!claimID) {
            setDetail(null);
            return undefined;
        }
        let cancelled = false;
        setFetching(true);
        setError(null);
        apiRequest
            .get(makeGetFacilityClaimByClaimIDURL(claimID))
            .then(({ data }) => {
                if (!cancelled) setDetail(data);
            })
            .catch(() => {
                if (!cancelled) {
                    setError('An error prevented fetching the claim details.');
                }
            })
            .finally(() => {
                if (!cancelled) setFetching(false);
            });
        return () => {
            cancelled = true;
        };
    }, [claimID, fetchCount]);

    const refetchDetail = useCallback(() => setFetchCount(n => n + 1), []);

    return { detail, fetching, error, refetchDetail };
};

/*
 * Claim actions. Each resolves with the refreshed claim detail the
 * backend returns, letting callers update state without a second fetch.
 */
export const useClaimActions = claimID => {
    const [acting, setActing] = useState(false);
    const [actionError, setActionError] = useState(null);

    const runAction = useCallback((url, payload) => {
        setActing(true);
        setActionError(null);
        return apiRequest
            .post(url, payload)
            .then(({ data }) => data)
            .catch(err => {
                setActionError(
                    'The action could not be completed. Please retry.',
                );
                throw err;
            })
            .finally(() => setActing(false));
    }, []);

    return {
        acting,
        actionError,
        approveClaim: reason =>
            runAction(makeApproveFacilityClaimByClaimIDURL(claimID), {
                reason,
            }),
        denyClaim: reason =>
            runAction(makeDenyFacilityClaimByClaimIDURL(claimID), { reason }),
        messageClaimant: message =>
            runAction(makeMessageFacilityClaimantByClaimIDURL(claimID), {
                message,
            }),
        addNote: note =>
            runAction(makeAddNewFacilityClaimReviewNoteURL(claimID), {
                note,
            }),
    };
};
