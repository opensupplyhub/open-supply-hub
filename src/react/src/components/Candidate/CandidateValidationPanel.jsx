import React, { useCallback } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import Paper from '@material-ui/core/Paper';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import IconButton from '@material-ui/core/IconButton';
import CircularProgress from '@material-ui/core/CircularProgress';
import CloseIcon from '@material-ui/icons/Close';
import CheckCircleOutline from '@material-ui/icons/CheckCircleOutline';
import HighlightOff from '@material-ui/icons/HighlightOff';
import EditIcon from '@material-ui/icons/Edit';
import { withStyles } from '@material-ui/core/styles';

import CandidateBadge, { CandidateStateChip } from './CandidateBadge';
import CandidateLoginDialog from './CandidateLoginDialog';
import { useCandidateDetail, useCandidateVote, VOTE_STATUS } from './hooks';
import {
    CANDIDATE_COPY,
    CANDIDATE_STATES,
    CANDIDATE_STATE_DESCRIPTIONS,
    CANDIDATE_VOTES,
    formatCandidateTally,
} from '../../util/candidateCopy';
import {
    formatConfidence,
    formatDistance,
    totalVotes,
} from '../../util/candidates';
import {
    makeContributeProductionLocationUpdateURL,
    makeFacilityDetailLink,
} from '../../util/util';
import { candidateValidationPanelStyles } from './styles';

export const PANEL_VARIANTS = Object.freeze({
    OVERLAY: 'overlay',
    INLINE: 'inline',
});

const VoteButton = ({
    classes,
    vote,
    label,
    Icon,
    selected,
    disabled,
    onClick,
    testId,
}) => (
    <Button
        type="button"
        fullWidth
        disabled={disabled}
        onClick={() => onClick(vote)}
        aria-pressed={selected}
        className={`${classes.voteButton} ${
            selected ? classes.voteButtonSelected : ''
        }`}
        classes={{ disabled: classes.voteButtonDisabled }}
        data-testid={testId}
        data-selected={selected ? 'true' : 'false'}
    >
        <Icon className={classes.voteButtonIcon} />
        {label}
        {selected && (
            <span className={classes.yourVoteTag}>
                {CANDIDATE_COPY.yourVote}
            </span>
        )}
    </Button>
);

VoteButton.propTypes = {
    classes: PropTypes.object.isRequired,
    vote: PropTypes.string.isRequired,
    label: PropTypes.string.isRequired,
    Icon: PropTypes.oneOfType([PropTypes.func, PropTypes.object]).isRequired,
    selected: PropTypes.bool.isRequired,
    disabled: PropTypes.bool.isRequired,
    onClick: PropTypes.func.isRequired,
    testId: PropTypes.string.isRequired,
};

const StatusLine = ({ classes, status, votingOpen, state }) => {
    if (status === VOTE_STATUS.RETIRED) {
        return (
            <Typography
                className={`${classes.statusText} ${classes.statusRetired}`}
                data-testid="candidate-vote-status"
            >
                {CANDIDATE_COPY.retired}. {CANDIDATE_COPY.retiredDetail}
            </Typography>
        );
    }
    if (status === VOTE_STATUS.ERROR) {
        return (
            <Typography
                className={`${classes.statusText} ${classes.statusError}`}
                data-testid="candidate-vote-status"
            >
                {CANDIDATE_COPY.saveError}
            </Typography>
        );
    }
    if (!votingOpen || state === CANDIDATE_STATES.CONFIRMED) {
        return (
            <Typography
                className={`${classes.statusText} ${classes.statusClosed}`}
                data-testid="candidate-vote-status"
            >
                {CANDIDATE_COPY.votingClosed}.{' '}
                {CANDIDATE_COPY.votingClosedDetail}
            </Typography>
        );
    }
    return (
        <Typography
            className={classes.statusText}
            data-testid="candidate-vote-status"
        >
            {CANDIDATE_COPY.changeVoteHint}
        </Typography>
    );
};

StatusLine.propTypes = {
    classes: PropTypes.object.isRequired,
    status: PropTypes.string.isRequired,
    votingOpen: PropTypes.bool.isRequired,
    state: PropTypes.string.isRequired,
};

