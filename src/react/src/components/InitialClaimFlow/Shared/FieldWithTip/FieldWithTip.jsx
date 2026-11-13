import React from 'react';
import { node, string, shape } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import styles from './styles';

/**
 * Lays out a form field with a tip that explains it. The tip comes after
 * the field in the DOM. On wide screens it sits in a second column, level
 * with the control; on narrower screens it drops under the control at full
 * width. Everything stays in normal page flow, so the tip can never overlap
 * the next section or leave the form card.
 */
const FieldWithTip = ({ heading, children, tip, classes }) => (
    <div className={classes.root}>
        <div className={classes.field}>{heading}</div>
        <div className={classes.field}>{children}</div>
        <div className={classes.tip}>{tip}</div>
    </div>
);

FieldWithTip.propTypes = {
    heading: node.isRequired,
    children: node.isRequired,
    tip: node.isRequired,
    classes: shape({
        root: string.isRequired,
        field: string.isRequired,
        tip: string.isRequired,
    }).isRequired,
};

export default withStyles(styles)(FieldWithTip);
