import React, { useState } from 'react';
import { bool, func, object } from 'prop-types';

import { EditorState, convertToRaw } from 'draft-js';
import draftToHtml from 'draftjs-to-html';
import { Editor } from 'react-draft-wysiwyg';
import 'react-draft-wysiwyg/dist/react-draft-wysiwyg.css';

import { withStyles } from '@material-ui/core/styles';
import {
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    InputLabel,
    Typography,
} from '@material-ui/core';

import { MODERATION_STATUSES_ENUM } from '../../util/constants';
import { makeConfirmActionDialogStyles } from '../../util/styles';

const ConfirmActionDialog = ({
    updateModerationEvent,
    isOpenDialog,
    closeDialog,
    classes,
}) => {
    const [editorState, setEditorState] = useState(EditorState.createEmpty());

    const contentState = editorState.getCurrentContent();
    const rawContentState = convertToRaw(contentState);
    const htmlContent = draftToHtml(rawContentState);
    const cleanedText = contentState.getPlainText();

    const handleEditorChange = content => {
        setEditorState(content);
    };

    const handleAction = () => {
        updateModerationEvent(
            MODERATION_STATUSES_ENUM.REJECTED,
            cleanedText,
            htmlContent,
        );
        closeDialog();
    };

    return (
        <Dialog
            open={isOpenDialog}
            onClose={closeDialog}
            aria-labelledby="contribution-action-dialog-title"
            aria-describedby="contribution-action-dialog-description"
            classes={{
                paper: classes.dialogPaperStyles,
            }}
        >
            <DialogTitle>Reject this contribution record?</DialogTitle>
            <DialogContent>
                <InputLabel htmlFor="dialog-wysiwyg">
                    <Typography variant="body2">
                        Enter a reason. (This will be emailed to the person who
                        submitted the contribution.)
                    </Typography>
                </InputLabel>
                <div
                    id="dialog-wysiwyg"
                    className={classes.editorContainerStyles}
                >
                    <Editor
                        editorState={editorState}
                        onEditorStateChange={handleEditorChange}
                        editorClassName={classes.editorStyles}
                        toolbar={{
                            options: [
                                'inline',
                                'blockType',
                                'list',
                                'link',
                                'history',
                            ],
                        }}
                    />
                </div>
            </DialogContent>
            <DialogActions className={classes.dialogActionsStyles}>
                <Button
                    variant="outlined"
                    color="primary"
                    onClick={closeDialog}
                    className={classes.buttonBaseStyles}
                >
                    Cancel
                </Button>
                <Button
                    variant="contained"
                    color="secondary"
                    onClick={handleAction}
                    className={classes.buttonBaseStyles}
                >
                    Reject
                </Button>
            </DialogActions>
        </Dialog>
    );
};

ConfirmActionDialog.propTypes = {
    updateModerationEvent: func.isRequired,
    isOpenDialog: bool.isRequired,
    closeDialog: func.isRequired,
    classes: object.isRequired,
};

export default withStyles(makeConfirmActionDialogStyles)(ConfirmActionDialog);
