import React, { useState, useEffect, useRef } from 'react';
import { func, shape, bool } from 'prop-types';
import { withRouter, Link } from 'react-router-dom';
import { withStyles } from '@material-ui/core/styles';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableRow from '@material-ui/core/TableRow';
import TableCell from '@material-ui/core/TableCell';
import CircularProgress from '@material-ui/core/CircularProgress';
import moment from 'moment';
import flow from 'lodash/flow';
import includes from 'lodash/includes';
import noop from 'lodash/noop';
import DashboardClaimsListTableHeader from './DashboardClaimsListTableHeader';

import {
    facilityClaimsListPropType,
    claimStatusOptionsPropType,
    countryOptionsPropType,
} from '../util/propTypes';

import {
    makeFacilityDetailLink,
    makeProfileRouteLink,
    makeFacilityClaimDetailsLink,
    getIDFromEvent,
    getComparator,
    sort,
} from '../util/util';

const dashboardClaimsListTableStyles = Object.freeze({
    containerStyles: Object.freeze({
        marginBottom: '60px',
    }),
    rowStyles: Object.freeze({
        cursor: 'pointer',
    }),
    loaderStyle: Object.freeze({
        display: 'block',
        margin: 'auto',
    }),
});

const FACILITY_LINK_ID = 'FACILITY_LINK_ID';
const CONTRIBUTOR_LINK_ID = 'CONTRIBUTOR_LINK_ID';

function DashboardClaimsListTable({
    data,
    fetching,
    handleSortClaims,
    handleGetClaims,
    handleGetCountries,
    claimStatuses,
    clearClaims,
    history: { push },
    classes,
    countriesData,
}) {
    /*
     Facility claims are sorted by id/desc by default on BE;
     Same defaults created on FE
    */
    const [order, setOrder] = useState('desc');
    const [orderBy, setOrderBy] = useState('id');
    const [loading, setLoading] = useState(true);
    const isFirstRender = useRef(true);
    const previousClaimStatuses = useRef(claimStatuses);

    const makeRowClickHandler = claimID =>
        flow(getIDFromEvent, id => {
            if (includes([FACILITY_LINK_ID, CONTRIBUTOR_LINK_ID], id)) {
                return noop();
            }

            return push(makeFacilityClaimDetailsLink(claimID));
        });

    const handleRequestSort = async (event, property) => {
        setLoading(true);

        let isAsc;
        setOrder(prevOrder => {
            isAsc = orderBy === property && prevOrder === 'asc';
            const newOrder = isAsc ? 'desc' : 'asc';
            return newOrder;
        });
        setOrderBy(property);

        /*
         Wait for the state updates before calculate sync sort operation;
         This simulates a new render cycle
        */
        await new Promise(resolve => setTimeout(resolve, 0));

        const sortedData = sort(
            data,
            getComparator(isAsc ? 'desc' : 'asc', property),
        ).slice();

        handleSortClaims(sortedData);
    };

    useEffect(() => {
        if (!countriesData) {
            handleGetCountries();
        }
    }, []);

    useEffect(() => {
        if (isFirstRender.current) {
            isFirstRender.current = false;
        } else if (
            claimStatuses.length > 0 ||
            (previousClaimStatuses.current.length > 0 &&
                claimStatuses.length === 0)
        ) {
            handleGetClaims();
        }

        previousClaimStatuses.current = claimStatuses;
    }, [claimStatuses]);

    useEffect(() => clearClaims, [handleGetClaims, clearClaims]);

    useEffect(() => {
        // Add small timeout to proper render the loader
        const timer = setTimeout(() => {
            setLoading(false);
        }, 200);

        return () => clearTimeout(timer);
    }, [data]);

    if (!data) {
        return null;
    }

    return (
        <Table>
            <DashboardClaimsListTableHeader
                order={order}
                orderBy={orderBy}
                onRequestSort={handleRequestSort}
            />
            {loading || fetching ? (
                <TableBody>
                    <TableRow>
                        <TableCell colSpan={7}>
                            <CircularProgress
                                size={25}
                                className={classes.loaderStyle}
                            />
                        </TableCell>
                    </TableRow>
                </TableBody>
            ) : (
                <TableBody>
                    {data.map(claim => (
                        <TableRow
                            hover
                            key={claim.id}
                            onClick={makeRowClickHandler(claim.id)}
                            className={classes.rowStyles}
                        >
                            <TableCell padding="dense">{claim.id}</TableCell>
                            <TableCell>
                                <Link
                                    to={makeFacilityDetailLink(claim.os_id)}
                                    href={makeFacilityDetailLink(claim.os_id)}
                                    id={FACILITY_LINK_ID}
                                >
                                    {claim.facility_name}
                                </Link>
                            </TableCell>
                            <TableCell>
                                <Link
                                    to={makeProfileRouteLink(
                                        claim.contributor_id,
                                    )}
                                    href={makeProfileRouteLink(
                                        claim.contributor_id,
                                    )}
                                    id={CONTRIBUTOR_LINK_ID}
                                >
                                    {claim.contributor_name}
                                </Link>
                            </TableCell>
                            <TableCell padding="dense">
                                {claim.facility_country_name}
                            </TableCell>
                            <TableCell padding="dense">
                                {moment(claim.created_at).format('LL')}
                            </TableCell>
                            <TableCell padding="dense">
                                {moment(claim.updated_at).format('LL')}
                            </TableCell>
                            <TableCell padding="dense">
                                {claim.status}
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            )}
        </Table>
    );
}

DashboardClaimsListTable.defaultProps = {
    data: null,
    countriesData: null,
};

DashboardClaimsListTable.propTypes = {
    data: facilityClaimsListPropType,
    fetching: bool.isRequired,
    handleGetClaims: func.isRequired,
    handleGetCountries: func.isRequired,
    history: shape({
        push: func.isRequired,
    }).isRequired,
    claimStatuses: claimStatusOptionsPropType.isRequired,
    countriesData: countryOptionsPropType,
    clearClaims: func.isRequired,
};

export default withRouter(
    withStyles(dashboardClaimsListTableStyles)(DashboardClaimsListTable),
);
