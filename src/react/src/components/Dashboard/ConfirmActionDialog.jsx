import React, { useState } from 'react';
import { EditorState, convertToRaw } from 'draft-js';
import draftToHtml from 'draftjs-to-html';
import { Editor } from 'react-draft-wysiwyg';
import 'react-draft-wysiwyg/dist/react-draft-wysiwyg.css';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    InputLabel,
    Typography,
    Button,
} from '@material-ui/core';
import { MODERATION_STATUSES_ENUM } from '../../util/constants';

const ConfirmActionDialog = ({
    updateModerationEvent,
    isOpen,
    closeDialog,
}) => {
    const [editorState, setEditorState] = useState(EditorState.createEmpty());
    // console.log('editorState >>>', editorState);

    const handleEditorChange = content => {
        // console.log('content >>>', content);
        setEditorState(content);
    };
    const contentState = editorState.getCurrentContent();
    const rawContentState = convertToRaw(contentState);
    // console.log('rawContentState >>>', rawContentState);
    const htmlContent = draftToHtml(rawContentState);
    console.log('htmlContent >>>', htmlContent);
    const cleanedText = contentState.getPlainText();
    console.log('cleanedText >>>', cleanedText);
    // console.log('typeof cleanedText >>>', typeof cleanedText);

    const handleAction = () => {
        updateModerationEvent(MODERATION_STATUSES_ENUM.REJECTED);
        // Convert the editor content to raw JSON or HTML (using a conversion library)
        // const content = convertToRaw(editorState.getCurrentContent());
        // Pass the content to your action handler
        // dialogContentData.action(content);
        // const contentString = JSON.stringify(rawContentState);
        // console.log('contentString >>>', contentString);
    };

    return (
        <Dialog
            open={isOpen}
            onClose={closeDialog}
            aria-labelledby="dialog-title"
        >
            <DialogTitle>Reject Event</DialogTitle>
            <DialogContent>
                <InputLabel htmlFor="dialog-wysiwyg">
                    <Typography variant="body2">
                        Please provide a reason for rejecting the event.
                    </Typography>
                </InputLabel>
                <div
                    id="dialog-wysiwyg"
                    style={{
                        border: '1px solid #ccc',
                        padding: '5px',
                        minHeight: '350px',
                    }}
                >
                    <Editor
                        editorState={editorState}
                        onEditorStateChange={handleEditorChange}
                        toolbar={{
                            options: [
                                'inline',
                                'blockType',
                                'list',
                                'link',
                                'history',
                            ],
                        }}
                        editorStyle={{
                            padding: '5px',
                            overflowY: 'auto',
                            maxHeight: '260px',
                        }}
                    />
                </div>
            </DialogContent>
            <DialogActions>
                <Button
                    variant="outlined"
                    color="primary"
                    onClick={closeDialog}
                >
                    Cancel
                </Button>
                <Button
                    variant="contained"
                    color="secondary"
                    onClick={handleAction}
                >
                    Reject
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default ConfirmActionDialog;
