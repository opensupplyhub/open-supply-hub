import React, { useState } from 'react';
import { bool, func, object } from 'prop-types';

import ReactQuill from 'react-quill-new';
import 'react-quill-new/dist/quill.snow.css';

import { withStyles } from '@material-ui/core/styles';
import {
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    InputLabel,
    Typography,
    Tooltip,
} from '@material-ui/core';

import { MODERATION_STATUSES_ENUM } from '../../util/constants';
import { makeRejectModerationEventDialogStyles } from '../../util/styles';

const MIN_TEXT_INPUT_LENGTH = 30;

const EDITOR_TOOLBAR = [
    [
        'bold',
        'italic',
        'underline',
        'strike',
        'blockquote',
        'code-block',
        { script: 'sub' },
        { script: 'super' },
    ],
    [{ header: [1, 2, 3, 4, 5, 6, false] }, { font: [] }],
    [{ list: 'ordered' }, { list: 'bullet' }, { direction: 'rtl' }],
    ['link'],
];

const RejectModerationEventDialog = ({
    updateModerationEvent,
    isOpenDialog,
    closeDialog,
    classes,
}) => {
    const [editorContent, setEditorContent] = useState({ html: '', text: '' });
    const [isTooltipOpen, setIsTooltipOpen] = useState(false);

    const { html: htmlContent, text: cleanedText } = editorContent;

    const handleEditorChange = (content, delta, source, editor) => {
        setEditorContent({ html: content, text: editor.getText().trim() });
    };

    const handleAction = () => {
        updateModerationEvent(
            MODERATION_STATUSES_ENUM.REJECTED,
            cleanedText,
            htmlContent,
        );
        closeDialog();
    };

    const handleTooltipClose = () => {
        setIsTooltipOpen(false);
    };

    const handleTooltipOpen = () => {
        setIsTooltipOpen(true);
    };

    const isRejectDisabled =
        cleanedText.replace(/\s/g, '').length < MIN_TEXT_INPUT_LENGTH;

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
                    <ReactQuill
                        theme="snow"
                        value={htmlContent}
                        onChange={handleEditorChange}
                        className={classes.editorStyles}
                        modules={{ toolbar: EDITOR_TOOLBAR }}
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
                <Tooltip
                    title="Please provide a message with at least 30 characters."
                    placement="top"
                    open={isTooltipOpen && isRejectDisabled}
                    onClose={handleTooltipClose}
                    onOpen={handleTooltipOpen}
                >
                    <span>
                        <Button
                            variant="contained"
                            color="secondary"
                            onClick={handleAction}
                            className={classes.buttonBaseStyles}
                            disabled={isRejectDisabled}
                        >
                            Reject
                        </Button>
                    </span>
                </Tooltip>
            </DialogActions>
        </Dialog>
    );
};

RejectModerationEventDialog.propTypes = {
    updateModerationEvent: func.isRequired,
    isOpenDialog: bool.isRequired,
    closeDialog: func.isRequired,
    classes: object.isRequired,
};

export default withStyles(makeRejectModerationEventDialogStyles)(
    RejectModerationEventDialog,
);
