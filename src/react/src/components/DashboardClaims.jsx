/* eslint no-unused-vars: 0 */
import React, { useEffect } from 'react';
import ReactSelect from 'react-select';
import { connect } from 'react-redux';
import { arrayOf, bool, func, string } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Paper from '@material-ui/core/Paper';
import CircularProgress from '@material-ui/core/CircularProgress';
import Typography from '@material-ui/core/Typography';

import DownloadFacilityClaimsButton from './DownloadFacilityClaimsButton';
import DashboardClaimsListTable from './DashboardClaimsListTable';

import {
    fetchFacilityClaims,
    clearFacilityClaims,
    sortFacilityClaims,
} from '../actions/claimFacilityDashboard';

import { facilityClaimsListPropType } from '../util/propTypes';

const STATUS = 'STATUS';

const dashboardClaimsStyles = () =>
    Object.freeze({
        container: Object.freeze({
            marginBottom: '60px',
            width: '100%',
        }),
        dashboardClaimsContainer: Object.freeze({
            marginTop: '24px',
            width: '100%',
        }),
        filterRow: Object.freeze({
            padding: '20px',
            display: 'flex',
            flexDirection: 'column',
            gap: '20px',
        }),
        filter: Object.freeze({
            flex: 1,
        }),
    });

const DashboardClaims = ({
    data,
    fetching,
    error,
    getClaims,
    clearClaims,
    sortClaims,
    classes,
}) => {
    useEffect(() => {
        getClaims();

        return clearClaims;
    }, [getClaims, clearClaims]);

    if (fetching) {
        return <CircularProgress />;
    }

    if (error) {
        return <Typography>{error}</Typography>;
    }

    if (!data) {
        return null;
    }

    return (
        <Paper className={classes.container}>
          <div className={classes.dashboardClaimsContainer}>
              <DownloadFacilityClaimsButton data={data} />
              <div className={classes.filterRow}>
                  <div className={classes.filter}>
                      <label htmlFor={STATUS}>Claim Status</label>
                        {/**
                     * <ReactSelect
                        id={STATUS}
                        name={STATUS}
                        classNamePrefix="select"
                        options={facilityClaimStatusChoicesEnum}
                        value={facilityClaimStatusChoicesEnum.find(
                            s => s.value === status,
                        )}
                        onChange={onStatusUpdate}
                        disabled={fetchingData}
                        styles={selectStyles}
                        theme={getSelectTheme}
                    />
                     */}
                    </div>
                </div>
              <DashboardClaimsListTable
                  data={data}
                  handleSortClaims={sortClaims}
              />
          </div>
        </Paper>
    );
};

DashboardClaims.defaultProps = {
    data: null,
    error: null,
};

DashboardClaims.propTypes = {
    data: facilityClaimsListPropType,
    fetching: bool.isRequired,
    error: arrayOf(string),
    getClaims: func.isRequired,
    clearClaims: func.isRequired,
    sortClaims: func.isRequired,
};

function mapStateToProps({
    claimFacilityDashboard: {
        list: { data, fetching, error },
    },
}) {
    return {
        data,
        fetching,
        error,
    };
}

function mapDispatchToProps(dispatch) {
    return {
        getClaims: () => dispatch(fetchFacilityClaims()),
        clearClaims: () => dispatch(clearFacilityClaims()),
        sortClaims: sortedData => dispatch(sortFacilityClaims(sortedData)),
    };
}

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(dashboardClaimsStyles)(DashboardClaims));
