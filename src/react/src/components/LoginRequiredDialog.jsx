import React from 'react';
import { bool, func } from 'prop-types';
import Dialog from '@material-ui/core/Dialog';
import DialogTitle from '@material-ui/core/DialogTitle';
import DialogContent from '@material-ui/core/DialogContent';
import DialogActions from '@material-ui/core/DialogActions';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import RouterLink from './RouterLink';
import { authLoginFormRoute, authRegisterFormRoute } from '../util/constants';

function LoginRequiredDialog({ open, onClose }) {
    return (
        <Dialog open={open}>
            {open ? (
                <>
                    <DialogTitle>Log In To Download</DialogTitle>
                    <DialogContent>
                        <Typography>
                            You must log in with an Open Supply Hub account
                            before downloading your search results.
                        </Typography>
                    </DialogContent>
                    <DialogActions>
                        <Button
                            variant="outlined"
                            color="secondary"
                            onClick={onClose}
                        >
                            Cancel
                        </Button>
                        <Button
                            variant="outlined"
                            color="primary"
                            onClick={onClose}
                            component={RouterLink}
                            to={authRegisterFormRoute}
                        >
                            Register
                        </Button>
                        <Button
                            variant="outlined"
                            color="primary"
                            onClick={onClose}
                            component={RouterLink}
                            to={authLoginFormRoute}
                        >
                            Log In
                        </Button>
                    </DialogActions>
                </>
            ) : (
                <div style={{ display: 'none' }} />
            )}
        </Dialog>
    );
}

LoginRequiredDialog.propTypes = {
    open: bool.isRequired,
    onClose: func.isRequired,
};

export default LoginRequiredDialog;
