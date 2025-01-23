import React from 'react';
import { bool, func } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';
import { makeProductionLocationCloseButtonStyles } from '../../util/styles';

const ProductionLocationDialogCloseButton = withStyles(
    makeProductionLocationCloseButtonStyles,
)(props => {
    const { isMobile, classes, handleShow } = props;
    return (
        <>
            {isMobile ? (
                <IconButton
                    aria-label="Close"
                    className="mobile-dialog-close-button"
                    onClick={() => handleShow(false)}
                >
                    <CloseIcon />
                </IconButton>
            ) : (
                <IconButton
                    aria-label="Close"
                    className={classes.desktopCloseButton}
                    onClick={() => handleShow(false)}
                >
                    <CloseIcon />
                </IconButton>
            )}
        </>
    );
});

ProductionLocationDialogCloseButton.propTypes = {
    handleShow: func.isRequired,
    isMobile: bool.isRequired,
};

export default ProductionLocationDialogCloseButton;
