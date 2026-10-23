import React, { useRef, useState } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { withStyles } from '@material-ui/core/styles';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import Divider from '@material-ui/core/Divider';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';

import Button from '../../Shared/Button/Button';
import { VARIANT } from '../../Shared/Button/constants';
import { authLoginFormRoute } from '../../../../util/constants';
import {
    CLAIM_INVITE_NOTE_MAX_LENGTH,
    sendClaimInvite,
} from '../../../../util/claimInvite';
import claimInviteDialogStyles from './claimInviteDialogStyles';

const STATUS = Object.freeze({
    idle: 'idle',
    sending: 'sending',
    sent: 'sent',
});

const ClaimInviteDialog = ({
    classes,
    open,
    onClose,
    osId,
    facilityName,
    isAnonymousUser,
}) => {
    const [recipientEmail, setRecipientEmail] = useState('');
    const [note, setNote] = useState('');
    const [status, setStatus] = useState(STATUS.idle);
    const [errorMessage, setErrorMessage] = useState(null);
    // A send can still be in flight after the dialog is closed and
    // reopened. inFlight blocks a second send until it settles, and the
    // session counter drops its result so it can't change the reopened
    // dialog.
    const inFlight = useRef(false);
    const session = useRef(0);

    const closeDialog = () => {
        session.current += 1;
        onClose();
        setRecipientEmail('');
        setNote('');
        setStatus(STATUS.idle);
        setErrorMessage(null);
    };

    // Wired to both the form (Enter in the email field) and the Send
    // button, which MUI renders as type="button", so a click submits once.
    const handleSubmit = event => {
        event.preventDefault();
        if (!recipientEmail.trim() || inFlight.current) return;

        const sendSession = session.current;
        inFlight.current = true;
        setStatus(STATUS.sending);
        setErrorMessage(null);
        sendClaimInvite(osId, { recipientEmail: recipientEmail.trim(), note })
            .then(() => {
                if (sendSession === session.current) setStatus(STATUS.sent);
            })
            .catch(error => {
                if (sendSession !== session.current) return;
                setStatus(STATUS.idle);
                setErrorMessage(error.message);
            })
            .finally(() => {
                inFlight.current = false;
            });
    };

    const renderLoginPrompt = () => (
        <>
            <DialogContent>
                <DialogContentText className={classes.description}>
                    Log in to send someone at this production location a link to
                    claim its profile.
                </DialogContentText>
            </DialogContent>
            <DialogActions className={classes.dialogActions}>
                <Button
                    variant={VARIANT.filled}
                    label="Log In"
                    onClick={onClose}
                    component={Link}
                    to={{
                        pathname: authLoginFormRoute,
                        state: { prevPath: window.location.pathname },
                    }}
                    data-testid="claim-invite-dialog-login"
                />
            </DialogActions>
        </>
    );

    const renderSent = () => (
        <>
            <DialogContent>
                <DialogContentText
                    className={classes.description}
                    data-testid="claim-invite-dialog-sent"
                >
                    {`We sent an invite to ${recipientEmail.trim()} with a link to claim this profile and tips for getting the claim approved.`}
                </DialogContentText>
            </DialogContent>
            <DialogActions className={classes.dialogActions}>
                <Button
                    variant={VARIANT.filled}
                    label="Done"
                    onClick={closeDialog}
                    data-testid="claim-invite-dialog-done"
                />
            </DialogActions>
        </>
    );

    const renderForm = () => (
        <form onSubmit={handleSubmit} noValidate>
            <DialogContent>
                <DialogContentText className={classes.description}>
                    Know someone who works at this production location? We will
                    email them a link to claim its profile, with a guide to the
                    claim process. Your organization is named as the sender.
                </DialogContentText>
                <TextField
                    autoFocus
                    required
                    fullWidth
                    type="email"
                    margin="dense"
                    variant="outlined"
                    label="Their email address"
                    value={recipientEmail}
                    onChange={e => {
                        setRecipientEmail(e.target.value);
                        setErrorMessage(null);
                    }}
                    className={classes.textField}
                    inputProps={{ 'data-testid': 'claim-invite-email' }}
                />
                <TextField
                    fullWidth
                    multiline
                    rows={4}
                    margin="dense"
                    variant="outlined"
                    label="Add a personal note (optional)"
                    value={note}
                    onChange={e => {
                        setNote(e.target.value);
                        setErrorMessage(null);
                    }}
                    className={classes.textField}
                    InputProps={{ className: classes.noteInput }}
                    helperText={`No links or web addresses. ${note.length}/${CLAIM_INVITE_NOTE_MAX_LENGTH}`}
                    inputProps={{
                        maxLength: CLAIM_INVITE_NOTE_MAX_LENGTH,
                        'data-testid': 'claim-invite-note',
                    }}
                />
                {errorMessage && (
                    <Typography
                        color="error"
                        className={classes.error}
                        data-testid="claim-invite-dialog-error"
                    >
                        {errorMessage}
                    </Typography>
                )}
            </DialogContent>
            <DialogActions className={classes.dialogActions}>
                <Button
                    variant={VARIANT.outlined}
                    label="Cancel"
                    onClick={closeDialog}
                    data-testid="claim-invite-dialog-cancel"
                />
                <Button
                    variant={VARIANT.filled}
                    onClick={handleSubmit}
                    label={
                        status === STATUS.sending ? 'Sending…' : 'Send invite'
                    }
                    disabled={
                        !recipientEmail.trim() || status === STATUS.sending
                    }
                    data-testid="claim-invite-dialog-send"
                />
            </DialogActions>
        </form>
    );

    const renderBody = () => {
        if (isAnonymousUser) return renderLoginPrompt();
        if (status === STATUS.sent) return renderSent();
        return renderForm();
    };

    return (
        <Dialog
            open={open}
            onClose={closeDialog}
            aria-labelledby="claim-invite-dialog-title"
            maxWidth={false}
            PaperProps={{
                className: classes.dialogPaper,
                'data-testid': 'claim-invite-dialog',
            }}
        >
            <DialogTitle
                id="claim-invite-dialog-title"
                disableTypography
                className={classes.dialogTitle}
            >
                <Typography variant="title" className={classes.title}>
                    Send a link to claim this profile
                </Typography>
                {facilityName && (
                    <Typography
                        className={classes.facilityName}
                        data-testid="claim-invite-dialog-facility-name"
                    >
                        {`Production Location Name: ${facilityName}`}
                    </Typography>
                )}
                <Divider />
            </DialogTitle>
            {renderBody()}
        </Dialog>
    );
};

ClaimInviteDialog.propTypes = {
    classes: PropTypes.object.isRequired,
    open: PropTypes.bool.isRequired,
    onClose: PropTypes.func.isRequired,
    osId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
    facilityName: PropTypes.string,
    isAnonymousUser: PropTypes.bool.isRequired,
};

ClaimInviteDialog.defaultProps = {
    facilityName: null,
};

const mapStateToProps = ({
    auth: {
        user: { user },
    },
}) => ({
    isAnonymousUser: !user || user.isAnon,
});

export default connect(mapStateToProps)(
    withStyles(claimInviteDialogStyles)(ClaimInviteDialog),
);
