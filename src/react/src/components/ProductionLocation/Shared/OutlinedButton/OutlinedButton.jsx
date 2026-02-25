import React from 'react';
import { func, string } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';

import Button from '@material-ui/core/Button';

import outlinedButtonStyles from './styles';

const OutlinedButton = ({ classes, label, onClick, ...rest }) => (
    <Button classes={{ root: classes.button }} onClick={onClick} {...rest}>
        {label}
    </Button>
);

OutlinedButton.propTypes = {
    label: string.isRequired,
    onClick: func.isRequired,
};

export default withStyles(outlinedButtonStyles)(OutlinedButton);
