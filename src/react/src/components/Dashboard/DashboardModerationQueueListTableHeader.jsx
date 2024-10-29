import React from 'react';
import { bool, func, object, oneOf, string } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import TableSortLabel from '@material-ui/core/TableSortLabel';
import { MODERATION_QUEUE_HEAD_CELLS } from '../../util/constants';
import { makeDashboardModerationQueueTableHeaderStyles } from '../../util/styles';

const DashboardModerationQueueListTableHeader = ({
    order,
    orderBy,
    onRequestSort,
    fetching,
    classes,
}) => {
    const createSortHandler = property => event => {
        onRequestSort(event, property);
    };

    return (
        <TableHead>
            <TableRow>
                {MODERATION_QUEUE_HEAD_CELLS.map(({ id, label }) => (
                    <TableCell
                        key={id}
                        sortDirection={orderBy === id ? order : false}
                        className={classes.headerCellStyles}
                    >
                        <TableSortLabel
                            aria-label={`${label} sort`}
                            active={orderBy === id}
                            direction={orderBy === id ? order : 'asc'}
                            onClick={createSortHandler(id)}
                            disabled={fetching}
                        >
                            {label}
                        </TableSortLabel>
                    </TableCell>
                ))}
            </TableRow>
        </TableHead>
    );
};

DashboardModerationQueueListTableHeader.propTypes = {
    fetching: bool.isRequired,
    order: oneOf(['asc', 'desc']).isRequired,
    orderBy: string.isRequired,
    onRequestSort: func.isRequired,
    classes: object.isRequired,
};

export default withStyles(makeDashboardModerationQueueTableHeaderStyles)(
    DashboardModerationQueueListTableHeader,
);
