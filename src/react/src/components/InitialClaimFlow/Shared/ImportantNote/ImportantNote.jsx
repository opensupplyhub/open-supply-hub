import React from 'react';
import { string, object, oneOf } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import Warning from '@material-ui/icons/Warning';
import InfoIcon from '@material-ui/icons/Info';

import importantNoteStyles from './styles';

const ImportantNote = ({ classes, text, iconType }) => {
    const Icon = iconType === 'info' ? InfoIcon : Warning;

    return (
        <Grid container className={classes.container}>
            <Typography variant="body2" className={classes.text}>
                <span className={classes.iconWrapper}>
                    <Icon className={classes.icon} />
                    <strong>IMPORTANT!</strong>
                </span>
                <span>{text}</span>
            </Typography>
        </Grid>
    );
};

ImportantNote.defaultProps = {
    iconType: 'warning',
};

ImportantNote.propTypes = {
    classes: object.isRequired,
    text: string.isRequired,
    iconType: oneOf(['warning', 'info']),
};

export default withStyles(importantNoteStyles)(ImportantNote);
