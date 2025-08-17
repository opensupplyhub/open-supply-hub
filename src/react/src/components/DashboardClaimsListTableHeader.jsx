import React from 'react';
import { func, string, bool } from 'prop-types';
import TableHead from '@material-ui/core/TableHead';
import TableSortLabel from '@material-ui/core/TableSortLabel';
import TableRow from '@material-ui/core/TableRow';
import TableCell from '@material-ui/core/TableCell';

// Table header ids should match keys from BE
const claimsListHeadCells = [
    {
        id: 'id',
        numeric: true,
        disablePadding: true,
        label: 'Claim ID',
    },
    {
        id: 'claim_reason',
        numeric: false,
        disablePadding: true,
        label: 'Claim Reason',
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
        disablePadding: true,
        label: 'Country',
    },
    {
        id: 'created_at',
        numeric: false,
        disablePadding: true,
        label: 'Created',
    },
    {
        id: 'claim_decision',
        numeric: false,
        disablePadding: true,
        label: 'Claim Decision',
    },
    {
        id: 'status',
        numeric: false,
        disablePadding: true,
        label: 'Status',
    },
    {
        id: 'updated_at',
        numeric: false,
        disablePadding: true,
        label: 'Last Updated',
    },
];

function DashboardClaimsListTableHeader({
    order,
    orderBy,
    onRequestSort,
    fetching,
    loading,
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
                            disabled={fetching || loading}
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
    loading: bool.isRequired,
    fetching: bool.isRequired,
    order: string.isRequired,
    orderBy: string.isRequired,
    onRequestSort: func.isRequired,
};

export default DashboardClaimsListTableHeader;
