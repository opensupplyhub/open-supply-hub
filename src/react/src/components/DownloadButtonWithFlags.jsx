import React from 'react';
import { bool, number, func } from 'prop-types';
import { connect } from 'react-redux';
import FeatureFlag from './FeatureFlag';
import DownloadFacilitiesButton from './DownloadFacilitiesButton';
import {
    PRIVATE_INSTANCE,
    FACILITIES_DOWNLOAD_LIMIT,
    UNION_CONTRIBUTOR_TYPE,
} from '../util/constants';

function DownloadButtonWithFlags({
    embed,
    facilitiesCount,
    isSameContributor,
    userAllowedRecords,
    setLoginRequiredDialogIsOpen,
    unionFilterActive,
}) {
    const count = facilitiesCount == null ? 0 : facilitiesCount;

    return (
        <FeatureFlag
            flag={PRIVATE_INSTANCE}
            alternative={
                <DownloadFacilitiesButton
                    disabled={
                        unionFilterActive ||
                        (embed && count > FACILITIES_DOWNLOAD_LIMIT)
                    }
                    upgrade={
                        !embed &&
                        !isSameContributor &&
                        count > userAllowedRecords
                    }
                    userAllowedRecords={userAllowedRecords}
                    setLoginRequiredDialogIsOpen={setLoginRequiredDialogIsOpen}
                    facilitiesCount={count}
                    isSameContributor={isSameContributor}
                    unionFilterActive={unionFilterActive}
                />
            }
        >
            <DownloadFacilitiesButton
                disabled={
                    unionFilterActive || count > FACILITIES_DOWNLOAD_LIMIT
                }
                userAllowedRecords={FACILITIES_DOWNLOAD_LIMIT}
                setLoginRequiredDialogIsOpen={setLoginRequiredDialogIsOpen}
                facilitiesCount={count}
                isSameContributor={isSameContributor}
                unionFilterActive={unionFilterActive}
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
    unionFilterActive: bool,
};

DownloadButtonWithFlags.defaultProps = {
    facilitiesCount: 0,
    isSameContributor: false,
    unionFilterActive: false,
};

// A search targets trade union-linked data - and so cannot be downloaded -
// when the "Union" Data Contributor Type is selected, or when any selected
// Data Contributor is a union. The Contributor List sub-filter is covered
// transitively, since a list can only be picked while its contributor is
// selected.
const isUnionSelected = (contributorTypes, contributors) => {
    const unionTypeSelected = (contributorTypes || []).some(
        option => option.value === UNION_CONTRIBUTOR_TYPE,
    );
    const unionContributorSelected = (contributors || []).some(
        option => option.type === UNION_CONTRIBUTOR_TYPE,
    );
    return unionTypeSelected || unionContributorSelected;
};

function mapStateToProps({ filters: { contributorTypes, contributors } }) {
    return {
        unionFilterActive: isUnionSelected(contributorTypes, contributors),
    };
}

export default connect(mapStateToProps)(DownloadButtonWithFlags);
