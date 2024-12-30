import React from 'react';
import { bool, func, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Dialog from '@material-ui/core/Dialog';
import DialogTitle from '@material-ui/core/DialogTitle';
import DialogActions from '@material-ui/core/DialogActions';
import Button from '@material-ui/core/Button';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';
import Typography from '@material-ui/core/Typography';
import history from '../../util/history';
import { makeConfirmNotFoundLocationDialogStyles } from '../../util/styles';
import { contributeProductionLocationRoute } from '../../util/constants';

const ConfirmNotFoundLocationDialog = ({
    confirmDialogIsOpen,
    handleConfirmDialogClose,
    clearLocations,
    classes,
}) => {
    const handleAddNewLocation = () => {
        handleConfirmDialogClose();
        clearLocations();
    };

    const handleSearchAgain = () => {
        handleConfirmDialogClose();
        history.push(`${contributeProductionLocationRoute}?tab=name-address`);
        clearLocations();
    };

    return (
        <Dialog
            classes={{
                paper: classes.dialogPaperStyles,
            }}
            open={confirmDialogIsOpen}
            onClose={handleConfirmDialogClose}
            aria-labelledby="confirm-not-found-location-dialog-title"
        >
            <IconButton
                aria-label="Close"
                className={classes.closeButtonStyles}
                onClick={handleConfirmDialogClose}
            >
                <CloseIcon />
            </IconButton>
            <DialogTitle id="confirm-not-found-location-dialog-title">
                <Typography className={classes.dialogTitleStyles}>
                    Are you sure you have reviewed the entire list and could not
                    find the production location?
                </Typography>
            </DialogTitle>
            <DialogActions className={classes.dialogActionsStyles}>
                <Button
                    variant="contained"
                    color="secondary"
                    onClick={handleSearchAgain}
                    classes={{
                        root: classes.buttonBaseStyles,
                        label: classes.buttonLabelStyles,
                    }}
                >
                    No, I would like to try searching again
                </Button>
                <Button
                    variant="contained"
                    onClick={handleAddNewLocation}
                    classes={{
                        root: `${classes.buttonBaseStyles} ${classes.addLocationButtonStyles}`,
                        label: classes.buttonLabelStyles,
                    }}
                >
                    Yes, add a new production location
                </Button>
            </DialogActions>
        </Dialog>
    );
};

ConfirmNotFoundLocationDialog.propTypes = {
    confirmDialogIsOpen: bool.isRequired,
    handleConfirmDialogClose: func.isRequired,
    clearLocations: func.isRequired,
    classes: object.isRequired,
};

export default withStyles(makeConfirmNotFoundLocationDialogStyles)(
    ConfirmNotFoundLocationDialog,
);
