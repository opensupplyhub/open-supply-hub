import React from 'react';
import { bool, number, func } from 'prop-types';
import FeatureFlag from './FeatureFlag';
import DownloadFacilitiesButton from './DownloadFacilitiesButton';
import { PRIVATE_INSTANCE, FACILITIES_DOWNLOAD_LIMIT } from '../util/constants';

function DownloadButtonWithFlags({
    embed,
    facilitiesCount,
    isAllUserContributed,
    userAllowedRecords,
    setLoginRequiredDialogIsOpen,
}) {
    return (
        <FeatureFlag
            flag={PRIVATE_INSTANCE}
            alternative={
                <DownloadFacilitiesButton
                    disabled={
                        embed && facilitiesCount > FACILITIES_DOWNLOAD_LIMIT
                    }
                    upgrade={
                        !embed &&
                        !isAllUserContributed &&
                        facilitiesCount > userAllowedRecords
                    }
                    userAllowedRecords={userAllowedRecords}
                    setLoginRequiredDialogIsOpen={setLoginRequiredDialogIsOpen}
                    facilitiesCount={facilitiesCount}
                />
            }
        >
            <DownloadFacilitiesButton
                disabled={facilitiesCount > FACILITIES_DOWNLOAD_LIMIT}
                userAllowedRecords={FACILITIES_DOWNLOAD_LIMIT}
                setLoginRequiredDialogIsOpen={setLoginRequiredDialogIsOpen}
            />
        </FeatureFlag>
    );
}

DownloadButtonWithFlags.propTypes = {
    embed: bool.isRequired,
    facilitiesCount: number,
    isAllUserContributed: bool,
    userAllowedRecords: number.isRequired,
    setLoginRequiredDialogIsOpen: func.isRequired,
};

DownloadButtonWithFlags.defaultProps = {
    facilitiesCount: 0,
    isAllUserContributed: false,
};

export default DownloadButtonWithFlags;
