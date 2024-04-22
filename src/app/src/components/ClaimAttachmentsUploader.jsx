import React, { useState, useRef } from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';
import { v4 as uuidv4 } from 'uuid';

import Typography from '@material-ui/core/Typography';
import SvgIcon from '@material-ui/core/SvgIcon';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';

import { updateClaimAFacilityUploadFiles } from '../actions/claimFacility';

const claimAttachmentsUploaderStyles = Object.freeze({
    fileUploadArea: Object.freeze({
        display: 'block',
        padding: '50px 0',
        background: 'rgb(240, 250, 242)',
        border: '2px dashed rgb(129, 214, 144)',
        textAlign: 'center',
        cursor: 'pointer',
        width: '95%',
    }),
    fileInputHidden: Object.freeze({
        display: 'none',
        visibility: 'hidden',
    }),
    uploadFileIcon: Object.freeze({
        fontSize: '35px',
    }),
    primary: Object.freeze({
        fontSize: '20px',
        fontWeight: 700,
    }),
    secondary: Object.freeze({
        margin: '0 auto',
    }),
    fileListUploaded: Object.freeze({
        listStyle: 'none',
        paddingLeft: 0,
    }),
    removeFileIcon: Object.freeze({
        fontSize: '8px',
        color: 'rgb(74, 153, 87)',
        marginRight: '5px',
    }),
    validationMessageStyles: Object.freeze({
        padding: '5px 0',
    }),
});

const ClaimAttachmentsUploader = ({ uploadFiles, updateUploadFiles }) => {
    const [errorMessage, setErrorMessage] = useState();
    const fileInputRef = useRef(null);

    const allowedExtensions = ['.jpg', '.jpeg', '.png', '.pdf'];
    const allowedFileSize = 5 * 1024 * 1024; // 5 MB
    const allowedFileAmount = 10;

    const getValidFiles = newFiles =>
        newFiles.filter(file => {
            const fileName = file.name;
            const extension = fileName.split('.').pop().toLowerCase();
            if (!allowedExtensions.includes(`.${extension}`)) {
                setErrorMessage(
                    `${fileName} could not be uploaded because it is not in a supported format.`,
                );
                return null;
            }
            if (file.size > allowedFileSize) {
                setErrorMessage(
                    `${fileName} could not be uploaded because it exceeds the maximum file size of 5MB.`,
                );
                return null;
            }
            if (uploadFiles.length + newFiles.length > allowedFileAmount) {
                setErrorMessage(
                    `${fileName} could not be uploaded because there is a maximum of ${allowedFileAmount} attachments and you have already uploaded ${allowedFileAmount} attachments.`,
                );
                return null;
            }
            return allowedExtensions.includes(`.${extension}`);
        });

    const handleDrop = e => {
        e.preventDefault();
        setErrorMessage('');
        const newFiles = Array.from(e.dataTransfer.files);
        updateUploadFiles([...uploadFiles, ...getValidFiles(newFiles)]);
    };

    const handleFileChange = e => {
        setErrorMessage('');
        const newFiles = Array.from(e.target.files);
        updateUploadFiles([...uploadFiles, ...getValidFiles(newFiles)]);
    };

    const handleRemoveFile = index => {
        const updatedFiles = uploadFiles.filter((file, i) => i !== index);
        updateUploadFiles(updatedFiles);
    };

    return (
        <div data-testid="claim-attachments-uploader">
            <ul style={claimAttachmentsUploaderStyles.fileListUploaded}>
                {uploadFiles.map((file, index) => (
                    <li key={uuidv4()}>
                        <IconButton
                            key="remove"
                            aria-label="Remove"
                            onClick={() => handleRemoveFile(index)}
                            style={
                                claimAttachmentsUploaderStyles.removeFileIcon
                            }
                            data-testid="claim-attachments-uploader-remove"
                        >
                            <CloseIcon />
                        </IconButton>
                        <a
                            href={URL.createObjectURL(file)}
                            rel="noreferrer"
                            target="_blank"
                        >
                            {file.name}
                        </a>
                    </li>
                ))}
                {errorMessage ? (
                    <Typography
                        variant="body2"
                        style={
                            claimAttachmentsUploaderStyles.validationMessageStyles
                        }
                        color="error"
                    >
                        {errorMessage}
                    </Typography>
                ) : null}
            </ul>
            <label
                style={claimAttachmentsUploaderStyles.fileUploadArea}
                onDrop={handleDrop}
                onDragOver={e => e.preventDefault()}
                htmlFor="fileInput"
            >
                <input
                    id="fileInput"
                    type="file"
                    accept={allowedExtensions.map(ext => ext).join(',')}
                    onChange={handleFileChange}
                    multiple
                    style={claimAttachmentsUploaderStyles.fileInputHidden}
                    ref={fileInputRef}
                    data-testid="claim-attachments-uploader-input"
                />
                <SvgIcon style={claimAttachmentsUploaderStyles.uploadFileIcon}>
                    <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8zm4 18H6V4h7v5h5zM8 15.01l1.41 1.41L11 14.84V19h2v-4.16l1.59 1.59L16 15.01 12.01 11z" />
                </SvgIcon>
                <p style={claimAttachmentsUploaderStyles.primary}>
                    Select a PNG, JPG, or PDf to upload
                </p>
                <p style={claimAttachmentsUploaderStyles.secondary}>
                    Or drag and drop files here
                </p>
                <p style={claimAttachmentsUploaderStyles.secondary}>
                    File size must be 5 MB or less; 10 files maximum
                </p>
            </label>
        </div>
    );
};

ClaimAttachmentsUploader.defaultProps = {
    uploadFiles: [],
};

ClaimAttachmentsUploader.propTypes = {
    uploadFiles: PropTypes.arrayOf(PropTypes.object),
    updateUploadFiles: PropTypes.func.isRequired,
};

function mapStateToProps({
    claimFacility: {
        claimData: {
            formData: { uploadFiles },
        },
    },
}) {
    return {
        uploadFiles,
    };
}

function mapDispatchToProps(dispatch) {
    return {
        updateUploadFiles: files =>
            dispatch(updateClaimAFacilityUploadFiles(files)),
    };
}

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(ClaimAttachmentsUploader);
