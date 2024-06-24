import React, { useCallback } from 'react';
import { func, string } from 'prop-types';
import TableHead from '@material-ui/core/TableHead';
import TableSortLabel from '@material-ui/core/TableSortLabel';
import TableRow from '@material-ui/core/TableRow';
import TableCell from '@material-ui/core/TableCell';

const DashboardClaimsListTableHeaderStyles = Object.freeze({
    firstTh: {
        width: '80px',
    },
    secondTh: {
        width: '175px',
    },
    thirdTh: {
        width: '145px',
    },
    fourthTh: {
        width: '90px',
    },
    sixthTh: {
        width: '100px',
    },
});

// Table header ids should match keys from BE
const claimsListHeadCells = [
    {
        id: 'id',
        numeric: true,
        disablePadding: true,
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
        id: 'updated_at',
        numeric: false,
        disablePadding: true,
        label: 'Last Updated',
    },
    {
        id: 'status',
        numeric: false,
        disablePadding: true,
        label: 'Status',
    },
];

function DashboardClaimsListTableHeader({ order, orderBy, onRequestSort }) {
    const getStyleByIndex = useCallback(index => {
        switch (index) {
            case 0:
                return DashboardClaimsListTableHeaderStyles.firstTh;
            case 1:
                return DashboardClaimsListTableHeaderStyles.secondTh;
            case 2:
                return DashboardClaimsListTableHeaderStyles.thirdTh;
            case 3:
                return DashboardClaimsListTableHeaderStyles.fourTh;
            case 5:
                return DashboardClaimsListTableHeaderStyles.sixthTh;
            default:
                return {};
        }
    }, []);

    const createSortHandler = property => event => {
        onRequestSort(event, property);
    };

    return (
        <TableHead>
            <TableRow>
                {claimsListHeadCells.map((headCell, index) => (
                    <TableCell
                        key={headCell.id}
                        sortDirection={orderBy === headCell.id ? order : false}
                        style={getStyleByIndex(index)}
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
