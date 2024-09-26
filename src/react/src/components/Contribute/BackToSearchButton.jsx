import React from 'react';
import ArrowBack from '@material-ui/icons/ArrowBackIos';
import { Button } from '@material-ui/core';
import { withStyles } from '@material-ui/core/styles';
import { string, func, object } from 'prop-types';
import { makeBackToSearchButtonStyles } from '../../util/styles';

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
