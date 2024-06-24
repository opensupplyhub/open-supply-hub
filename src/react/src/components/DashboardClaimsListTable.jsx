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
import DashboardClaimsListTableHeader from './DashboardClaimsListTableHeader';

import { facilityClaimsListPropType } from '../util/propTypes';

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
});

const FACILITY_LINK_ID = 'FACILITY_LINK_ID';
const CONTRIBUTOR_LINK_ID = 'CONTRIBUTOR_LINK_ID';

function DashboardClaimsListTable({
    data,
    handleSortClaims,
    history: { push },
}) {
    /*
     Facility claims are sorted by id/desc by default on BE,
     make same defaults on FE
     */
    const [order, setOrder] = useState('desc');
    const [orderBy, setOrderBy] = useState('id');

    const makeRowClickHandler = claimID =>
        flow(getIDFromEvent, id => {
            if (includes([FACILITY_LINK_ID, CONTRIBUTOR_LINK_ID], id)) {
                return noop();
            }

            return push(makeFacilityClaimDetailsLink(claimID));
        });

    const handleRequestSort = (event, property) => {
        let isAsc;
        setOrder(prevOrder => {
            isAsc = orderBy === property && prevOrder === 'asc';
            const newOrder = isAsc ? 'desc' : 'asc';
            return newOrder;
        });

        setOrderBy(property);

        const sortedData = sort(
            data,
            getComparator(isAsc ? 'desc' : 'asc', property),
        ).slice();
        handleSortClaims(sortedData);
    };

    return (
        <Paper style={dashboardClaimsListTableStyles.containerStyles}>
            <Table>
                <DashboardClaimsListTableHeader
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
                            style={dashboardClaimsListTableStyles.rowStyles}
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

DashboardClaimsListTable.propTypes = {
    data: facilityClaimsListPropType.isRequired,
    history: shape({
        push: func.isRequired,
    }).isRequired,
};

export default withRouter(DashboardClaimsListTable);
