import React from 'react';
import { bool, func, object, string } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import TableSortLabel from '@material-ui/core/TableSortLabel';

const moderationQueueListHeadCells = [
    {
        id: 'created_at',
        numeric: false,
        disablePadding: true,
        label: 'Created Date',
    },
    {
        id: 'name',
        numeric: false,
        disablePadding: true,
        label: 'Location Name',
    },
    {
        id: 'country.name',
        numeric: false,
        disablePadding: true,
        label: 'Country',
    },
    {
        id: 'contributor_name',
        numeric: false,
        disablePadding: true,
        label: 'Contributor',
    },
    {
        id: 'source',
        numeric: false,
        disablePadding: true,
        label: 'Source Type',
    },
    {
        id: 'moderation_status',
        numeric: false,
        disablePadding: true,
        label: 'Moderation Status',
    },
    {
        id: 'moderation_decision_date',
        numeric: false,
        disablePadding: true,
        label: 'Moderation Decision Date',
    },
    {
        id: 'updated_at',
        numeric: false,
        disablePadding: true,
        label: 'Last Updated',
    },
];

const makeDashboardModerationQueueTableHeaderStyles = Object.freeze({
    headerCellStyles: Object.freeze({
        fontSize: '14px',
        fontWeight: 'bold',
    }),
});

function DashboardModerationQueueListTableHeader({
    order,
    orderBy,
    onRequestSort,
    fetching,
    classes,
}) {
    const createSortHandler = property => event => {
        onRequestSort(event, property);
    };

    return (
        <TableHead>
            <TableRow>
                {moderationQueueListHeadCells.map(headCell => (
                    <TableCell
                        key={headCell.id}
                        sortDirection={orderBy === headCell.id ? order : false}
                        className={classes.headerCellStyles}
                    >
                        <TableSortLabel
                            active={orderBy === headCell.id}
                            direction={orderBy === headCell.id ? order : 'asc'}
                            onClick={createSortHandler(headCell.id)}
                            disabled={fetching}
                        >
                            {headCell.label}
                        </TableSortLabel>
                    </TableCell>
                ))}
            </TableRow>
        </TableHead>
    );
}

DashboardModerationQueueListTableHeader.propTypes = {
    fetching: bool.isRequired,
    order: string.isRequired,
    orderBy: string.isRequired,
    onRequestSort: func.isRequired,
    classes: object.isRequired,
};

export default withStyles(makeDashboardModerationQueueTableHeaderStyles)(
    DashboardModerationQueueListTableHeader,
);
