import React, { useState } from 'react';
import { bool, object } from 'prop-types';
import { withRouter } from 'react-router-dom';
import moment from 'moment';
import { withStyles } from '@material-ui/core/styles';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableRow from '@material-ui/core/TableRow';
import TableCell from '@material-ui/core/TableCell';
import TablePagination from '@material-ui/core/TablePagination';
import CircularProgress from '@material-ui/core/CircularProgress';
import DashboardModerationQueueListTableHeader from './DashboardModerationQueueListTableHeader';
import { moderationEventsPropType } from '../../util/propTypes';
import { SOURCE_TYPES, EMPTY_PLACEHOLDER } from '../../util/constants';
import { makeDashboardModerationQueueListTableStyles } from '../../util/styles';
import { formatDate } from '../../util/util';

const INITIAL_PAGE_INDEX = 0;
const ROWS_PER_PAGE_OPTIONS = [5, 10, 25];
const DEFAULT_ROWS_PER_PAGE = 5;
function DashboardModerationQueueListTable({ events, fetching, classes }) {
    const [order, setOrder] = useState('desc');
    const [orderBy, setOrderBy] = useState('created_at');
    const [page, setPage] = useState(INITIAL_PAGE_INDEX);
    const [rowsPerPage, setRowsPerPage] = useState(DEFAULT_ROWS_PER_PAGE);

    const handleChangePage = (_, newPage) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = event => {
        setRowsPerPage(event.target.value);
        setPage(INITIAL_PAGE_INDEX);
    };

    const handleRequestSort = (_, property) => {
        const isDesc = orderBy === property && order === 'desc';
        setOrder(isDesc ? 'asc' : 'desc');
        setOrderBy(property);
    };

    const getRowClassName = source => {
        switch (source) {
            case SOURCE_TYPES.SLC:
                return classes.slcRowStyles;
            case SOURCE_TYPES.API:
                return classes.apiRowStyles;
            default:
                return classes.defaultRowStyles;
        }
    };

    return (
        <>
            <div className={classes.tableContainerStyles}>
                <Table>
                    <DashboardModerationQueueListTableHeader
                        order={order}
                        orderBy={orderBy}
                        onRequestSort={handleRequestSort}
                        fetching={fetching}
                    />
                    {fetching ? (
                        <TableBody>
                            <TableRow>
                                <TableCell colSpan={8}>
                                    <CircularProgress
                                        size={25}
                                        className={classes.loaderStyles}
                                    />
                                </TableCell>
                            </TableRow>
                        </TableBody>
                    ) : (
                        <TableBody>
                            <TableRow className={classes.emptyRowStyles} />
                            {events
                                .slice(
                                    page * rowsPerPage,
                                    page * rowsPerPage + rowsPerPage,
                                )
                                .map(
                                    ({
                                        moderation_id: moderationId,
                                        created_at: createdAt,
                                        name,
                                        country,
                                        contributor_name: contributorName,
                                        source,
                                        moderation_status: moderationStatus,
                                        moderation_decision_date: moderationDecisionDate,
                                        updated_at: updatedAt,
                                    }) => (
                                        <TableRow
                                            hover
                                            key={moderationId}
                                            className={`${
                                                classes.row
                                            } ${getRowClassName(source)}`}
                                        >
                                            <TableCell padding="dense">
                                                {formatDate(createdAt, 'LL')}
                                            </TableCell>
                                            <TableCell>{name}</TableCell>
                                            <TableCell padding="dense">
                                                {country.name}
                                            </TableCell>
                                            <TableCell>
                                                {contributorName}
                                            </TableCell>
                                            <TableCell>{source}</TableCell>
                                            <TableCell>
                                                {moderationStatus}
                                            </TableCell>
                                            <TableCell padding="dense">
                                                {moderationDecisionDate !== null
                                                    ? formatDate(
                                                          moderationDecisionDate,
                                                          'LL',
                                                      )
                                                    : EMPTY_PLACEHOLDER}
                                            </TableCell>
                                            <TableCell padding="dense">
                                                {moment(updatedAt).format('LL')}
                                            </TableCell>
                                        </TableRow>
                                    ),
                                )}
                        </TableBody>
                    )}
                </Table>
            </div>
            <TablePagination
                rowsPerPageOptions={ROWS_PER_PAGE_OPTIONS}
                component="div"
                count={events.length}
                rowsPerPage={rowsPerPage}
                page={page}
                backIconButtonProps={{
                    'aria-label': 'Previous Page',
                }}
                nextIconButtonProps={{
                    'aria-label': 'Next Page',
                }}
                onChangePage={handleChangePage}
                onChangeRowsPerPage={handleChangeRowsPerPage}
            />
        </>
    );
}

DashboardModerationQueueListTable.defaultProps = {
    events: null,
};

DashboardModerationQueueListTable.propTypes = {
    events: moderationEventsPropType,
    fetching: bool.isRequired,
    classes: object.isRequired,
};

export default withRouter(
    withStyles(makeDashboardModerationQueueListTableStyles)(
        DashboardModerationQueueListTable,
    ),
);
