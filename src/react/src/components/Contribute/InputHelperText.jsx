import React from 'react';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import InfoOutlinedIcon from '@material-ui/icons/InfoOutlined';
import { inputHelperText } from '../../util/styles';

const InputHelperText = ({ classes, text = 'This field is required.' }) => (
    <span className={classes.helperTextWrapStyles}>
        <InfoOutlinedIcon className={classes.iconInfoStyles} />
        <Typography component="span" className={classes.inputHelperTextStyles}>
            {text}
        </Typography>
    </span>
);

export default withStyles(inputHelperText)(InputHelperText);
