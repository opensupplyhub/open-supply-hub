import React from 'react';
import PropTypes from 'prop-types';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';
import moment from 'moment';

import CandidateBadge, { CandidateStateChip } from './CandidateBadge';
import { CANDIDATE_COPY } from '../../util/candidateCopy';
import { formatConfidence } from '../../util/candidates';
import { candidateHeadingStyles } from './styles';

/**
 * Detail-page header block for a candidate OS ID: badge, state and the
 * provenance line (source, confidence, external id, detection date).
 */
const CandidateHeading = ({ classes, candidate }) => {
    if (!candidate) return null;

    const items = [
        {
            key: 'source',
            label: CANDIDATE_COPY.provenanceSource,
            value: candidate.source,
        },
        {
            key: 'confidence',
            label: CANDIDATE_COPY.provenanceConfidence,
            value:
                typeof candidate.confidence === 'number'
                    ? formatConfidence(candidate.confidence)
                    : null,
        },
        {
            key: 'external-id',
            label: CANDIDATE_COPY.provenanceExternalId,
            value: candidate.externalId,
        },
        {
            key: 'detected',
            label: CANDIDATE_COPY.provenanceDetected,
            value: candidate.createdAt
                ? moment(candidate.createdAt).format('LL')
                : null,
        },
    ].filter(item => item.value);

    return (
        <div className={classes.container} data-testid="candidate-heading">
            <div className={classes.badgeRow}>
                <CandidateBadge />
                <CandidateStateChip state={candidate.validation.state} />
            </div>
            {items.length > 0 && (
                <Typography
                    component="p"
                    className={classes.provenance}
                    data-testid="candidate-provenance"
                >
                    {items.map(item => (
                        <span key={item.key} className={classes.provenanceItem}>
                            <span className={classes.provenanceLabel}>
                                {item.label}:
                            </span>{' '}
                            {item.value}
                        </span>
                    ))}
                </Typography>
            )}
            <Typography component="p" className={classes.note}>
                {CANDIDATE_COPY.detailHiddenSectionsNote}
            </Typography>
        </div>
    );
};

CandidateHeading.propTypes = {
    classes: PropTypes.object.isRequired,
    candidate: PropTypes.shape({
        source: PropTypes.string,
        confidence: PropTypes.number,
        externalId: PropTypes.string,
        createdAt: PropTypes.string,
        validation: PropTypes.shape({ state: PropTypes.string }),
    }),
};

CandidateHeading.defaultProps = {
    candidate: null,
};

export default withStyles(candidateHeadingStyles)(CandidateHeading);
