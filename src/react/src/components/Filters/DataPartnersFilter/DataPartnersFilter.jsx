import React, { useEffect } from 'react';
import { arrayOf, bool, func, shape, string } from 'prop-types';
import { connect } from 'react-redux';

import NestedSelect from '../NestedSelect';
import { DATA_PARTNERS, contributorOptionPropType } from './constants';

import { setPartnerContributorFilter } from '../../../actions/filters';
import { fetchPartnerGroupContributorsIfNeeded } from '../../../actions/partnerGroupContributors';
import { getPartnerGroupsWithContributors } from '../../../selectors/partnerFieldGroupsSelectors';

const DataPartnersFilter = ({
    groups,
    fetching,
    selectedContributors,
    onContributorChange,
    loadGroupsIfNeeded,
}) => {
    useEffect(() => {
        if (selectedContributors?.length) {
            loadGroupsIfNeeded();
        }
    }, [selectedContributors, loadGroupsIfNeeded]);

    return (
        <div className="form__field">
            <NestedSelect
                name={DATA_PARTNERS}
                label="Spotlight Data Partners"
                optionsData={groups}
                sectors={selectedContributors}
                updateSector={onContributorChange}
                onMenuOpen={loadGroupsIfNeeded}
                noOptionsMessage={() =>
                    fetching ? 'Loading...' : 'No options'
                }
                disabled={fetching}
                isSideBarSearch
            />
        </div>
    );
};

DataPartnersFilter.propTypes = {
    groups: arrayOf(
        shape({
            label: string.isRequired,
            options: arrayOf(contributorOptionPropType).isRequired,
        }),
    ).isRequired,
    fetching: bool.isRequired,
    selectedContributors: arrayOf(contributorOptionPropType).isRequired,
    onContributorChange: func.isRequired,
    loadGroupsIfNeeded: func.isRequired,
};

const mapStateToProps = state => ({
    groups: getPartnerGroupsWithContributors(state),
    fetching: state.partnerGroupContributors.fetching,
    selectedContributors: state.filters.partnerContributors,
});

const mapDispatchToProps = dispatch => ({
    onContributorChange: contributors =>
        dispatch(setPartnerContributorFilter(contributors)),
    loadGroupsIfNeeded: () => dispatch(fetchPartnerGroupContributorsIfNeeded()),
});

export default connect(mapStateToProps, mapDispatchToProps)(DataPartnersFilter);
