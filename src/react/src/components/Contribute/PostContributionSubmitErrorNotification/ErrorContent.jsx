import React from 'react';
import { object, node, string, oneOfType } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';
import { CopyToClipboard } from 'react-copy-to-clipboard';
import { toast } from 'react-toastify';
import ContentCopyIcon from '../../ContentCopyIcon';

import { errorContentStyles } from './styles';

const ErrorContent = ({
    title,
    supportInstructions,
    rawErrorData,
    children,
    classes,
}) => {
    const stringifiedRawErrorData = JSON.stringify(rawErrorData, null, 2);

    return (
        <>
            <Typography variant="subheading" className={classes.title}>
                {title}
            </Typography>
            {children}
            <Typography>{supportInstructions}</Typography>
            {rawErrorData && (
                <>
                    <TextField
                        multiline
                        rows={3}
                        fullWidth
                        variant="filled"
                        value={stringifiedRawErrorData}
                        InputProps={{
                            readOnly: true,
                            classes: {
                                root: classes.rawErrorDataContentWrapper,
                            },
                        }}
                        className={classes.rawErrorDataContainer}
                    />
                    <CopyToClipboard
                        text={stringifiedRawErrorData}
                        onCopy={() => toast('Copied error data to clipboard')}
                    >
                        <Button variant="outlined">
                            <ContentCopyIcon />
                            <span className={classes.buttonText}>
                                Copy Error Data
                            </span>
                        </Button>
                    </CopyToClipboard>
                </>
            )}
        </>
    );
};

ErrorContent.propTypes = {
    title: string.isRequired,
    supportInstructions: string.isRequired,
    rawErrorData: oneOfType([object, string]).isRequired,
    children: node.isRequired,
    classes: object.isRequired,
};

export default withStyles(errorContentStyles)(ErrorContent);
