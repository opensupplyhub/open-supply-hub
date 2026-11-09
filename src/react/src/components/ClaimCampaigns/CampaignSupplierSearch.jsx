import React, { useEffect, useRef, useState } from 'react';
import { func, instanceOf, object } from 'prop-types';
import { connect } from 'react-redux';
import { withStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import CircularProgress from '@material-ui/core/CircularProgress';
import InputLabel from '@material-ui/core/InputLabel';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';

import ContributorFilter from '../Filters/ContributorFilter';
import CountryNameFilter from '../Filters/CountryNameFilter';
import SectorFilter from '../Filters/SectorFilter';
import StyledSelect from '../Filters/StyledSelect';
import ProcessingTypeSearch from '../Filters/ProcessingTypeSearch';
import {
    updateFacilityFreeTextQueryFilter,
    updateFacilityTypeFilter,
    updateParentCompanyFilter,
    updateProcessingTypeFilter,
} from '../../actions/filters';
import {
    fetchAllPrimaryFilterOptionsIfNeeded,
    fetchFacilityProcessingTypeOptions,
    fetchProcessingTypeSuggestions,
} from '../../actions/filterOptions';
import apiRequest from '../../util/apiRequest';
import { makeClaimCampaignSearchURL } from '../../util/constants';
import {
    createQueryStringFromSearchFilters,
    mapFacilityTypeOptions,
} from '../../util/util';
import { campaignSupplierSearchStyles } from './styles';

export const SEARCH_STATUS_LABELS = Object.freeze({
    claimed: 'Claimed',
    pending: 'Pending review',
    unclaimed: 'Not started',
});

// The filters offered here. Only these go into the search, so a filter
// set on the map but not shown here (e.g. number of workers) can't
// narrow the results without the brand seeing it.
const pickCampaignFilters = filters => ({
    facilityFreeTextQuery: filters.facilityFreeTextQuery,
    countries: filters.countries,
    contributors: filters.contributors,
    combineContributors: filters.combineContributors,
    sectors: filters.sectors,
    facilityType: filters.facilityType,
    processingType: filters.processingType,
    parentCompany: filters.parentCompany,
});

const searchErrorMessage = error => {
    const data = error && error.response && error.response.data;
    if (data && data.detail) {
        return data.detail;
    }
    return 'An error prevented the search. Please try again.';
};

// Lets a brand find suppliers with the same filters as the public OS Hub
// search, including facilities it didn't contribute, and add them to the
// campaign all at once or one by one. The filters share their state with
// the map search, like the rest of the site.
export const CampaignSupplierSearch = ({
    classes,
    filters,
    filterOptions,
    getFilters,
    picked,
    onAdd,
    fetchFilterOptions,
    updateFilter,
    fetchSuggestionsForProcessingType,
}) => {
    const [searching, setSearching] = useState(false);
    const [results, setResults] = useState(null);
    const [error, setError] = useState(null);
    const processingTypeRef = useRef(null);

    useEffect(() => {
        fetchFilterOptions();
    }, [fetchFilterOptions]);

    const runSearch = () => {
        // Like the site search: save any processing type still being
        // typed, and stop if it isn't valid.
        const pendingQueryIsValid = processingTypeRef.current?.commitPendingQuery?.();
        if (pendingQueryIsValid === false) {
            return;
        }
        const queryString = createQueryStringFromSearchFilters(
            pickCampaignFilters(getFilters()),
        );
        if (!queryString) {
            setError('Add at least one search filter.');
            return;
        }
        setSearching(true);
        setError(null);
        apiRequest
            .get(makeClaimCampaignSearchURL(queryString))
            .then(({ data }) => setResults(data))
            .catch(err => {
                setResults(null);
                setError(searchErrorMessage(err));
            })
            .finally(() => setSearching(false));
    };

    const canAdd = s => s.claim_status !== 'claimed';
    const addable = results
        ? results.suppliers.filter(s => canAdd(s) && !picked.has(s.os_id))
        : [];

    return (
        <div>
            <div className={classes.filters}>
                <div className="form__field">
                    <InputLabel
                        shrink={false}
                        htmlFor="campaign-search-text"
                        className={classes.fieldLabel}
                    >
                        Facility Name or OS ID
                    </InputLabel>
                    <TextField
                        id="campaign-search-text"
                        variant="outlined"
                        placeholder="e.g. ABC Textiles Limited"
                        value={filters.facilityFreeTextQuery || ''}
                        onChange={e =>
                            updateFilter(
                                updateFacilityFreeTextQueryFilter,
                                e.target.value,
                            )
                        }
                        onKeyPress={e => e.key === 'Enter' && runSearch()}
                        fullWidth
                        InputProps={{
                            classes: {
                                root: classes.textRoot,
                                input: classes.textInput,
                                notchedOutline: classes.textOutline,
                            },
                        }}
                    />
                </div>
                <div>
                    <CountryNameFilter />
                </div>
                <div>
                    <ContributorFilter />
                </div>
                <div>
                    <SectorFilter />
                </div>
                <div className="form__field">
                    <StyledSelect
                        label="Facility Type"
                        name="FACILITY_TYPE"
                        options={mapFacilityTypeOptions(
                            filterOptions.facilityProcessingType || [],
                            [],
                        )}
                        value={filters.facilityType}
                        onChange={v =>
                            updateFilter(updateFacilityTypeFilter, v)
                        }
                    />
                </div>
                <div className="form__field">
                    <StyledSelect
                        creatable
                        label="Parent Company"
                        name="PARENT_COMPANY"
                        value={filters.parentCompany}
                        onChange={v =>
                            updateFilter(updateParentCompanyFilter, v)
                        }
                        placeholder="e.g. ABC Textiles Limited"
                        aria-label="Parent company"
                    />
                </div>
                <div className="form__field">
                    <ProcessingTypeSearch
                        processingTypeSearchRef={processingTypeRef}
                        label="Processing Type"
                        placeholder="Search processing types"
                        processingType={filters.processingType}
                        onProcessingTypeChange={v =>
                            updateFilter(updateProcessingTypeFilter, v)
                        }
                        facilityType={filters.facilityType}
                        suggestions={filterOptions.processingTypeSuggestions}
                        onFetchSuggestions={fetchSuggestionsForProcessingType}
                    />
                </div>
            </div>
            <div className={classes.searchRow}>
                <Button
                    variant="contained"
                    color="primary"
                    onClick={runSearch}
                    disabled={searching}
                >
                    {searching ? 'Searching…' : 'Search'}
                </Button>
                <Typography className={classes.fine}>
                    Closed production locations aren&apos;t shown, and claimed
                    ones can&apos;t be added.
                </Typography>
            </div>
            {error && (
                <Typography className={classes.error} role="alert">
                    {error}
                </Typography>
            )}
            {searching && <CircularProgress size={24} />}

            {results && !searching && (
                <>
                    <div className={classes.toolbar}>
                        <Typography>
                            {results.count > results.limit
                                ? `Showing the first ${results.limit} of ${results.count} results, sorted by name. Narrow your filters to see the rest.`
                                : `${results.count} result${
                                      results.count === 1 ? '' : 's'
                                  }`}
                        </Typography>
                        <span className={classes.grow} />
                        <Button
                            size="small"
                            color="primary"
                            variant="outlined"
                            disabled={!addable.length}
                            onClick={() => onAdd(addable)}
                        >
                            Add all {addable.length} not yet claimed
                        </Button>
                    </div>
                    <div className={classes.tableWrap}>
                        <Table>
                            <TableHead>
                                <TableRow>
                                    <TableCell>Production location</TableCell>
                                    <TableCell>OS ID</TableCell>
                                    <TableCell>Claim status</TableCell>
                                    <TableCell />
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {results.suppliers.map(s => (
                                    <TableRow key={s.os_id}>
                                        <TableCell>
                                            {s.name}
                                            <span className={classes.country}>
                                                {s.country_code}
                                            </span>
                                        </TableCell>
                                        <TableCell>{s.os_id}</TableCell>
                                        <TableCell>
                                            {SEARCH_STATUS_LABELS[
                                                s.claim_status
                                            ] || s.claim_status}
                                        </TableCell>
                                        <TableCell>
                                            {picked.has(s.os_id) ? (
                                                <span className={classes.fine}>
                                                    Added
                                                </span>
                                            ) : (
                                                <Button
                                                    size="small"
                                                    color="primary"
                                                    disabled={!canAdd(s)}
                                                    onClick={() => onAdd([s])}
                                                    aria-label={`Add ${s.name}`}
                                                >
                                                    Add
                                                </Button>
                                            )}
                                        </TableCell>
                                    </TableRow>
                                ))}
                                {results.suppliers.length === 0 && (
                                    <TableRow>
                                        <TableCell colSpan={4}>
                                            No production locations match these
                                            filters.
                                        </TableCell>
                                    </TableRow>
                                )}
                            </TableBody>
                        </Table>
                    </div>
                </>
            )}
        </div>
    );
};

CampaignSupplierSearch.propTypes = {
    classes: object.isRequired,
    filters: object.isRequired,
    filterOptions: object.isRequired,
    getFilters: func.isRequired,
    updateFilter: func.isRequired,
    fetchSuggestionsForProcessingType: func.isRequired,
    picked: instanceOf(Map).isRequired,
    onAdd: func.isRequired,
    fetchFilterOptions: func.isRequired,
};

const mapStateToProps = ({
    filters,
    filterOptions: {
        facilityProcessingType: { data: facilityProcessingType } = {},
        processingTypeSuggestions,
    },
}) => ({
    filters,
    filterOptions: { facilityProcessingType, processingTypeSuggestions },
});

const mapDispatchToProps = dispatch => ({
    fetchFilterOptions: () => {
        dispatch(fetchAllPrimaryFilterOptionsIfNeeded());
        dispatch((_, getState) => {
            const { facilityProcessingType } = getState().filterOptions;
            if (!facilityProcessingType || !facilityProcessingType.data) {
                dispatch(fetchFacilityProcessingTypeOptions());
            }
        });
    },
    updateFilter: (action, value) => dispatch(action(value)),
    fetchSuggestionsForProcessingType: (query, facilityTypes) =>
        dispatch(fetchProcessingTypeSuggestions(query, facilityTypes)),
    // Read when searching, so filters changed a moment ago are included.
    getFilters: () => dispatch((_, getState) => getState().filters),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(campaignSupplierSearchStyles)(CampaignSupplierSearch));
