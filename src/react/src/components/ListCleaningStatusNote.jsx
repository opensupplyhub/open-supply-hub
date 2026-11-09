import React, { useCallback, useEffect, useRef, useState } from 'react';
import { bool, func, number, object, shape } from 'prop-types';
import { connect } from 'react-redux';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';

import {
    fetchFacilityListCleaning,
    resetFacilityListCleaning,
} from '../actions/facilityListCleaning';
import ListCleaningReviewDialog from './ListCleaningReviewDialog';
import { plural } from './FacilityListCleaningSuggestions';
import COLOURS from '../util/COLOURS';

/*
 * v3 of the list-cleaning feedback (OSDEV-3726): the list page no longer
 * carries the review itself. It carries one line about where the
 * contributor's single submission stands, and, while the window is still
 * open, a way for the owner to get back to the review screen.
 */
const styles = Object.freeze({
    box: Object.freeze({
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        gap: '12px',
        padding: '12px 16px',
        margin: '0 0.5rem 20px 0.5rem',
        borderLeftWidth: '4px',
        borderLeftStyle: 'solid',
        borderLeftColor: COLOURS.NAVY_BLUE,
        background: '#F0F4FF',
    }),
    closed: Object.freeze({
        borderLeftColor: COLOURS.DARK_GREY,
        background: COLOURS.LIGHT_GREY,
    }),
    text: Object.freeze({ flex: '1 1 320px' }),
});

const when = iso =>
    new Date(iso).toLocaleString(undefined, {
        hour: 'numeric',
        minute: '2-digit',
        day: 'numeric',
        month: 'short',
    });

const openText = (run, isListOwner, isAdminUser) => {
    if (isListOwner) {
        return `You can still review and submit changes to this list until ${when(
            run.review_until,
        )}. After that it goes to a human moderator as uploaded.`;
    }
    const forAdmin = isAdminUser
        ? ' Approve and reject are unavailable until then.'
        : '';
    return `The contributor can still submit changes until ${when(
        run.review_until,
    )}.${forAdmin}`;
};

const submittedText = (run, data) => {
    const applied = data.summary?.changes_applied || 0;
    const how = applied
        ? `with ${plural(applied, 'change')} from the automated checks`
        : 'as uploaded';
    return `Submitted ${when(
        run.submitted_at,
    )} ${how}. No further changes are possible; a human moderator will review it.`;
};

const statusText = (run, data, { open, isListOwner, isAdminUser }) => {
    if (open) return openText(run, isListOwner, isAdminUser);
    if (run.closed_reason === 'clean') {
        return (
            'The automated checks found nothing to fix, so the list went ' +
            'straight to a human moderator as uploaded.'
        );
    }
    if (run.closed_reason === 'submitted') return submittedText(run, data);
    return `The review window closed ${when(
        run.closed_at,
    )} without a submission, so the list went through as uploaded.`;
};

const ListCleaningStatusNote = ({
    listID,
    isListOwner,
    isAdminUser,
    data,
    fetchCleaning,
    clearCleaning,
    onSubmitted,
}) => {
    const [reviewing, setReviewing] = useState(false);
    // The parent passes a new onSubmitted on every render, which makes
    // react-redux rebuild the dispatchers; keep the latest in refs so the
    // fetch-on-mount and clear-on-unmount happen once per list, not once
    // per render (a mid-submission clear would wipe the dialog's state).
    const fetchRef = useRef(fetchCleaning);
    fetchRef.current = fetchCleaning;
    const clearRef = useRef(clearCleaning);
    clearRef.current = clearCleaning;
    const submittedRef = useRef(onSubmitted);
    submittedRef.current = onSubmitted;
    useEffect(() => {
        fetchRef.current();
        return () => clearRef.current();
    }, [listID]);
    const backFromReview = useCallback(() => {
        setReviewing(false);
        fetchRef.current();
        if (submittedRef.current) submittedRef.current();
    }, []);

    // A ticking refetch while the window is open, so the line flips to
    // "closed" on its own when the hour runs out.
    const open = !!data?.window_open;
    useEffect(() => {
        if (!open || reviewing) return undefined;
        const ms = Math.min(60000, (data.seconds_left + 1) * 1000);
        const timer = setTimeout(() => fetchRef.current(), ms);
        return () => clearTimeout(timer);
    }, [open, reviewing, data]);

    const run = data?.run;
    if (run?.status !== 'COMPLETE') return null;
    const text = statusText(run, data, { open, isListOwner, isAdminUser });

    return (
        <>
            <div style={{ ...styles.box, ...(open ? {} : styles.closed) }}>
                <Typography style={styles.text}>{text}</Typography>
                {open && isListOwner && (
                    <Button
                        variant="contained"
                        color="primary"
                        size="small"
                        onClick={() => setReviewing(true)}
                    >
                        Resume review
                    </Button>
                )}
            </div>
            {reviewing && (
                <ListCleaningReviewDialog
                    listID={listID}
                    open
                    resumed
                    onContinue={backFromReview}
                />
            )}
        </>
    );
};

ListCleaningStatusNote.defaultProps = {
    data: null,
    onSubmitted: null,
};

ListCleaningStatusNote.propTypes = {
    listID: number.isRequired,
    isListOwner: bool.isRequired,
    isAdminUser: bool.isRequired,
    data: shape({ run: object, window_open: bool }),
    fetchCleaning: func.isRequired,
    clearCleaning: func.isRequired,
    onSubmitted: func,
};

const mapStateToProps = ({ facilityListCleaning: { data } }) => ({ data });

const mapDispatchToProps = (dispatch, { listID }) => ({
    fetchCleaning: () =>
        dispatch(fetchFacilityListCleaning(listID, { silent: true })),
    clearCleaning: () => dispatch(resetFacilityListCleaning()),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(ListCleaningStatusNote);
