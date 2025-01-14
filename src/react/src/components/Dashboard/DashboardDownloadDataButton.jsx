import React, { useEffect } from 'react';
import { arrayOf, string, func, bool } from 'prop-types';
import { toast } from 'react-toastify';
import DownloadExcelButton from './DownloadExcelButton';
import { moderationEventsListPropType } from '../../util/propTypes';

const DashboardDownloadDataButton = ({
    fetching,
    downloadPayload,
    downloadData,
    downloadError,
}) => {
    useEffect(() => {
        if (downloadError) {
            toast('A problem prevented downloading the data');
        }
    }, [downloadError]);

    const handleDownload = () => {
        downloadData(downloadPayload);
    };

    return (
        <DownloadExcelButton
            fetching={fetching}
            handleDownload={handleDownload}
        />
    );
};

DashboardDownloadDataButton.defaultProps = {
    downloadError: null,
};

DashboardDownloadDataButton.propTypes = {
    fetching: bool.isRequired,
    downloadPayload: moderationEventsListPropType.isRequired,
    downloadData: func.isRequired,
    downloadError: arrayOf(string),
};

export default DashboardDownloadDataButton;
