import React from 'react';
import { bool, func, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';
import { makeProductionLocationCloseButtonStyles } from '../../util/styles';

const ProductionLocationDialogCloseButton = ({
    isMobile,
    classes,
    handleGoToMainPage,
}) => (
    <>
        {isMobile ? (
            <IconButton
                aria-label="Close"
                className="mobile-dialog-close-button"
                onClick={() => handleGoToMainPage()}
            >
                <CloseIcon />
            </IconButton>
        ) : (
            <IconButton
                aria-label="Close"
                className={classes.desktopCloseButton}
                onClick={() => handleGoToMainPage()}
            >
                <CloseIcon />
            </IconButton>
        )}
    </>
);

ProductionLocationDialogCloseButton.propTypes = {
    handleGoToMainPage: func.isRequired,
    isMobile: bool.isRequired,
    classes: object.isRequired,
};

export default withStyles(makeProductionLocationCloseButtonStyles)(
    ProductionLocationDialogCloseButton,
);
