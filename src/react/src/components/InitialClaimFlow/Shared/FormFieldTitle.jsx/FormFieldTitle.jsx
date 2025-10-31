import React from 'react';
import { string, bool, shape } from 'prop-types';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';
import RequiredAsterisk from '../../../RequiredAsterisk';
import styles from './styles';

const FormFieldTitle = ({ label, required, classes }) => (
    <Typography component="h4" className={classes.title}>
        {label}
        {required ? <RequiredAsterisk /> : null}
    </Typography>
);

FormFieldTitle.defaultProps = {
    required: false,
};

FormFieldTitle.propTypes = {
    label: string.isRequired,
    required: bool,
    classes: shape({
        title: string.isRequired,
    }).isRequired,
};

export default withStyles(styles)(FormFieldTitle);