const SuggestedMatches = ({ classes, matches }) => (
    <div className={classes.section}>
        <Typography className={classes.matchesTitle} component="h4">
            {CANDIDATE_COPY.nearbyMatchesTitle}
        </Typography>
        {matches.length === 0 ? (
            <Typography className={classes.matchMeta}>
                {CANDIDATE_COPY.nearbyMatchesEmpty}
            </Typography>
        ) : (
            <ul className={classes.matchesList} data-testid="candidate-matches">
                {matches.map(match => (
                    <li key={match.osId} className={classes.matchItem}>
                        <Link
                            to={makeFacilityDetailLink(match.osId)}
                            className={classes.matchName}
                            data-testid="candidate-match-link"
                        >
                            {match.name || match.osId}
                        </Link>
                        <Typography className={classes.matchMeta}>
                            {[match.address, formatDistance(match.distanceM)]
                                .filter(Boolean)
                                .join(' · ')}
                        </Typography>
                    </li>
                ))}
            </ul>
        )}
    </div>
);

SuggestedMatches.propTypes = {
    classes: PropTypes.object.isRequired,
    matches: PropTypes.arrayOf(
        PropTypes.shape({
            osId: PropTypes.string.isRequired,
            name: PropTypes.string,
            address: PropTypes.string,
            distanceM: PropTypes.number,
        }),
    ).isRequired,
};

/**
 * Validation panel for a satellite-detected candidate (OSDEV-3247).
 *
 * `candidate` is the normalized shape from util/candidates.js. A seed from
 * the map layer (isDetailLoaded: false) triggers one detail fetch for
 * your_vote / voting_open / suggested matches; detail-page payloads arrive
 * complete.
 */
