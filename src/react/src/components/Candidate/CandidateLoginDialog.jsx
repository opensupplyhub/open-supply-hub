import React from 'react';
import { bool, func } from 'prop-types';
import { Link } from 'react-router-dom';
import Dialog from '@material-ui/core/Dialog';
import DialogTitle from '@material-ui/core/DialogTitle';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogActions from '@material-ui/core/DialogActions';
import Button from '@material-ui/core/Button';

import { authLoginFormRoute } from '../../util/constants';
import { CANDIDATE_COPY } from '../../util/candidateCopy';

/**
 * Login prompt for anonymous voters. Mirrors the gated-action pattern used
 * by ReportFacilityStatusDialog / LoginRequiredDialog: explain, then link
 * to the login form. No request is sent until the user is signed in.
 */
const CandidateLoginDialog = ({ open, onClose }) => (
    <Dialog
        open={open}
        onClose={onClose}
        aria-labelledby="candidate-login-dialog-title"
        PaperProps={{ 'data-testid': 'candidate-login-dialog' }}
    >
        <DialogTitle id="candidate-login-dialog-title">
            {CANDIDATE_COPY.loginTitle}
        </DialogTitle>
        <DialogContent>
            <DialogContentText>{CANDIDATE_COPY.loginBody}</DialogContentText>
        </DialogContent>
        <DialogActions>
            <Button variant="outlined" color="secondary" onClick={onClose}>
                {CANDIDATE_COPY.loginCancel}
            </Button>
            <Button
                variant="contained"
                color="primary"
                onClick={onClose}
                component={Link}
                to={authLoginFormRoute}
                data-testid="candidate-login-dialog-login"
            >
                {CANDIDATE_COPY.loginAction}
            </Button>
        </DialogActions>
    </Dialog>
);

CandidateLoginDialog.propTypes = {
    open: bool.isRequired,
    onClose: func.isRequired,
};

export default CandidateLoginDialog;
