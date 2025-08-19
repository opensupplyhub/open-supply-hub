import React from 'react';
import { bool, number, func } from 'prop-types';
import FeatureFlag from './FeatureFlag';
import DownloadFacilitiesButton from './DownloadFacilitiesButton';
import { PRIVATE_INSTANCE, FACILITIES_DOWNLOAD_LIMIT } from '../util/constants';

function DownloadButtonWithFlags({
    embed,
    facilitiesCount,
    isSameContributor,
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
                        !isSameContributor &&
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
    isSameContributor: bool,
    userAllowedRecords: number.isRequired,
    setLoginRequiredDialogIsOpen: func.isRequired,
};

DownloadButtonWithFlags.defaultProps = {
    facilitiesCount: 0,
    isSameContributor: false,
};

export default DownloadButtonWithFlags;
