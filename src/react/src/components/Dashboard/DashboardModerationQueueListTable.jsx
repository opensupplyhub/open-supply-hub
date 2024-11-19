import React, { useState, useCallback } from 'react';
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
import {
    EMPTY_PLACEHOLDER,
    DATE_FORMATS,
    MODERATION_STATUS_COLORS,
} from '../../util/constants';
import { makeDashboardModerationQueueListTableStyles } from '../../util/styles';
import {
    formatDate,
    openInNewTab,
    makeContributionRecordLink,
} from '../../util/util';

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
    const handleRowClick = useCallback(
        id => () => {
            try {
                const url = makeContributionRecordLink(id);
                openInNewTab(url);
            } catch (error) {
                console.error(
                    `Failed to open contribution record: ${error.message}`,
                );
            }
        },
        [],
    );

    const handleChangeRowsPerPage = event => {
        setRowsPerPage(event.target.value);
        setPage(INITIAL_PAGE_INDEX);
    };

    const handleRequestSort = (_, property) => {
        const isDesc = orderBy === property && order === 'desc';
        setOrder(isDesc ? 'asc' : 'desc');
        setOrderBy(property);
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
                                        cleaned_data: cleanedData,
                                        contributor_name: contributorName,
                                        source,
                                        status: moderationStatus,
                                        moderation_decision_date: moderationDecisionDate,
                                        updated_at: updatedAt,
                                    }) => (
                                        <TableRow
                                            hover
                                            key={moderationId}
                                            className={classes.rowStyles}
                                            role="button"
                                            aria-label={`View contribution record for ${cleanedData.name}`}
                                            style={{ cursor: 'pointer' }}
                                            onClick={handleRowClick(
                                                moderationId,
                                            )}
                                        >
                                            <TableCell padding="dense">
                                                {formatDate(
                                                    createdAt,
                                                    DATE_FORMATS.LONG,
                                                )}
                                            </TableCell>
                                            <TableCell>
                                                {cleanedData.name}
                                            </TableCell>
                                            <TableCell padding="dense">
                                                {cleanedData.country.name}
                                            </TableCell>
                                            <TableCell>
                                                {contributorName}
                                            </TableCell>
                                            <TableCell>{source}</TableCell>
                                            <TableCell
                                                style={{
                                                    backgroundColor:
                                                        MODERATION_STATUS_COLORS[
                                                            moderationStatus
                                                        ] || 'default',
                                                }}
                                            >
                                                {moderationStatus}
                                            </TableCell>
                                            <TableCell padding="dense">
                                                {moderationDecisionDate !== null
                                                    ? formatDate(
                                                          moderationDecisionDate,
                                                          DATE_FORMATS.LONG,
                                                      )
                                                    : EMPTY_PLACEHOLDER}
                                            </TableCell>
                                            <TableCell padding="dense">
                                                {moment(updatedAt).format(
                                                    DATE_FORMATS.LONG,
                                                )}
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
