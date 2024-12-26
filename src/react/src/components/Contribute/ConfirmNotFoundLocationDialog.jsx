import React from 'react';
import { withStyles } from '@material-ui/core/styles';
import Dialog from '@material-ui/core/Dialog';
import DialogTitle from '@material-ui/core/DialogTitle';
import DialogActions from '@material-ui/core/DialogActions';
import Button from '@material-ui/core/Button';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';
import Typography from '@material-ui/core/Typography';

const makeConfirmNotFoundLocationDialogStyles = theme =>
    Object.freeze({
        dialogPaperStyles: Object.freeze({
            borderRadius: 0,
            padding: '24px 80px 42px',
        }),
        closeButtonStyles: {
            position: 'absolute',
            right: '16px',
            top: '16px',
            color: '#000',
        },
        dialogTitleStyles: Object.freeze({
            fontSize: '32px',
            lineHeight: '32px',
            fontWeight: theme.typography.fontWeightSemiBoldPlus,
            textAlign: 'center',
            padding: 0,
        }),
        dialogActionsStyles: Object.freeze({
            display: 'flex',
            justifyContent: 'center',
            gap: '16px',
        }),
        buttonBaseStyles: Object.freeze({
            textTransform: 'none',
            border: 'none',
            height: '48px',
            width: '309px',
        }),
        buttonLabelStyles: Object.freeze({
            fontSize: '18px',
            lineHeight: '22px',
            fontWeight: theme.typography.fontWeightExtraBold,
        }),
        addLocationButtonStyles: Object.freeze({
            backgroundColor: theme.palette.action.main,
            '&:hover': {
                backgroundColor: theme.palette.action.dark,
            },
        }),
    });

const ConfirmNotFoundLocationDialog = ({
    confirmDialogIsOpen,
    handleConfirmDialogClose,
    classes,
}) => (
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
                onClick={handleConfirmDialogClose}
                classes={{
                    root: classes.buttonBaseStyles,
                    label: classes.buttonLabelStyles,
                }}
            >
                No, I would like to try searching again
            </Button>
            <Button
                variant="contained"
                onClick={handleConfirmDialogClose}
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

export default withStyles(makeConfirmNotFoundLocationDialogStyles)(
    ConfirmNotFoundLocationDialog,
);
