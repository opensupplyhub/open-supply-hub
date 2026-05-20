import React, { useEffect } from 'react';
import { arrayOf, bool, func, shape, string } from 'prop-types';
import { connect } from 'react-redux';
import Checkbox from '@material-ui/core/Checkbox';
import FormControlLabel from '@material-ui/core/FormControlLabel';

import NestedSelect from './NestedSelect';
import ShowOnly from '../ShowOnly';

import {
    setPartnerContributorFilter,
    updateCombinePartnerContributorsFilterOption,
} from '../../actions/filters';
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
    combinePartnerContributors,
    onContributorChange,
    onCombinePartnerContributorsChange,
    loadGroupsIfNeeded,
}) {
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
            <ShowOnly
                when={selectedContributors && selectedContributors.length > 1}
            >
                <div style={{ marginLeft: '16px' }}>
                    <FormControlLabel
                        control={
                            <Checkbox
                                checked={!!combinePartnerContributors}
                                onChange={onCombinePartnerContributorsChange}
                                color="primary"
                                value={combinePartnerContributors}
                            />
                        }
                        label="Show only shared facilities"
                    />
                </div>
            </ShowOnly>
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
    combinePartnerContributors: string.isRequired,
    onContributorChange: func.isRequired,
    onCombinePartnerContributorsChange: func.isRequired,
    loadGroupsIfNeeded: func.isRequired,
};

const mapStateToProps = state => ({
    groups: getPartnerGroupsWithContributors(state),
    fetching: state.partnerGroupContributors.fetching,
    selectedContributors: state.filters.partnerContributors,
    combinePartnerContributors: state.filters.combinePartnerContributors,
});

const mapDispatchToProps = dispatch => ({
    onContributorChange: contributors => {
        if (!contributors || contributors.length < 2) {
            dispatch(updateCombinePartnerContributorsFilterOption(''));
        }
        dispatch(setPartnerContributorFilter(contributors));
    },
    onCombinePartnerContributorsChange: e =>
        dispatch(
            updateCombinePartnerContributorsFilterOption(
                e.target.checked ? 'AND' : '',
            ),
        ),
    loadGroupsIfNeeded: () => dispatch(fetchPartnerGroupContributorsIfNeeded()),
});

export default connect(mapStateToProps, mapDispatchToProps)(DataPartnersFilter);