const CandidateValidationPanel = ({
    classes,
    candidate: seed,
    variant,
    onClose,
    onValidationChange,
    user,
}) => {
    const [candidate, loadingDetail] = useCandidateDetail(seed);
    const isAnon = !user || user.isAnon !== false;

    const {
        validation,
        status,
        castVote,
        loginPromptOpen,
        closeLoginPrompt,
    } = useCandidateVote({
        osId: candidate ? candidate.osId : null,
        initialValidation: candidate ? candidate.validation : null,
        isAnon,
        onValidationChange,
    });

    const handleVote = useCallback(vote => castVote(vote), [castVote]);

    if (!candidate) return null;

    const { state, tally, yourVote, votingOpen } = validation;
    const isDisputed = state === CANDIDATE_STATES.DISPUTED;
    const votes = totalVotes(tally);
    const buttonsDisabled =
        !votingOpen ||
        status === VOTE_STATUS.SAVING ||
        status === VOTE_STATUS.RETIRED;

    return (
        <Paper
            elevation={variant === PANEL_VARIANTS.OVERLAY ? 4 : 0}
            className={`${classes.root} ${classes[variant]}`}
            data-testid="candidate-validation-panel"
            data-os-id={candidate.osId}
        >
            <div className={classes.header}>
                <div className={classes.headerText}>
                    <div>
                        <CandidateBadge />
                    </div>
                    <Typography component="h3" className={classes.title}>
                        {CANDIDATE_COPY.panelTitle}
                    </Typography>
                    <Typography component="p" className={classes.intro}>
                        {CANDIDATE_COPY.panelIntro}
                    </Typography>
                </div>
                {onClose && (
                    <IconButton
                        size="small"
                        onClick={onClose}
                        aria-label="Close"
                        className={classes.closeButton}
                        data-testid="candidate-panel-close"
                    >
                        <CloseIcon fontSize="small" />
                    </IconButton>
                )}
            </div>

            <div className={classes.section}>
                <Typography className={classes.metaRow}>
                    <span className={classes.metaLabel}>
                        {CANDIDATE_COPY.provenanceSource}:
                    </span>{' '}
                    {candidate.source || '—'}
                </Typography>
                <Typography className={classes.metaRow}>
                    <span className={classes.metaLabel}>
                        {CANDIDATE_COPY.provenanceConfidence}:
                    </span>{' '}
                    {formatConfidence(candidate.confidence)}
                </Typography>
                {candidate.externalId && (
                    <Typography className={classes.metaRow}>
                        <span className={classes.metaLabel}>
                            {CANDIDATE_COPY.provenanceExternalId}:
                        </span>{' '}
                        {candidate.externalId}
                    </Typography>
                )}
            </div>

            <div className={classes.section}>
                <div className={classes.stateRow}>
                    <CandidateStateChip state={state} />
                    <Typography
                        className={`${classes.tally} ${
                            isDisputed ? classes.tallyDisputed : ''
                        }`}
                        data-testid="candidate-tally"
                    >
                        {votes === 0
                            ? CANDIDATE_COPY.noVotesYet
                            : formatCandidateTally(tally)}
                    </Typography>
                </div>
                <Typography className={classes.stateDescription}>
                    {CANDIDATE_STATE_DESCRIPTIONS[state] ||
                        CANDIDATE_STATE_DESCRIPTIONS[
                            CANDIDATE_STATES.UNVERIFIED
                        ]}
                </Typography>
            </div>

            <div className={classes.section}>
                {loadingDetail ? (
                    <div className={classes.loading}>
                        <CircularProgress size={20} />
                    </div>
                ) : (
                    <div className={classes.voteButtons}>
                        <VoteButton
                            classes={classes}
                            vote={CANDIDATE_VOTES.CONFIRMED}
                            label={CANDIDATE_COPY.voteFacility}
                            Icon={CheckCircleOutline}
                            selected={yourVote === CANDIDATE_VOTES.CONFIRMED}
                            disabled={buttonsDisabled}
                            onClick={handleVote}
                            testId="candidate-vote-confirmed"
                        />
                        <VoteButton
                            classes={classes}
                            vote={CANDIDATE_VOTES.NOT_A_FACILITY}
                            label={CANDIDATE_COPY.voteNotFacility}
                            Icon={HighlightOff}
                            selected={
                                yourVote === CANDIDATE_VOTES.NOT_A_FACILITY
                            }
                            disabled={buttonsDisabled}
                            onClick={handleVote}
                            testId="candidate-vote-not-a-facility"
                        />
                    </div>
                )}
                <StatusLine
                    classes={classes}
                    status={status}
                    votingOpen={votingOpen}
                    state={state}
                />
            </div>

            <SuggestedMatches
                classes={classes}
                matches={candidate.suggestedMatches || []}
            />

            <div className={`${classes.section} ${classes.sectionLast}`}>
                <Link
                    to={makeContributeProductionLocationUpdateURL(
                        candidate.osId,
                    )}
                    className={classes.knowLink}
                    data-testid="candidate-know-this-facility"
                >
                    <EditIcon fontSize="small" />
                    {CANDIDATE_COPY.knowThisFacility}
                </Link>
                <Typography className={classes.knowHint}>
                    {CANDIDATE_COPY.knowThisFacilityHint}
                </Typography>
            </div>

            <CandidateLoginDialog
                open={loginPromptOpen}
                onClose={closeLoginPrompt}
            />
        </Paper>
    );
};

CandidateValidationPanel.propTypes = {
    classes: PropTypes.object.isRequired,
    candidate: PropTypes.shape({
        osId: PropTypes.string.isRequired,
        source: PropTypes.string,
        confidence: PropTypes.number,
        externalId: PropTypes.string,
        validation: PropTypes.shape({
            state: PropTypes.string,
            tally: PropTypes.object,
            yourVote: PropTypes.string,
            votingOpen: PropTypes.bool,
        }),
        suggestedMatches: PropTypes.array,
        isDetailLoaded: PropTypes.bool,
    }),
    variant: PropTypes.oneOf(Object.values(PANEL_VARIANTS)),
    onClose: PropTypes.func,
    onValidationChange: PropTypes.func,
    user: PropTypes.shape({ isAnon: PropTypes.bool }),
};

CandidateValidationPanel.defaultProps = {
    candidate: null,
    variant: PANEL_VARIANTS.INLINE,
    onClose: null,
    onValidationChange: null,
    user: null,
};

const mapStateToProps = ({ auth }) => ({
    user: auth && auth.user ? auth.user.user : null,
});

export default connect(mapStateToProps)(
    withStyles(candidateValidationPanelStyles)(CandidateValidationPanel),
);
