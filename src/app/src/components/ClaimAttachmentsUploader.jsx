// TODO: remove this eslint comment later
/* eslint no-unused-vars: 0 */
import React, { useState, useRef } from 'react';
import { connect } from 'react-redux';
import SvgIcon from '@material-ui/core/SvgIcon';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';

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
});

const ClaimAttachmentsUploader = () => {
    const [files, setFiles] = useState([]);
    const fileInputRef = useRef(null);

    const handleDrop = e => {
        e.preventDefault();
        const newFiles = Array.from(e.dataTransfer.files);
        setFiles([...files, ...newFiles]);
    };

    const handleFileChange = e => {
        const newFiles = Array.from(e.target.files);
        setFiles([...files, ...newFiles]);
    };

    const handleRemoveFile = index => {
        const updatedFiles = files.filter((file, i) => i !== index);
        setFiles(updatedFiles);
    };

    return (
        <>
            <ul style={claimAttachmentsUploaderStyles.fileListUploaded}>
                {files.map((file, index) => (
                    <li key={Math.floor(Math.random() * 1000 + Date.now())}>
                        <IconButton
                            key="remove"
                            aria-label="Remove"
                            onClick={() => handleRemoveFile(index)}
                            style={
                                claimAttachmentsUploaderStyles.removeFileIcon
                            }
                        >
                            <CloseIcon />
                        </IconButton>
                        {file.name}{' '}
                    </li>
                ))}
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
                    accept=".jpg,.jpeg,.png,.pdf"
                    onChange={handleFileChange}
                    multiple
                    style={claimAttachmentsUploaderStyles.fileInputHidden}
                    ref={fileInputRef}
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
        </>
    );
};

// TODO: proceed with refactoring
/*
function mapDispatchToProps(dispatch) {
    return {
        updateUploadFiles: e =>
            dispatch(updateClaimAFacilityUploadFiles(getValueFromEvent(e))),
    };
}
*/

export default connect(null, null)(ClaimAttachmentsUploader);
