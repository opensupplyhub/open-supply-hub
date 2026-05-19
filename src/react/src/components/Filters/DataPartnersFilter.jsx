import React from 'react';
import { arrayOf, bool, func, shape, string } from 'prop-types';
import { connect } from 'react-redux';

import NestedSelect from './NestedSelect';

import { setPartnerContributorFilter } from '../../actions/filters';
import { fetchPartnerGroupContributorsIfNeeded } from '../../actions/partnerGroupContributors';
import { getPartnerGroupsWithContributors } from '../../selectors/partnerFieldGroupsSelectors';

const DATA_PARTNERS = 'DATA_PARTNERS';

const contributorOptionPropType = shape({
    groupLabel: string.isRequired,
    label: string.isRequired,
    value: string.isRequired,
});

function DataPartnersFilter({
    groups,
    fetching,
    selectedContributors,
    onContributorChange,
    loadGroupsIfNeeded,
}) {
    return (
        <div className="form__field">
            <NestedSelect
                name={DATA_PARTNERS}
                label="Data Partners"
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
}

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
