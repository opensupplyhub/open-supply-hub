import React from 'react';
import { string, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import Tooltip from '@material-ui/core/Tooltip';
import HelpOutlineIcon from '@material-ui/icons/HelpOutline';
import { labelStyles } from './styles.js';

const LabelWithTooltip = ({ label, tooltipText, classes }) => (
    <Grid container className={classes.labelContainer}>
        <Grid item>
            <Typography className={classes.label}>{label}</Typography>
        </Grid>
        <Grid container item className={classes.tooltipContainer}>
            <Tooltip
                title={tooltipText}
                enterTouchDelay={0}
                placement="top"
                classes={{
                    tooltip: classes.tooltip,
                    popper: classes.tooltipPopper,
                }}
            >
                <HelpOutlineIcon className={classes.helpIcon} />
            </Tooltip>
        </Grid>
    </Grid>
);

LabelWithTooltip.propTypes = {
    label: string.isRequired,
    tooltipText: string.isRequired,
    classes: object.isRequired,
};

export default withStyles(labelStyles)(LabelWithTooltip);
