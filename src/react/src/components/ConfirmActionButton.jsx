import React, { useState, useCallback } from 'react';
import { arrayOf, bool, func, shape, string } from 'prop-types';
import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogTitle from '@material-ui/core/DialogTitle';
import { useMergeButtonClickHandler } from './../util/hooks';
import { CONFIRM_ACTION, MERGE_ACTION, REJECT_ACTION } from '../util/constants';
import COLOURS from '../util/COLOURS';

const actionDialogStates = Object.freeze({
    none: 'none',
    confirm: CONFIRM_ACTION,
    merge: MERGE_ACTION,
    reject: REJECT_ACTION,
});

const ConfirmActionButton = ({
    action,
    activeCheckboxes,
    listItem,
    fetching,
    activeSubmitButton,
    buttonName,
    confirmMatch,
    rejectMatch,
    openMergeModal,
    targetFacilityOSID,
    facilityToMergeOSID,
    updateTargetOSID,
    updateToMergeOSID,
    fetchToMergeFacility,
    fetchTargetFacility,
    resetCheckboxes,
}) => {
    const [currentDialog, setCurrentDialog] = useState(actionDialogStates.none);

    const handleMergeButtonClick = useMergeButtonClickHandler({
        targetFacilityOSID,
        facilityToMergeOSID,
        facilitiesToMergeData: activeCheckboxes,
        updateToMergeOSID,
        updateTargetOSID,
        fetchToMergeFacility,
        fetchTargetFacility,
        openMergeModal,
    });

    const openActionDialog = useCallback(() => {
        switch (action) {
            case CONFIRM_ACTION:
                setCurrentDialog(actionDialogStates.confirm);
                break;
            case MERGE_ACTION:
                handleMergeButtonClick();
                break;
            case REJECT_ACTION:
                setCurrentDialog(actionDialogStates.reject);
                break;
            default:
                break;
        }
    }, [
        action,
        activeCheckboxes,
        updateTargetOSID,
        updateToMergeOSID,
        fetchToMergeFacility,
        fetchTargetFacility,
        openMergeModal,
    ]);

    const closeDialog = useCallback(() => {
        setCurrentDialog(actionDialogStates.none);
    }, []);

    const confirmFacilityMatch = useCallback(() => {
        confirmMatch();
        resetCheckboxes();
        closeDialog();
    }, [confirmMatch, closeDialog]);

    const rejectFacilityMatch = useCallback(() => {
        rejectMatch();
        resetCheckboxes();
        closeDialog();
    }, [rejectMatch, closeDialog]);

    const confirmDialog = (
        <Dialog
            open={currentDialog === actionDialogStates.confirm}
            aria-labelledby="alert-dialog-title"
            aria-describedby="alert-dialog-description"
        >
            <DialogTitle id="alert-dialog-title">
                Confirm this potential facility match?
            </DialogTitle>
            <DialogContent>
                <h3>
                    This action will confirm this facility as a match for the
                    list item.
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
                <Button onClick={closeDialog} color="primary">
                    No, do not confirm
                </Button>
                <Button
                    onClick={confirmFacilityMatch}
                    color="primary"
                    autoFocus
                >
                    Yes, confirm
                </Button>
            </DialogActions>
        </Dialog>
    );

    const rejectDialog = (
        <Dialog
            open={currentDialog === actionDialogStates.reject}
            aria-labelledby="alert-dialog-title"
            aria-describedby="alert-dialog-description"
        >
            <DialogTitle id="alert-dialog-title">
                Reject this potential facility match?
            </DialogTitle>
            <DialogContent>
                <h3>
                    This action will reject the facility as a potential match.
                </h3>
                <p>
                    <strong>Potential matches to reject:</strong>
                </p>
                <ul>
                    {activeCheckboxes.map(facilityMatchToReject => (
                        <div key={facilityMatchToReject.id}>
                            <li>name: {facilityMatchToReject?.name}</li>
                            <li>address: {facilityMatchToReject?.address}</li>
                            <hr color={COLOURS.ACCENT_GREY} />
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
                    If no other potential matches remain, this will create a new
                    facility.
                </p>
            </DialogContent>
            <DialogActions>
                <Button onClick={closeDialog} color="primary">
                    No, do not reject
                </Button>
                <Button onClick={rejectFacilityMatch} color="primary" autoFocus>
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
                onClick={() => openActionDialog(action)}
            >
                {buttonName}
            </Button>
            {confirmDialog}
            {rejectDialog}
        </>
    );
};

ConfirmActionButton.defaultProps = {
    fetching: false,
    activeSubmitButton: false,
    action: CONFIRM_ACTION,
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
    action: string,
    fetching: bool,
    activeSubmitButton: bool,
    buttonName: string.isRequired,
    confirmMatch: func.isRequired,
    rejectMatch: func.isRequired,
    openMergeModal: func.isRequired,
    targetFacilityOSID: string.isRequired,
    facilityToMergeOSID: string.isRequired,
    updateTargetOSID: func.isRequired,
    updateToMergeOSID: func.isRequired,
    fetchToMergeFacility: func.isRequired,
    fetchTargetFacility: func.isRequired,
    resetCheckboxes: func.isRequired,
};

export default ConfirmActionButton;
