import React from 'react';
import { bool, func, object, string } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Dialog from '@material-ui/core/Dialog';
import DialogTitle from '@material-ui/core/DialogTitle';
import DialogContent from '@material-ui/core/DialogContent';
import DialogActions from '@material-ui/core/DialogActions';
import Button from '@material-ui/core/Button';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';
import Typography from '@material-ui/core/Typography';
import { makeContributionWarningDialogStyles } from '../../util/styles';

const ContributionWarningDialog = ({
    open,
    onClose,
    onSubmitAnyway,
    title,
    message,
    classes,
}) => (
    <Dialog
        classes={{ paper: classes.dialogPaperStyles }}
        open={open}
        onClose={onClose}
        aria-labelledby="contribution-warning-dialog-title"
    >
        <IconButton
            aria-label="Close"
            className={classes.closeButtonStyles}
            onClick={onClose}
        >
            <CloseIcon />
        </IconButton>
        <DialogTitle id="contribution-warning-dialog-title" disableTypography>
            <Typography className={classes.dialogTitleStyles}>
                {title}
            </Typography>
        </DialogTitle>
        <DialogContent>
            <Typography className={classes.dialogBodyStyles}>
                {message}
            </Typography>
        </DialogContent>
        <DialogActions className={classes.dialogActionsStyles}>
            <Button
                variant="contained"
                color="secondary"
                onClick={onClose}
                classes={{
                    root: classes.buttonBaseStyles,
                    label: classes.buttonLabelStyles,
                }}
            >
                Go back and edit
            </Button>
            <Button
                variant="contained"
                onClick={onSubmitAnyway}
                classes={{
                    root: `${classes.buttonBaseStyles} ${classes.submitAnywayButtonStyles}`,
                    label: classes.buttonLabelStyles,
                }}
            >
                Submit anyway
            </Button>
        </DialogActions>
    </Dialog>
);

ContributionWarningDialog.propTypes = {
    open: bool.isRequired,
    onClose: func.isRequired,
    onSubmitAnyway: func.isRequired,
    title: string.isRequired,
    message: string.isRequired,
    classes: object.isRequired,
};

export default withStyles(makeContributionWarningDialogStyles)(
    ContributionWarningDialog,
);
