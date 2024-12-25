import React from 'react';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import ErrorOutlineIcon from '@material-ui/icons/ErrorOutline';
import { inputErrorText } from '../../util/styles';

const InputErrorText = ({ classes, text = 'This field is required.' }) => (
    <span className={classes.errorTextWrapStyles}>
        <ErrorOutlineIcon className={classes.iconInfoStyles} />
        <Typography component="span" className={classes.inputErrorTextStyles}>
            {text}
        </Typography>
    </span>
);

export default withStyles(inputErrorText)(InputErrorText);
