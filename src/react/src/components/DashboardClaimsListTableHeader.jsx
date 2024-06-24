import React from 'react';
import { func, string } from 'prop-types';
import TableHead from '@material-ui/core/TableHead';
import TableSortLabel from '@material-ui/core/TableSortLabel';
import TableRow from '@material-ui/core/TableRow';
import TableCell from '@material-ui/core/TableCell';

const claimsListHeadCells = [
    {
        id: 'id',
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
        id: 'contributor_name',
        numeric: false,
        disablePadding: true,
        label: 'Organization Name',
    },
    {
        id: 'facility_country_name',
        numeric: false,
        padding: 'dense',
        label: 'Country',
    },
    {
        id: 'created_at',
        numeric: false,
        padding: 'dense',
        label: 'Created',
    },
    {
        id: 'updated_at',
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

function DashboardClaimsListTableHeader({ order, orderBy, onRequestSort }) {
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
                        </TableSortLabel>
                    </TableCell>
                ))}
            </TableRow>
        </TableHead>
    );
}

DashboardClaimsListTableHeader.propTypes = {
    order: string.isRequired,
    orderBy: string.isRequired,
    onRequestSort: func.isRequired,
};

export default DashboardClaimsListTableHeader;
