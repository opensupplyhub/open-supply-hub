import React, { useState } from 'react';
import { func, shape } from 'prop-types';
import { withRouter, Link } from 'react-router-dom';
import Paper from '@material-ui/core/Paper';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableRow from '@material-ui/core/TableRow';
import TableCell from '@material-ui/core/TableCell';
import moment from 'moment';
import flow from 'lodash/flow';
import includes from 'lodash/includes';
import noop from 'lodash/noop';
import DashboardClaimsListTableHeaderSorted from './DashboardClaimsListTableHeaderSorted';

import { facilityClaimsListPropType } from '../util/propTypes';

import {
    makeFacilityDetailLink,
    makeProfileRouteLink,
    makeFacilityClaimDetailsLink,
    getIDFromEvent,
} from '../util/util';

const dashboardClaimsListTableSortedStyles = Object.freeze({
    containerStyles: Object.freeze({
        marginBottom: '60px',
    }),
    rowStyles: Object.freeze({
        cursor: 'pointer',
    }),
});

// TODO: move sorting functionality (3 functions) to util.js
function descendingComparator(a, b, orderBy) {
    if (b[orderBy] < a[orderBy]) {
        return -1;
    }
    if (b[orderBy] > a[orderBy]) {
        return 1;
    }
    return 0;
}

function getComparator(order, orderBy) {
    return order === 'desc'
        ? (a, b) => descendingComparator(a, b, orderBy)
        : (a, b) => -descendingComparator(a, b, orderBy);
}

function sort(array, comparator) {
    const stabilizedThis = array.map((el, index) => [el, index]);
    stabilizedThis.sort((a, b) => {
        const order = comparator(a[0], b[0]);
        if (order !== 0) {
            return order;
        }
        return a[1] - b[1];
    });
    return stabilizedThis.map(el => el[0]);
}

const FACILITY_LINK_ID = 'FACILITY_LINK_ID';
const CONTRIBUTOR_LINK_ID = 'CONTRIBUTOR_LINK_ID';

function DashboardClaimsListTableSorted({
    data,
    handleSortClaims,
    history: { push },
}) {
    const [order, setOrder] = useState('asc');
    const [orderBy, setOrderBy] = useState('claim_id');

    const makeRowClickHandler = claimID =>
        flow(getIDFromEvent, id => {
            if (includes([FACILITY_LINK_ID, CONTRIBUTOR_LINK_ID], id)) {
                return noop();
            }

            return push(makeFacilityClaimDetailsLink(claimID));
        });

    const handleRequestSort = (event, property) => {
        const isAsc = orderBy === property && order === 'asc';
        setOrder(isAsc ? 'desc' : 'asc');
        setOrderBy(property);
        const sortedData = sort(data, getComparator(order, orderBy)).slice();
        handleSortClaims(sortedData);
    };

    return (
        <Paper style={dashboardClaimsListTableSortedStyles.containerStyles}>
            <Table>
                <DashboardClaimsListTableHeaderSorted
                    order={order}
                    orderBy={orderBy}
                    onRequestSort={handleRequestSort}
                />
                <TableBody>
                    {data.map(claim => (
                        <TableRow
                            hover
                            key={claim.id}
                            onClick={makeRowClickHandler(claim.id)}
                            style={
                                dashboardClaimsListTableSortedStyles.rowStyles
                            }
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
            </Table>
        </Paper>
    );
}

DashboardClaimsListTableSorted.propTypes = {
    data: facilityClaimsListPropType.isRequired,
    history: shape({
        push: func.isRequired,
    }).isRequired,
};

export default withRouter(DashboardClaimsListTableSorted);
