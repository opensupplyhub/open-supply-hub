import React from 'react';
import { func, string } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';

import Button from '@material-ui/core/Button';

import filledButtonStyles from './styles';

const FilledButton = ({ classes, label, onClick, ...rest }) => (
    <Button classes={{ root: classes.button }} onClick={onClick} {...rest}>
        {label}
    </Button>
);

FilledButton.propTypes = {
    label: string.isRequired,
    onClick: func.isRequired,
};

export default withStyles(filledButtonStyles)(FilledButton);
