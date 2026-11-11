/**
 * Data hook for the candidate review page (OSDEV-3755).
 *
 * One page of GET /api/v1/production-locations/candidates/ (list mode,
 * OSDEV-3754) for a query object (see util/candidates.js), refetched when
 * the query changes, with the in-flight request cancelled on change. Kept
 * in component state rather than Redux for the same reason as the vote
 * hooks: one page reads it, the server owns the truth, and nothing else
 * in the app needs the list.
 */
import { useCallback, useEffect, useRef, useState } from 'react';
import axios from 'axios';
import get from 'lodash/get';

import apiRequest from '../../util/apiRequest';
import {
    makeCandidatesListURL,
    normalizeCandidateListFeature,
} from '../../util/candidates';

export const LIST_STATUS = Object.freeze({
    LOADING: 'loading',
    READY: 'ready',
    PAGE_PAST_END: 'page_past_end',
    ERROR: 'error',
});

const INITIAL = Object.freeze({
    rows: [],
    count: 0,
    status: LIST_STATUS.LOADING,
});

/**
 * `enabled` false (anonymous or session still unknown) sends no request.
 * That is the page's UX gate, not access control: the pilot switch is
 * the gate, and the API's plain list answers anonymous callers (only its
 * nearby sorts and filters need a login). A list fetched for a logged-out
 * visitor would be one they can neither vote on nor sort by nearby, so
 * the page asks them to log in instead.
 */
export const useCandidateList = (query, { enabled = true } = {}) => {
    const [state, setState] = useState(INITIAL);
    const [refreshKey, setRefreshKey] = useState(0);
    const url = makeCandidatesListURL(query);
    const controllerRef = useRef(null);

    useEffect(() => {
        if (!enabled) return undefined;
        if (controllerRef.current) controllerRef.current.abort();
        const controller = new AbortController();
        controllerRef.current = controller;
        setState(current => ({ ...current, status: LIST_STATUS.LOADING }));
        apiRequest
            .get(url, { signal: controller.signal })
            .then(({ data }) => {
                const rows = (get(data, 'features') || [])
                    .map(normalizeCandidateListFeature)
                    .filter(Boolean);
                setState({
                    rows,
                    count: Number(get(data, 'count', rows.length)) || 0,
                    status: LIST_STATUS.READY,
                });
            })
            .catch(err => {
                if (axios.isCancel(err)) return;
                const status = get(err, 'response.status');
                setState({
                    rows: [],
                    count: 0,
                    status:
                        status === 404
                            ? LIST_STATUS.PAGE_PAST_END
                            : LIST_STATUS.ERROR,
                });
            });
        return () => controller.abort();
    }, [url, enabled, refreshKey]);

    const refetch = useCallback(() => setRefreshKey(key => key + 1), []);

    /**
     * Apply a vote outcome to the row in place (state and tally), so the
     * table reflects the panel without a round trip.
     */
    const updateRowValidation = useCallback((osId, validation) => {
        setState(current => ({
            ...current,
            rows: current.rows.map(row =>
                row.osId === osId
                    ? {
                          ...row,
                          validation: {
                              ...row.validation,
                              state: validation.state,
                              tally: validation.tally,
                          },
                      }
                    : row,
            ),
        }));
    }, []);

    return { ...state, refetch, updateRowValidation };
};

export default useCandidateList;
