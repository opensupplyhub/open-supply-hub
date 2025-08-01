import React, { useState } from 'react';
import { object, func } from 'prop-types';
import DromoUploader from 'dromo-uploader-react';
import MaterialButton from '@material-ui/core/Button';

import env from '../util/env';
import { processDromoResults } from '../util/util';

const uploaderButtonStyle = Object.freeze({
    backgroundColor: '#62CC74',
    color: 'white',
});

const SelfServiceDromoUploader = ({ fileInput, updateFileName }) => {
    const [isUploaderOpen, setIsUploaderOpen] = useState(false);

    const openUploader = () => setIsUploaderOpen(true);
    const closeUploader = () => setIsUploaderOpen(false);

    const handleDromoResults = (results, metadata) => {
        const { filename } = metadata;

        processDromoResults(results, filename, fileInput, updateFileName);
        closeUploader();
    };

    return (
        <>
            <MaterialButton
                onClick={openUploader}
                type="button"
                variant="contained"
                style={uploaderButtonStyle}
                disableRipple
            >
                SMART UPLOAD (BETA)
            </MaterialButton>

            <DromoUploader
                licenseKey={env('REACT_APP_DROMO_LICENSE_KEY')}
                schemaId={env('REACT_APP_DROMO_SCHEMA_ID')}
                open={isUploaderOpen}
                onCancel={closeUploader}
                onResults={handleDromoResults}
            />
        </>
    );
};

SelfServiceDromoUploader.propTypes = {
    fileInput: object.isRequired,
    updateFileName: func.isRequired,
};

export default SelfServiceDromoUploader;
