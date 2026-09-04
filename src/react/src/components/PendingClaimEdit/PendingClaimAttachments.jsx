import React, { useState } from 'react';
import { bool, func, number, object } from 'prop-types';
import moment from 'moment';
import Paper from '@material-ui/core/Paper';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import IconButton from '@material-ui/core/IconButton';
import DeleteIcon from '@material-ui/icons/Delete';
import Dialog from '@material-ui/core/Dialog';
import DialogTitle from '@material-ui/core/DialogTitle';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogActions from '@material-ui/core/DialogActions';
import CircularProgress from '@material-ui/core/CircularProgress';
import { withStyles } from '@material-ui/core/styles';

import { facilityClaimAttachmentsPropType } from '../../util/propTypes';
import { makeFacilityClaimAttachmentDownloadURL } from '../../util/util';

const styles = Object.freeze({
    container: Object.freeze({
        padding: '25px',
        marginTop: '20px',
        marginBottom: '20px',
    }),
    list: Object.freeze({
        listStyle: 'none',
        padding: 0,
        margin: '10px 0 0 0',
    }),
    listItem: Object.freeze({
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderBottom: '1px solid rgba(0, 0, 0, 0.08)',
        padding: '6px 0',
    }),
    uploadedAt: Object.freeze({
        color: 'rgba(0, 0, 0, 0.54)',
        marginLeft: '12px',
    }),
});

/*
 * The documents already stored on the pending claim. Download links go
 * through the authorization-checked download endpoint (the API answers
 * with a short-lived redirect); no storage URLs exist in the payload.
 */
function PendingClaimAttachments({
    classes,
    claimId,
    attachments,
    deleting,
    onDelete,
}) {
    const [attachmentToDelete, setAttachmentToDelete] = useState(null);

    const closeDialog = () => setAttachmentToDelete(null);

    const confirmDelete = () => {
        onDelete(attachmentToDelete.id);
        closeDialog();
    };

    return (
        <Paper className={classes.container}>
            <Typography variant="title">Uploaded documents</Typography>
            {attachments.length === 0 ? (
                <Typography variant="body1">
                    No documents uploaded yet.
                </Typography>
            ) : (
                <ul className={classes.list}>
                    {attachments.map(attachment => (
                        <li key={attachment.id} className={classes.listItem}>
                            <span>
                                <a
                                    href={makeFacilityClaimAttachmentDownloadURL(
                                        claimId,
                                        attachment.id,
                                    )}
                                    rel="noreferrer"
                                    target="_blank"
                                >
                                    {attachment.file_name}
                                </a>
                                <span className={classes.uploadedAt}>
                                    {moment(attachment.uploaded_at).format(
                                        'LL',
                                    )}
                                </span>
                            </span>
                            {deleting ? (
                                <CircularProgress size={20} />
                            ) : (
                                <IconButton
                                    aria-label={`Remove ${attachment.file_name}`}
                                    onClick={() =>
                                        setAttachmentToDelete(attachment)
                                    }
                                >
                                    <DeleteIcon />
                                </IconButton>
                            )}
                        </li>
                    ))}
                </ul>
            )}
            <Dialog open={attachmentToDelete !== null} onClose={closeDialog}>
                <DialogTitle>Remove this document?</DialogTitle>
                <DialogContent>
                    <DialogContentText>
                        {attachmentToDelete !== null
                            ? `${attachmentToDelete.file_name} will be removed
                               from your claim. This cannot be undone.`
                            : ''}
                    </DialogContentText>
                </DialogContent>
                <DialogActions>
                    <Button onClick={closeDialog}>Cancel</Button>
                    <Button color="secondary" onClick={confirmDelete}>
                        Remove
                    </Button>
                </DialogActions>
            </Dialog>
        </Paper>
    );
}

PendingClaimAttachments.defaultProps = {
    attachments: [],
    deleting: false,
};

PendingClaimAttachments.propTypes = {
    classes: object.isRequired,
    claimId: number.isRequired,
    attachments: facilityClaimAttachmentsPropType,
    deleting: bool,
    onDelete: func.isRequired,
};

export default withStyles(styles)(PendingClaimAttachments);
