import React, { useEffect, useRef, useState } from 'react';
import { func, instanceOf, object } from 'prop-types';
import { connect } from 'react-redux';
import { withStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import CircularProgress from '@material-ui/core/CircularProgress';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Typography from '@material-ui/core/Typography';

import TextSearchFilter from '../Filters/TextSearchFilter';
import ContributorFilter from '../Filters/ContributorFilter';
import CountryNameFilter from '../Filters/CountryNameFilter';
import SectorFilter from '../Filters/SectorFilter';
import FilterSidebarExtendedSearch from '../FilterSidebarExtendedSearch';
import { fetchAllPrimaryFilterOptionsIfNeeded } from '../../actions/filterOptions';
import apiRequest from '../../util/apiRequest';
import { makeClaimCampaignSearchURL } from '../../util/constants';
import { createQueryStringFromSearchFilters } from '../../util/util';
import { campaignSupplierSearchStyles } from './styles';

export const SEARCH_STATUS_LABELS = Object.freeze({
    claimed: 'Claimed',
    pending: 'Claim pending',
    unclaimed: 'Not claimed',
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
    getFilters,
    picked,
    onAdd,
    fetchFilterOptions,
}) => {
    const [searching, setSearching] = useState(false);
    const [results, setResults] = useState(null);
    const [error, setError] = useState(null);
    const extendedSearchRef = useRef(null);

    useEffect(() => {
        fetchFilterOptions();
    }, [fetchFilterOptions]);

    const runSearch = () => {
        // Like the site search: save any processing type still being
        // typed, and stop if it isn't valid.
        const pendingQueryIsValid = extendedSearchRef.current?.commitPendingQuery?.();
        if (pendingQueryIsValid === false) {
            return;
        }
        const queryString = createQueryStringFromSearchFilters(getFilters());
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

    const addable = results
        ? results.suppliers.filter(
              s => s.claim_status !== 'claimed' && !picked.has(s.os_id),
          )
        : [];

    return (
        <div>
            <div className={classes.filters}>
                <TextSearchFilter searchForFacilities={runSearch} />
                <ContributorFilter />
                <CountryNameFilter />
                <SectorFilter />
                <FilterSidebarExtendedSearch ref={extendedSearchRef} />
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
                            Add all {addable.length} not claimed
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
                                                    disabled={
                                                        s.claim_status ===
                                                        'claimed'
                                                    }
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
    getFilters: func.isRequired,
    picked: instanceOf(Map).isRequired,
    onAdd: func.isRequired,
    fetchFilterOptions: func.isRequired,
};

const mapDispatchToProps = dispatch => ({
    fetchFilterOptions: () => dispatch(fetchAllPrimaryFilterOptionsIfNeeded()),
    // Read when searching, so filters changed a moment ago are included.
    getFilters: () => dispatch((_, getState) => getState().filters),
});

export default connect(
    null,
    mapDispatchToProps,
)(withStyles(campaignSupplierSearchStyles)(CampaignSupplierSearch));
