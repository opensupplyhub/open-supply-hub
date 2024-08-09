import React from 'react';
import { bool, func } from 'prop-types';
import { connect } from 'react-redux';

import StyledSelect from './StyledSelect';

import { updateSectorFilter } from '../../actions/filters';
import {
    fetchSectorOptions,
    fetchGroupedSectorOptions,
} from '../../actions/filterOptions';

import {
    sectorOptionsPropType,
    groupedSectorOptionsPropType,
} from '../../util/propTypes';
import NestedSelect from './NestedSelect';

const SECTORS = 'SECTORS';

function SectorFilter({
    sectorOptions,
    sectors,
    updateSector,
    fetchSectors,
    fetchingSectors,
    fetchingOptions,
    hideSectorData,
    isSideBarSearch,
    embed,
    groupedSectorOptions,
    fetchingGroupedSectors,
    fetchGroupedSectors,
}) {
    if (hideSectorData) {
        return null;
    }

    return (
        <>
            <div className="form__field">
                {embed ? (
                    <StyledSelect
                        name={SECTORS}
                        label="Sector"
                        options={sectorOptions || []}
                        value={sectors}
                        onChange={updateSector}
                        onFocus={() =>
                            !sectorOptions && !fetchingSectors && fetchSectors()
                        }
                        noOptionsMessage={() =>
                            fetchingSectors ? 'Loading..' : 'No options'
                        }
                        disabled={fetchingOptions || fetchingSectors}
                        isSideBarSearch={isSideBarSearch}
                    />
                ) : (
                    <NestedSelect
                        name={SECTORS}
                        label="Sector"
                        optionsData={groupedSectorOptions || []}
                        sectors={sectors}
                        updateSector={updateSector}
                        onFocus={() =>
                            !groupedSectorOptions &&
                            !fetchingGroupedSectors &&
                            fetchGroupedSectors()
                        }
                        noOptionsMessage={() =>
                            fetchingGroupedSectors ? 'Loading..' : 'No options'
                        }
                        disabled={fetchingOptions || fetchingGroupedSectors}
                        isSideBarSearch={isSideBarSearch}
                    />
                )}
            </div>
        </>
    );
}

SectorFilter.defaultProps = {
    sectorOptions: null,
    groupedSectorOptions: null,
};

SectorFilter.propTypes = {
    sectorOptions: sectorOptionsPropType,
    updateSector: func.isRequired,
    fetchSectors: func.isRequired,
    sectors: sectorOptionsPropType.isRequired,
    fetchingSectors: bool.isRequired,
    fetchingOptions: bool.isRequired,
    embed: bool.isRequired,
    groupedSectorOptions: groupedSectorOptionsPropType,
    fetchingGroupedSectors: bool.isRequired,
    fetchGroupedSectors: func.isRequired,
};

function mapStateToProps({
    filterOptions: {
        sectors: { data: sectorOptions, fetching: fetchingSectors },
        groupedSectors: {
            data: groupedSectorOptions,
            fetching: fetchingGroupedSectors,
        },
        contributors: { fetching: fetchingContributors },
        countries: { fetching: fetchingCountries },
    },
    filters: { sectors },
    embeddedMap: { embed, config },
}) {
    return {
        sectorOptions,
        sectors,
        fetchingSectors,
        fetchingOptions: fetchingCountries || fetchingContributors,
        hideSectorData: embed ? config.hide_sector_data : false,
        embed,
        groupedSectorOptions,
        fetchingGroupedSectors,
    };
}

function mapDispatchToProps(dispatch) {
    return {
        updateSector: v => dispatch(updateSectorFilter(v)),
        fetchSectors: () => dispatch(fetchSectorOptions()),
        fetchGroupedSectors: () => dispatch(fetchGroupedSectorOptions()),
    };
}

export default connect(mapStateToProps, mapDispatchToProps)(SectorFilter);
