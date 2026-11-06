import React, { useCallback, useEffect, useState } from 'react';
import { bool, func, number, object, shape } from 'prop-types';
import { connect } from 'react-redux';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';

import {
    fetchFacilityListCleaning,
    resetFacilityListCleaning,
} from '../actions/facilityListCleaning';
import ListCleaningReviewDialog from './ListCleaningReviewDialog';
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
        borderLeft: `4px solid ${COLOURS.NAVY_BLUE}`,
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
    useEffect(() => {
        fetchCleaning();
        return () => clearCleaning();
    }, [fetchCleaning, clearCleaning]);
    const backFromReview = useCallback(() => {
        setReviewing(false);
        fetchCleaning();
        if (onSubmitted) onSubmitted();
    }, [fetchCleaning, onSubmitted]);

    // A ticking refetch while the window is open, so the line flips to
    // "closed" on its own when the hour runs out.
    const open = !!(data && data.window_open);
    useEffect(() => {
        if (!open || reviewing) return undefined;
        const ms = Math.min(60000, (data.seconds_left + 1) * 1000);
        const timer = setTimeout(fetchCleaning, ms);
        return () => clearTimeout(timer);
    }, [open, reviewing, data, fetchCleaning]);

    const run = data && data.run;
    if (!run || run.status !== 'COMPLETE') return null;

    let text;
    if (open) {
        if (isListOwner) {
            text = `You can still review and submit changes to this list until ${when(
                run.review_until,
            )}. After that it goes to a moderator as uploaded.`;
        } else {
            text = `The contributor can still submit changes until ${when(
                run.review_until,
            )}.${
                isAdminUser
                    ? ' Approve and reject are unavailable until then.'
                    : ''
            }`;
        }
    } else if (run.closed_reason === 'submitted') {
        const applied = (data.summary && data.summary.changes_applied) || 0;
        text = `Submitted ${when(run.submitted_at)} ${
            applied
                ? `with ${applied} ${
                      applied === 1 ? 'change' : 'changes'
                  } from the automated checks`
                : 'as uploaded'
        }. No further changes are possible; a moderator will review it.`;
    } else {
        text = `The review window closed ${when(
            run.closed_at,
        )} without a submission, so the list went through as uploaded.`;
    }

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
