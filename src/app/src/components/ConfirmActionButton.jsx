import React, { Component } from 'react';

import { arrayOf, bool, func, shape, string } from 'prop-types';

import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogTitle from '@material-ui/core/DialogTitle';

import { CONFIRM_ACTION, MERGE_ACTION, REJECT_ACTION } from '../util/constants';

const actionDialogStates = Object.freeze({
    none: 'none',
    confirm: CONFIRM_ACTION,
    merge: MERGE_ACTION,
    reject: REJECT_ACTION,
});

export default class ConfirmActionButton extends Component {
    state = {
        currentDialog: actionDialogStates.none,
    };

    openActionDialog = action => {
        switch (action) {
            case CONFIRM_ACTION:
                this.setState(state =>
                    Object.assign({}, state, {
                        currentDialog: actionDialogStates.confirm,
                    }),
                );
                break;
            case MERGE_ACTION:
                this.props.updateTargetOSID(
                    this.props.activeCheckboxes[0]?.os_id,
                );
                this.props.updateToMergeOSID(
                    this.props.activeCheckboxes[1]?.os_id,
                );
                this.props.fetchToMergeFacility();
                this.props.fetchTargetFacility();

                this.props.openMergeModal();
                break;
            case REJECT_ACTION:
                this.setState(state =>
                    Object.assign({}, state, {
                        currentDialog: actionDialogStates.reject,
                    }),
                );
                break;
            default:
                break;
        }
    };

    closeDialog = () =>
        this.setState(state =>
            Object.assign({}, state, {
                currentDialog: actionDialogStates.none,
            }),
        );

    confirmFacilityMatch = () => {
        this.props.confirmMatch();
        return this.closeDialog();
    };

    rejectFacilityMatch = () => {
        this.props.rejectMatch();
        return this.closeDialog();
    };

    render() {
        const {
            action,
            listItem,
            fetching,
            activeSubmitButton,
            activeCheckboxes,
            buttonName,
        } = this.props;

        const confirmDialog = (
            <Dialog
                open={this.state.currentDialog === actionDialogStates.confirm}
                aria-labelledby="alert-dialog-title"
                aria-describedby="alert-dialog-description"
            >
                <DialogTitle id="alert-dialog-title">
                    Confirm this potential facility match?
                </DialogTitle>
                <DialogContent id="alert-dialog-description">
                    <h3>
                        This action will confirm this facility as a match for
                        the list item.
                    </h3>
                    <p>
                        <strong>Potential match:</strong>
                    </p>
                    <ul>
                        <li>name: {activeCheckboxes[0]?.name}</li>
                        <li>address: {activeCheckboxes[0]?.address}</li>
                    </ul>
                    <p>
                        <strong>List item:</strong>
                    </p>
                    <ul>
                        <li>name: {listItem?.name}</li>
                        <li>address: {listItem?.address}</li>
                    </ul>
                </DialogContent>
                <DialogActions>
                    <Button
                        variant="outlined"
                        color="primary"
                        onClick={this.closeDialog}
                    >
                        No, do not confirm
                    </Button>
                    <Button
                        variant="contained"
                        color="primary"
                        onClick={this.confirmFacilityMatch}
                    >
                        Yes, confirm
                    </Button>
                </DialogActions>
            </Dialog>
        );

        const rejectDialog = (
            <Dialog
                open={this.state.currentDialog === actionDialogStates.reject}
                aria-labelledby="alert-dialog-title"
                aria-describedby="alert-dialog-description"
            >
                <DialogTitle id="alert-dialog-title">
                    Reject this potential facility match?
                </DialogTitle>
                <DialogContent id="alert-dialog-description">
                    <h3>
                        This action will reject the facility as a potential
                        match.
                    </h3>
                    <p>
                        <strong>Potential matches to reject:</strong>
                    </p>
                    <ul>
                        {activeCheckboxes.map(facilityMatchToReject => (
                            <div key={facilityMatchToReject.id}>
                                <li>name: {facilityMatchToReject?.name}</li>
                                <li>
                                    address: {facilityMatchToReject?.address}
                                </li>
                                <hr color="#E7E8EA" />
                            </div>
                        ))}
                    </ul>
                    <p>
                        <strong>List item:</strong>
                    </p>
                    <ul>
                        <li>name: {listItem?.name}</li>
                        <li>address: {listItem?.address}</li>
                    </ul>
                    <p>
                        If no other potential matches remain, this will create a
                        new facility.
                    </p>
                </DialogContent>
                <DialogActions>
                    <Button
                        variant="outlined"
                        color="secondary"
                        onClick={this.closeDialog}
                    >
                        No, do not reject
                    </Button>
                    <Button
                        variant="contained"
                        color="secondary"
                        onClick={this.rejectFacilityMatch}
                    >
                        Yes, reject
                    </Button>
                </DialogActions>
            </Dialog>
        );

        return (
            <>
                <Button
                    disabled={fetching || !activeSubmitButton}
                    type="button"
                    color="secondary"
                    variant="contained"
                    onClick={() => this.openActionDialog(action)}
                >
                    {buttonName}
                </Button>
                {confirmDialog}
                {rejectDialog}
            </>
        );
    }
}

ConfirmActionButton.defaultProps = {
    fetching: false,
    activeSubmitButton: false,
};

ConfirmActionButton.propTypes = {
    activeCheckboxes: arrayOf(
        shape({
            name: string,
            address: string,
        }),
    ).isRequired,
    listItem: shape({
        name: string.isRequired,
        address: string.isRequired,
    }).isRequired,
    fetching: bool,
    activeSubmitButton: bool,
    confirmMatch: func.isRequired,
    rejectMatch: func.isRequired,
    openMergeModal: func.isRequired,
};
