import React from 'react';
import { arrayOf, bool, func, object, shape, string } from 'prop-types';
import Dialog from '@material-ui/core/Dialog';
import DialogTitle from '@material-ui/core/DialogTitle';
import DialogContent from '@material-ui/core/DialogContent';
import DialogActions from '@material-ui/core/DialogActions';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';

import { primaryButtonStyles } from './InitialClaimFlow/ClaimForm/styles';

/*
 * Generic outcome dialog for the claim flows (OSDEV-3371): shown after
 * submitting a claim (ClaimForm, ClaimFacilityStepper) and after saving
 * a pending claim edit (PendingClaimEdit). Texts and actions come in as
 * props; the structure and styling follow the v1 claim flow's success
 * dialog.
 */
const claimOutcomeDialogStyles = theme =>
    Object.freeze({
        dialogTitle: Object.freeze({
            fontSize: '36px',
            fontWeight: theme.typography.fontWeightSemiBoldPlus,
            display: 'flex',
            alignItems: 'center',
            textAlign: 'center',
            justifyContent: 'center',
        }),
        dialogBodyText: Object.freeze({
            textAlign: 'center',
            fontSize: '18px',
        }),
        dialogActions: Object.freeze({
            justifyContent: 'center',
            padding: theme.spacing.unit * 2,
            gap: '24px',
            [theme.breakpoints.down('sm')]: {
                flexDirection: 'column',
                gap: '12px',
            },
        }),
        secondaryButton: Object.freeze({
            width: '200px',
            height: '49px',
            borderRadius: 0,
            textTransform: 'none',
            fontSize: '18px',
            fontWeight: theme.typography.fontWeightExtraBold,
            border: '1px solid #0D1128',
            [theme.breakpoints.down('sm')]: {
                width: '100%',
            },
        }),
        primaryButton: primaryButtonStyles(theme),
    });

function ClaimOutcomeDialog({ classes, open, title, body, actions }) {
    return (
        <Dialog open={open}>
            <DialogTitle className={classes.dialogTitle}>
                <Typography className={classes.dialogTitle}>{title}</Typography>
            </DialogTitle>
            <DialogContent>
                <Typography variant="body1" className={classes.dialogBodyText}>
                    {body}
                </Typography>
            </DialogContent>
            <DialogActions className={classes.dialogActions}>
                {actions.map(action => (
                    <Button
                        key={action.label}
                        variant="contained"
                        color="primary"
                        onClick={action.onClick}
                        href={action.href}
                        className={
                            action.secondary
                                ? classes.secondaryButton
                                : classes.primaryButton
                        }
                    >
                        {action.label}
                    </Button>
                ))}
            </DialogActions>
        </Dialog>
    );
}

ClaimOutcomeDialog.defaultProps = {
    open: false,
};

ClaimOutcomeDialog.propTypes = {
    classes: object.isRequired,
    open: bool,
    title: string.isRequired,
    body: string.isRequired,
    actions: arrayOf(
        shape({
            label: string.isRequired,
            onClick: func,
            href: string,
            secondary: bool,
        }),
    ).isRequired,
};

export default withStyles(claimOutcomeDialogStyles)(ClaimOutcomeDialog);
