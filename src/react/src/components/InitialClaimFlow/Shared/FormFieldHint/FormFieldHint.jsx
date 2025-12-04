import React from 'react';
import { string, shape } from 'prop-types';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';
import styles from './styles';

const FormFieldHint = ({ text, classes }) => (
    <Typography className={classes.hint}>{text}</Typography>
);

FormFieldHint.propTypes = {
    text: string.isRequired,
    classes: shape({
        hint: string.isRequired,
    }).isRequired,
};

export default withStyles(styles)(FormFieldHint);
