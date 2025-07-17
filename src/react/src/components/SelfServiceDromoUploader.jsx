import React, { useState } from 'react';
import { object, func } from 'prop-types';
import DromoUploader from 'dromo-uploader-react';
import MaterialButton from '@material-ui/core/Button';
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
                Beta Self Service Upload
            </MaterialButton>

            <DromoUploader
                licenseKey="ee427cf5-da27-4f28-a260-c9a17d02ad30"
                schemaId="6f3e129c-d724-4b80-b2c9-8e54b47e8017"
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
