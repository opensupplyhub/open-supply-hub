import React from 'react';
import { arrayOf, string, shape } from 'prop-types';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';
import styles from './styles';

/**
 * Static guidance shown at a proof question on the claim form: what is
 * approved fastest (`title` and `details`) and what can delay approval
 * (`delays`). Text only, no logic.
 */
const BestProofBox = ({ title, details, delays, classes }) => (
    <div className={classes.box} data-testid="best-proof-box">
        <Typography className={classes.title}>{title}</Typography>
        {details.map(line => (
            <Typography key={line} className={classes.detail}>
                {line}
            </Typography>
        ))}
        {delays.map(line => (
            <Typography key={line} className={classes.delay}>
                {line}
            </Typography>
        ))}
    </div>
);

BestProofBox.defaultProps = {
    details: [],
    delays: [],
};

BestProofBox.propTypes = {
    title: string.isRequired,
    details: arrayOf(string),
    delays: arrayOf(string),
    classes: shape({
        box: string.isRequired,
        title: string.isRequired,
        detail: string.isRequired,
        delay: string.isRequired,
    }).isRequired,
};

export default withStyles(styles)(BestProofBox);
