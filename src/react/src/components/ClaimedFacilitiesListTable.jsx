import React from 'react';
import { func, shape } from 'prop-types';
import { withRouter } from 'react-router-dom';
import Paper from '@material-ui/core/Paper';
import Table from '@material-ui/core/Table';
import TableHead from '@material-ui/core/TableHead';
import TableBody from '@material-ui/core/TableBody';
import TableRow from '@material-ui/core/TableRow';
import TableCell from '@material-ui/core/TableCell';
import Chip from '@material-ui/core/Chip';

import { facilityClaimsListPropType } from '../util/propTypes';
import { facilityClaimStatusChoicesEnum } from '../util/constants';
import COLOURS from '../util/COLOURS';

import {
    makeClaimedFacilityDetailsLink,
    makePendingClaimEditLink,
} from '../util/util';

const dashboardClaimsListTableStyles = Object.freeze({
    containerStyles: Object.freeze({
        marginBottom: '60px',
        width: '100%',
    }),
    rowStyles: Object.freeze({
        cursor: 'pointer',
    }),
    osIdColumnStyles: Object.freeze({
        width: '20%',
    }),
    pendingChipStyles: Object.freeze({
        backgroundColor: COLOURS.PALE_LIGHT_YELLOW,
    }),
    approvedChipStyles: Object.freeze({
        backgroundColor: COLOURS.MINT_GREEN,
    }),
});

const statusChipStyle = status =>
    status === facilityClaimStatusChoicesEnum.PENDING
        ? dashboardClaimsListTableStyles.pendingChipStyles
        : dashboardClaimsListTableStyles.approvedChipStyles;

function ClaimedFacilitiesListTable({ data, history: { push } }) {
    // A pending claim opens the pending-claim edit view; an approved
    // claim opens the claimed-facility profile editor, as before.
    const makeRowClickHandler = claim => () =>
        push(
            claim.status === facilityClaimStatusChoicesEnum.PENDING
                ? makePendingClaimEditLink(claim.id)
                : makeClaimedFacilityDetailsLink(claim.id),
        );

    return (
        <Paper style={dashboardClaimsListTableStyles.containerStyles}>
            <Table>
                <TableHead>
                    <TableRow>
                        <TableCell>Name</TableCell>
                        <TableCell>OS ID</TableCell>
                        <TableCell>Address</TableCell>
                        <TableCell>Country</TableCell>
                        <TableCell>Status</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {data.map(claim => (
                        <TableRow
                            hover
                            key={claim.id}
                            onClick={makeRowClickHandler(claim)}
                            style={dashboardClaimsListTableStyles.rowStyles}
                        >
                            <TableCell>{claim.facility_name}</TableCell>
                            <TableCell>{claim.os_id}</TableCell>
                            <TableCell>{claim.facility_address}</TableCell>
                            <TableCell>{claim.facility_country_name}</TableCell>
                            <TableCell>
                                <Chip
                                    label={claim.status}
                                    style={statusChipStyle(claim.status)}
                                />
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </Paper>
    );
}

ClaimedFacilitiesListTable.propTypes = {
    data: facilityClaimsListPropType.isRequired,
    history: shape({
        push: func.isRequired,
    }).isRequired,
};

export default withRouter(ClaimedFacilitiesListTable);
