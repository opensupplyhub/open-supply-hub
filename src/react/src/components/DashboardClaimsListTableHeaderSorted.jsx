/* eslint no-unused-vars: 0 */
import React from 'react';
import TableHead from '@material-ui/core/TableHead';
import TableSortLabel from '@material-ui/core/TableSortLabel';
import TableRow from '@material-ui/core/TableRow';
import TableCell from '@material-ui/core/TableCell';
// TODO: probably you don't need this util
import { visuallyHidden } from '@mui/utils';

const claimsListHeadCells = [
    {
        id: 'claim_id',
        numeric: true,
        padding: 'dense',
        label: 'Claim ID',
    },
    {
        id: 'facility_name',
        numeric: false,
        disablePadding: true,
        label: 'Facility Name',
    },
    {
        id: 'organization_name',
        numeric: false,
        disablePadding: true,
        label: 'Organization Name',
    },
    {
        id: 'country',
        numeric: false,
        padding: 'dense',
        label: 'Country',
    },
    {
        id: 'created',
        numeric: false,
        padding: 'dense',
        label: 'Created',
    },
    {
        id: 'last_updated',
        numeric: false,
        padding: 'dense',
        label: 'Last Updated',
    },
    {
        id: 'status',
        numeric: false,
        padding: 'dense',
        label: 'Status',
    },
];

function DashboardClaimsListTableHeaderSorted({
    order,
    orderBy,
    onRequestSort,
}) {
    const createSortHandler = property => event => {
        onRequestSort(event, property);
    };

    return (
        <TableHead>
            <TableRow>
                {claimsListHeadCells.map(headCell => (
                    <TableCell
                        key={headCell.id}
                        sortDirection={orderBy === headCell.id ? order : false}
                    >
                        <TableSortLabel
                            active={orderBy === headCell.id}
                            direction={orderBy === headCell.id ? order : 'asc'}
                            onClick={createSortHandler(headCell.id)}
                        >
                            {headCell.label}
                            {orderBy === headCell.id ? (
                                <span sx={visuallyHidden}>
                                    {order === 'desc'
                                        ? 'sorted descending'
                                        : 'sorted ascending'}
                                </span>
                            ) : null}
                        </TableSortLabel>
                    </TableCell>
                ))}
            </TableRow>
        </TableHead>
    );
}

// TODO: Apply proptypes

export default DashboardClaimsListTableHeaderSorted;
