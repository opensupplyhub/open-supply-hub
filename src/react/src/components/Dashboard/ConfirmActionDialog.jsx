import React, { useState, useMemo } from 'react';
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

    const { cleanedText, htmlContent } = useMemo(() => {
        const contentState = editorState.getCurrentContent();
        return {
            cleanedText: contentState.getPlainText(),
            htmlContent: draftToHtml(convertToRaw(contentState)),
        };
    }, [editorState]);

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
            <DialogTitle>Reject this Moderation Event?</DialogTitle>
            <DialogContent>
                <InputLabel htmlFor="dialog-wysiwyg">
                    <Typography variant="body2">
                        Keep the instructions brief and action orientated.
                        (Suggested opening, &quot;Just a few fixes are
                        needed.&quot;)
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
