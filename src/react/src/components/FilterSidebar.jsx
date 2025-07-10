import React, { useEffect, useRef, useState } from 'react';
import { bool, func, arrayOf, string } from 'prop-types';
import { connect } from 'react-redux';
import {
    Grid,
    Hidden,
    IconButton,
    Modal,
    Tab,
    Tabs,
    withStyles,
    withTheme,
} from '@material-ui/core';
import CircularProgress from '@material-ui/core/CircularProgress';
import CloseIcon from '@material-ui/icons/Close';
import get from 'lodash/get';

import Button from './Button';
import FilterIcon from './FilterIcon';
import FeatureFlag from './FeatureFlag';
import FilterSidebarSearchTab from './FilterSidebarSearchTab';
import FilterSidebarFacilitiesTab from './FilterSidebarFacilitiesTab';
import MapWithHookedHeight from './MapWithHookedHeight';
import NonVectorTileFilterSidebarFacilitiesTab from './NonVectorTileFilterSidebarFacilitiesTab';
import MergeModal from './MergeModal';
import FilterSidebarHeader from './FilterSidebarHeader';

import { VECTOR_TILE } from '../util/constants';

import { setSidebarTabActive, toggleFilterModal } from '../actions/ui';
import { resetMergeFacilitiesState } from '../actions/mergeFacilities';
import {
    fetchContributorOptions,
    fetchListOptions,
    fetchCountryOptions,
    fetchAllPrimaryFilterOptions,
} from '../actions/filterOptions';
import { fetchFacilities } from '../actions/facilities';

import {
    contributorOptionsPropType,
    countryOptionsPropType,
    sectorOptionsPropType,
} from '../util/propTypes';

import { allListsAreEmpty } from '../util/util';
import MapIcon from './MapIcon';
import FacilitiesIcon from './FacilitiesIcon';

const filterSidebarStyles = theme =>
    Object.freeze({
        filterDrawer: {
            backgroundColor: '#fff',
            height: '100%',
        },
        filterDrawerContents: {
            alignItems: 'center',
            paddingLeft: '1em',
            paddingRight: '1em',
            display: 'flex',
            justifyContent: 'space-between',
        },
        filterDrawerHeader: {
            fontFamily: theme.typography.fontFamily,
        },
        filterButton: {
            backgroundColor: theme.palette.action.main,
            '&:hover': {
                backgroundColor: theme.palette.action.dark,
            },
            color: theme.palette.secondary.contrastText,
            fontWeight: 900,
        },
        tab: {
            backgroundColor: theme.palette.secondary.main,
            color: theme.palette.secondary.contrastText,
            borderColor: '#000',
            borderStyle: 'solid',
            borderWidth: 1,
            fontWeight: 800,
        },
        searchContainer: {
            minWidth: '200px',
        },
        resultsContainer: {
            [theme.breakpoints.up('sm')]: {
                minWidth: '250px',
            },
            [theme.breakpoints.up('md')]: {
                minWidth: '320px',
            },
        },
    });

