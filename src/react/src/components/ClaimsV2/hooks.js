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

    const fetchClaims = useCallback(() => {
        setFetching(true);
        setError(null);
        apiRequest
            .get(
                makeGetFacilityClaimsURLWithQueryString(
                    `statuses=${statuses}`,
                ),
            )
            .then(({ data }) => setClaims(data))
            .catch(() =>
                setError('An error prevented fetching the claims list.'),
            )
            .finally(() => setFetching(false));
    }, [statuses]);

    useEffect(fetchClaims, [fetchClaims]);

    return { claims, fetching, error, refetchClaims: fetchClaims };
};

export const useClaimDetail = claimID => {
    const [detail, setDetail] = useState(null);
    const [fetching, setFetching] = useState(false);
    const [error, setError] = useState(null);

    const fetchDetail = useCallback(() => {
        if (!claimID) {
            setDetail(null);
            return;
        }
        setFetching(true);
        setError(null);
        apiRequest
            .get(makeGetFacilityClaimByClaimIDURL(claimID))
            .then(({ data }) => setDetail(data))
            .catch(() =>
                setError('An error prevented fetching the claim details.'),
            )
            .finally(() => setFetching(false));
    }, [claimID]);

    useEffect(fetchDetail, [fetchDetail]);

    return { detail, fetching, error, refetchDetail: fetchDetail };
};

/*
 * Claim actions. Each resolves with the refreshed claim detail the
 * backend returns, letting callers update state without a second fetch.
 */
export const useClaimActions = claimID => {
    const [acting, setActing] = useState(false);
    const [actionError, setActionError] = useState(null);

    const runAction = useCallback(
        (url, payload) => {
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
        },
        [],
    );

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
