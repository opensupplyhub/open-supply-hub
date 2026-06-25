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

// The download button is disabled only when a search targets trade
// union-linked data *exclusively* - i.e. there is a union signal (the "Union"
// Data Contributor Type, or a union Data Contributor / its list sub-filter)
// and no non-union contributor signal. A mixed search stays downloadable; the
// backend relabels the union rows to "Other" in the CSV/XLSX.
const isUnionOnlySelected = (contributorTypes, contributors) => {
    const types = contributorTypes || [];
    const contribs = contributors || [];

    const hasUnionSignal =
        types.some(option => option.value === UNION_CONTRIBUTOR_TYPE) ||
        contribs.some(option => option.type === UNION_CONTRIBUTOR_TYPE);
    if (!hasUnionSignal) {
        return false;
    }

    const hasNonUnionSignal =
        types.some(option => option.value !== UNION_CONTRIBUTOR_TYPE) ||
        contribs.some(option => option.type !== UNION_CONTRIBUTOR_TYPE);

    return !hasNonUnionSignal;
};

function mapStateToProps({
    filters: { contributorTypes, contributors, combineContributors },
}) {
    const unionOnly =
        !combineContributors &&
        isUnionOnlySelected(contributorTypes, contributors);

    return {
        unionFilterActive: unionOnly,
    };
}

export default connect(mapStateToProps)(DownloadButtonWithFlags);