const FilterSidebar = ({
    activeFilterSidebarTab,
    filterModalOpen,
    contributorsData,
    countriesData,
    sectorsData,
    fetchingFeatureFlags,
    contributors,
    facilitiesCount,
    merging,
    mergeError,
    toggleFilter,
    setTabActive,
    fetchFilterOptions,
    fetchContributors,
    fetchLists,
    fetchCountries,
    resetMergeState,
    refreshSearchResultsAfterMerge,
    theme,
    classes,
}) => {
    /* eslint-disable react-hooks/exhaustive-deps */
    useEffect(() => {
        if (allListsAreEmpty(contributorsData, countriesData, sectorsData)) {
            fetchFilterOptions();
        }

        if (!contributorsData) {
            fetchContributors();
        }

        if (!countriesData) {
            fetchCountries();
        }

        if (contributors && contributors.length) {
            fetchLists();
        }

        return resetMergeState;
    }, []);
    /* eslint-disable react-hooks/exhaustive-deps */

    const isFirstRender = useRef(true);
    useEffect(() => {
        if (isFirstRender.current) {
            isFirstRender.current = false;
        } else {
            fetchLists();
        }
    }, [contributors]);

    const [mergingFacilities, setMergingFacilities] = useState(false);
    useEffect(() => {
        if (merging) {
            setMergingFacilities(true);
        }

        if (!merging && mergingFacilities) {
            setMergingFacilities(false);

            if (!mergeError) {
                refreshSearchResultsAfterMerge();
            }
        }
    }, [
        merging,
        mergingFacilities,
        mergeError,
        refreshSearchResultsAfterMerge,
    ]);

    const actionContrastText = theme.palette.getContrastText(
        theme.palette.action.main,
    );
    const tabContrastText = theme.palette.secondary.contrastText;

    const renderHeader = (multiLine = false) =>
        facilitiesCount > 0 && <FilterSidebarHeader multiLine={multiLine} />;

    if (fetchingFeatureFlags) {
        return <CircularProgress />;
    }

    return (
        <>
            <Hidden smUp>
                <Grid
                    item
                    style={{
                        alignItems: 'center',
                        display: 'flex',
                        width: '100%',
                        flexDirection: 'column',
                    }}
                >
                    <Tabs
                        value={activeFilterSidebarTab}
                        onChange={(_, v) => {
                            setTabActive(v);
                        }}
                        classes={{
                            root: 'tabs results-height-subtract',
                            indicator: 'tabs-indicator-color',
                        }}
                    >
                        <Tab
                            label={
                                <div
                                    style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                    }}
                                >
                                    <FacilitiesIcon
                                        color={
                                            activeFilterSidebarTab === 0 &&
                                            tabContrastText
                                        }
                                    />
                                    LIST
                                </div>
                            }
                            className={classes.tab}
                            style={
                                activeFilterSidebarTab === 0
                                    ? {
                                          // omit shared border
                                          borderRightWidth: 0,
                                      }
                                    : {
                                          backgroundColor: '#fff',
                                          color: '#000',
                                          // omit shared border
                                          borderRightWidth: 0,
                                      }
                            }
                        />
                        <Tab
                            label={
                                <div
                                    style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                    }}
                                >
                                    <MapIcon
                                        color={
                                            activeFilterSidebarTab === 1 &&
                                            tabContrastText
                                        }
                                    />
                                    MAP
                                </div>
                            }
                            className={classes.tab}
                            style={
                                activeFilterSidebarTab === 1
                                    ? {}
                                    : {
                                          backgroundColor: '#fff',
                                          color: '#000',
                                      }
                            }
                        />
                        <div style={{ padding: '10px' }} />
                        <Button
                            Icon={FilterIcon}
                            color={actionContrastText}
                            onClick={() => toggleFilter(true)}
                            className={classes.filterButton}
                            text="FILTERS"
                        />
                    </Tabs>
                    {activeFilterSidebarTab === 0 && (
                        <Grid item sm={12}>
                            {renderHeader(true)}

                            <FeatureFlag
                                flag={VECTOR_TILE}
                                alternative={
                                    <NonVectorTileFilterSidebarFacilitiesTab />
                                }
                            >
                                <FilterSidebarFacilitiesTab />
                            </FeatureFlag>
                        </Grid>
                    )}
                    {activeFilterSidebarTab === 1 && (
                        <div
                            style={{
                                height: '100%',
                                marginTop: '1em',
                                width: '100%',
                            }}
                        >
                            <MapWithHookedHeight />
                        </div>
                    )}
                </Grid>
            </Hidden>
            <Hidden only="xs">
                <Grid item sm={3} className={classes.searchContainer}>
                    <FilterSidebarSearchTab />
                </Grid>
            </Hidden>
            <Hidden only="xs">
                <Grid item xs={12} sm={4} className={classes.resultsContainer}>
                    {renderHeader()}
                    <FeatureFlag
                        flag={VECTOR_TILE}
                        alternative={
                            <NonVectorTileFilterSidebarFacilitiesTab />
                        }
                    >
                        <FilterSidebarFacilitiesTab />
                    </FeatureFlag>
                </Grid>
            </Hidden>
            <Modal open={filterModalOpen} onClose={() => toggleFilter(false)}>
                <div className={classes.filterDrawer}>
                    <div className={classes.filterDrawerContents}>
                        <h1 className={classes.filterDrawerHeader}>Filters</h1>
                        <IconButton onClick={() => toggleFilter(false)}>
                            <CloseIcon />
                        </IconButton>
                    </div>
                    <FilterSidebarSearchTab />
                </div>
            </Modal>
            <MergeModal />
        </>
    );
};
FilterSidebar.defaultProps = {
    contributorsData: null,
    countriesData: null,
    sectorsData: null,
    mergeError: null,
};

FilterSidebar.propTypes = {
    fetchFilterOptions: func.isRequired,
    fetchContributors: func.isRequired,
    fetchCountries: func.isRequired,
    contributorsData: contributorOptionsPropType,
    countriesData: countryOptionsPropType,
    sectorsData: sectorOptionsPropType,
    fetchingFeatureFlags: bool.isRequired,
    merging: bool.isRequired,
    mergeError: arrayOf(string),
    resetMergeState: func.isRequired,
    refreshSearchResultsAfterMerge: func.isRequired,
};

function mapStateToProps({
    ui: { activeFilterSidebarTab, filterModalOpen },
    filterOptions: {
        contributors: { data: contributorsData },
        countries: { data: countriesData },
        sectors: { data: sectorsData },
    },
    featureFlags: { fetching: fetchingFeatureFlags },
    filters: { contributors },
    facilities: {
        facilities: { data: facilities },
    },
    mergeFacilities: {
        merge: { fetching: merging, error: mergeError },
    },
}) {
    return {
        activeFilterSidebarTab,
        filterModalOpen,
        contributorsData,
        countriesData,
        sectorsData,
        fetchingFeatureFlags,
        contributors,
        facilitiesCount: get(facilities, 'count', null),
        merging,
        mergeError,
    };
}

function mapDispatchToProps(dispatch, { history: { push } }) {
    return {
        toggleFilter: () => dispatch(toggleFilterModal()),
        setTabActive: value => dispatch(setSidebarTabActive(value)),
        fetchFilterOptions: () => dispatch(fetchAllPrimaryFilterOptions()),
        fetchContributors: () => dispatch(fetchContributorOptions()),
        fetchLists: () => dispatch(fetchListOptions()),
        fetchCountries: () => dispatch(fetchCountryOptions()),
        refreshSearchResultsAfterMerge: () =>
            dispatch(fetchFacilities({ pushNewRoute: push })),
        resetMergeState: () => dispatch(resetMergeFacilitiesState()),
    };
}

export default withTheme()(
    withStyles(filterSidebarStyles)(
        connect(mapStateToProps, mapDispatchToProps)(FilterSidebar),
    ),
);
