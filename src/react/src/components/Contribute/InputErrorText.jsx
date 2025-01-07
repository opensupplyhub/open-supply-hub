import React from 'react';
import { withStyles } from '@material-ui/core/styles';
import { string, object } from 'prop-types';
import Typography from '@material-ui/core/Typography';
import ErrorOutlineIcon from '@material-ui/icons/ErrorOutline';
import { inputErrorText } from '../../util/styles';

const InputErrorText = ({ classes, text }) => (
    <span className={classes.errorTextWrapStyles}>
        <ErrorOutlineIcon className={classes.iconInfoStyles} />
        <Typography component="span" className={classes.inputErrorTextStyles}>
            {text}
        </Typography>
    </span>
);

InputErrorText.defaultProps = {
    text: 'This field is required.',
};

InputErrorText.propTypes = {
    text: string,
    classes: object.isRequired,
};

export default withStyles(inputErrorText)(InputErrorText);