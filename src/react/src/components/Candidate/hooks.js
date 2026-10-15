/**
 * Candidate validation hooks (OSDEV-3247).
 *
 * Vote state is kept in component state rather than a Redux slice on
 * purpose: it is scoped to one panel, nothing else in the app reads it, and
 * the backend derives the state so there is no client cache to share. A
 * slice would add redux-act actions, an immutability-helper reducer and a
 * reducers/index.js registration for a value that lives as long as the
 * panel. The ProductionLocation hooks (useDrawerState, useReportStatusDialog)
 * follow the same pattern.
 */
import { useCallback, useEffect, useRef, useState } from 'react';
import axios from 'axios';

import apiRequest from '../../util/apiRequest';
import {
    applyVoteToTally,
    getVoteErrorKind,
    makeCandidateDetailURL,
    makeCandidateVotesURL,
    normalizeCandidateDetail,
    normalizeValidation,
} from '../../util/candidates';

export const VOTE_STATUS = Object.freeze({
    IDLE: 'idle',
    SAVING: 'saving',
    CLOSED: 'closed',
    RETIRED: 'retired',
    ERROR: 'error',
});

/**
 * Ensures the panel has the full candidate detail (your_vote, voting_open,
 * suggested matches). Bbox-layer features only carry the public tally, so
 * the detail endpoint is fetched once per OS ID; detail-page payloads arrive
 * complete and skip the request.
 */
export const useCandidateDetail = seed => {
    const [candidate, setCandidate] = useState(seed);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        setCandidate(seed);
        if (!seed || seed.isDetailLoaded) {
            setLoading(false);
            return undefined;
        }
        const controller = new AbortController();
        setLoading(true);
        apiRequest
            .get(makeCandidateDetailURL(seed.osId), {
                signal: controller.signal,
            })
            .then(({ data }) => {
                const detail = normalizeCandidateDetail(data);
                if (detail) {
                    setCandidate(current => ({
                        ...(current || seed),
                        ...detail,
                    }));
                }
                setLoading(false);
            })
            .catch(err => {
                if (axios.isCancel(err)) return;
                // Leave the seed in place; the vote endpoints still work.
                setLoading(false);
            });
        return () => controller.abort();
    }, [seed]);

    return [candidate, loading];
};

/**
 * Casting and changing a vote on one candidate.
 *
 * Optimistic update: the tally and your_vote move immediately, then are
 * replaced by the server body. 409 closes voting (confirmed) and refetches
 * the detail so the state chip and tally reflect the server, 410 marks the
 * candidate retired, 401/403 opens the login prompt, anything else reverts
 * and shows a retry message. Anonymous users never send a request; while
 * the session is still unknown (`isAnon` undefined) a click is a no-op.
 */
export const useCandidateVote = ({
    osId,
    initialValidation,
    isAnon,
    onValidationChange,
}) => {
    const [validation, setValidation] = useState(() =>
        normalizeValidation(initialValidation),
    );
    const [status, setStatus] = useState(VOTE_STATUS.IDLE);
    const [loginPromptOpen, setLoginPromptOpen] = useState(false);
    const latestValidation = useRef(validation);
    latestValidation.current = validation;

    useEffect(() => {
        const next = normalizeValidation(initialValidation);
        setValidation(next);
        setStatus(VOTE_STATUS.IDLE);
    }, [osId, initialValidation]);

    const commit = useCallback(
        next => {
            setValidation(next);
            if (onValidationChange) onValidationChange(next);
        },
        [onValidationChange],
    );

    /**
     * A 409 body carries no state, so the closed validation is read back
     * from the v1 detail. If that read fails, the last known block is kept
     * with voting marked closed.
     */
    const closeVoting = useCallback(
        fallback => {
            const closed = normalizeValidation({
                ...fallback,
                your_vote: fallback.yourVote,
                voting_open: false,
            });
            return apiRequest
                .get(makeCandidateDetailURL(osId))
                .then(({ data }) =>
                    normalizeValidation({
                        ...closed,
                        your_vote: closed.yourVote,
                        voting_open: false,
                        ...((data && data.validation) || {}),
                    }),
                )
                .catch(() => closed)
                .then(next => {
                    commit(next);
                    setStatus(VOTE_STATUS.CLOSED);
                    return null;
                });
        },
        [commit, osId],
    );

    const castVote = useCallback(
        vote => {
            if (typeof isAnon !== 'boolean') {
                return Promise.resolve(null);
            }
            if (isAnon) {
                setLoginPromptOpen(true);
                return Promise.resolve(null);
            }
            const { current } = latestValidation;
            if (
                !current.votingOpen ||
                status === VOTE_STATUS.SAVING ||
                status === VOTE_STATUS.RETIRED
            ) {
                return Promise.resolve(null);
            }
            const previous = current;
            const previousVote = current.yourVote || null;
            if (previousVote === vote) {
                return Promise.resolve(null);
            }
            setStatus(VOTE_STATUS.SAVING);
            setValidation({
                ...current,
                yourVote: vote,
                tally: applyVoteToTally(current.tally, previousVote, vote),
            });
            return apiRequest
                .post(makeCandidateVotesURL(osId), { vote })
                .then(({ data }) => {
                    const reconciled = normalizeValidation({
                        state: data.state,
                        tally: data.tally,
                        your_vote: data.your_vote,
                    });
                    commit(reconciled);
                    setStatus(VOTE_STATUS.IDLE);
                    return reconciled;
                })
                .catch(err => {
                    const kind = getVoteErrorKind(err);
                    if (kind === 'closed') {
                        return closeVoting(previous);
                    }
                    if (kind === 'retired') {
                        commit({ ...previous, votingOpen: false });
                        setStatus(VOTE_STATUS.RETIRED);
                    } else if (kind === 'unauthenticated') {
                        setValidation(previous);
                        setStatus(VOTE_STATUS.IDLE);
                        setLoginPromptOpen(true);
                    } else {
                        setValidation(previous);
                        setStatus(VOTE_STATUS.ERROR);
                    }
                    return null;
                });
        },
        [closeVoting, commit, isAnon, osId, status],
    );

    const closeLoginPrompt = useCallback(() => setLoginPromptOpen(false), []);

    return {
        validation,
        status,
        castVote,
        loginPromptOpen,
        closeLoginPrompt,
    };
};
