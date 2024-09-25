import React from 'react';
import { string, func, object } from 'prop-types';
import { Button } from '@material-ui/core';
import { withStyles } from '@material-ui/core/styles';
import ArrowBack from '@material-ui/icons/ArrowBackIos';

const makeBackToSearchButtonStyles = theme =>
    Object.freeze({
        backButtonRootStyles: Object.freeze({
            textTransform: 'none',
            fontSize: '18px',
            fontWeight: theme.typography.fontWeightSemiBoldPlus,
        }),
        backButtonLabelStyles: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
        }),
    });

const BackToSearchButton = ({ label, handleBackToSearch, classes }) => (
    <Button
        color="primary"
        classes={{
            root: classes.backButtonRootStyles,
            label: classes.backButtonLabelStyles,
        }}
        onClick={handleBackToSearch}
    >
        <ArrowBack />
        {label}
    </Button>
);

BackToSearchButton.propTypes = {
    label: string.isRequired,
    handleBackToSearch: func.isRequired,
    classes: object.isRequired,
};

export default withStyles(makeBackToSearchButtonStyles)(BackToSearchButton);
