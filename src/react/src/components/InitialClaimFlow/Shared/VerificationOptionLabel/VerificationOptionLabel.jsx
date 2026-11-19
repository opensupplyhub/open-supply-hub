import React from 'react';
import { oneOf, string, shape } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import {
    VERIFICATION_OPTION_TAGS,
    VERIFICATION_OPTION_TAG_TEXT,
} from './constants';
import styles from './styles';

/**
 * A choice in a verification dropdown, with a small tag that says whether
 * it is a preferred kind of proof or one that can delay the review.
 */
const VerificationOptionLabel = ({ label, tag, classes }) => (
    <span className={classes.root}>
        <span>{label}</span>
        {tag && (
            <span
                className={
                    tag === VERIFICATION_OPTION_TAGS.PREFERRED
                        ? classes.preferredTag
                        : classes.canDelayTag
                }
            >
                {tag === VERIFICATION_OPTION_TAGS.PREFERRED && (
                    <span aria-hidden="true">★ </span>
                )}
                {VERIFICATION_OPTION_TAG_TEXT[tag]}
            </span>
        )}
    </span>
);

VerificationOptionLabel.defaultProps = {
    tag: null,
};

VerificationOptionLabel.propTypes = {
    label: string.isRequired,
    tag: oneOf(Object.values(VERIFICATION_OPTION_TAGS)),
    classes: shape({
        root: string.isRequired,
        preferredTag: string.isRequired,
        canDelayTag: string.isRequired,
    }).isRequired,
};

export default withStyles(styles)(VerificationOptionLabel);
