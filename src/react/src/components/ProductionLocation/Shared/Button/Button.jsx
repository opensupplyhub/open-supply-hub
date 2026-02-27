import React from 'react';
import { func, string, oneOf } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';

import MaterialButton from '@material-ui/core/Button';

import buttonStyles from './styles';
import { VARIANT } from './constants';

const Button = ({ classes, variant, label, onClick, ...rest }) => (
    <MaterialButton
        classes={{ root: classes[variant] }}
        onClick={onClick}
        {...rest}
    >
        {label}
    </MaterialButton>
);

Button.propTypes = {
    label: string.isRequired,
    onClick: func.isRequired,
    variant: oneOf([VARIANT.outlined, VARIANT.filled]),
};

Button.defaultProps = {
    variant: VARIANT.filled,
};

export default withStyles(buttonStyles)(Button);
