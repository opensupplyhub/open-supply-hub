import React from 'react';
import { object, oneOf, string } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import { VERIFICATION_OPTION_TAGS } from './constants';
import styles from './styles';

/**
 * A choice in a verification dropdown, with a small tag that says whether
 * it is a preferred kind of proof or one that can delay the review.
 */
const VerificationOptionLabel = ({ label, tag, classes }) => (
    <span className={classes.root}>
        <span className={classes.label}>{label}</span>
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
            {tag}
        </span>
    </span>
);

VerificationOptionLabel.propTypes = {
    label: string.isRequired,
    tag: oneOf(Object.values(VERIFICATION_OPTION_TAGS)).isRequired,
    classes: object.isRequired,
};

const StyledVerificationOptionLabel = withStyles(styles)(
    VerificationOptionLabel,
);

/**
 * How an option in a verification dropdown is drawn (react-select's
 * `formatOptionLabel`). In the open list an option shows its `tag` beside
 * its label. The chosen value shows the label alone. The tag is display
 * only: the option's `label` is what the claim stores, so the tag must
 * never be folded into it.
 */
export const formatVerificationOptionLabel = (option, { context }) =>
    context === 'menu' ? (
        <StyledVerificationOptionLabel label={option.label} tag={option.tag} />
    ) : (
        option.label
    );

export default StyledVerificationOptionLabel;
