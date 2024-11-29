import React, { useState, useCallback } from 'react';
import { useDispatch } from 'react-redux';
import { bool, object, number, func } from 'prop-types';
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
import {
    clearModerationEvents,
    updateModerationEventsPage,
    updateModerationEventsOrder,
} from '../../actions/dashboardModerationQueue';
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
const ROWS_PER_PAGE_OPTIONS = [25, 50, 100];
const DEFAULT_ROWS_PER_PAGE = 25;
function DashboardModerationQueueListTable({
    events,
    count,
    page,
    maxPage,
    pageSize,
    fetching,
    fetchEvents,
    classes,
}) {
    const [order, setOrder] = useState('desc');
    const [orderBy, setOrderBy] = useState('created_at');

    const dispatch = useDispatch();

    const handleChangePage = (_, newPage) => {
        dispatch(
            updateModerationEventsPage({
                page: newPage,
                maxPage: newPage > maxPage ? newPage : maxPage,
                pageSize,
            }),
        );
        if (newPage > page && newPage > maxPage) {
            fetchEvents();
        }
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
        const newRowsPerPage = event.target.value;

        dispatch(clearModerationEvents());
        dispatch(
            updateModerationEventsPage({
                page: INITIAL_PAGE_INDEX,
                maxPage: INITIAL_PAGE_INDEX,
                pageSize: newRowsPerPage,
            }),
        );
        fetchEvents();
    };

    const handleRequestSort = (_, property) => {
        const isDesc = orderBy === property && order === 'desc';
        const newOrder = isDesc ? 'asc' : 'desc';
        setOrder(newOrder);
        setOrderBy(property);

        dispatch(clearModerationEvents());
        dispatch(
            updateModerationEventsOrder({
                sortBy: property,
                orderBy: newOrder,
            }),
        );
        dispatch(
            updateModerationEventsPage({
                page: INITIAL_PAGE_INDEX,
                maxPage: INITIAL_PAGE_INDEX,
                pageSize,
            }),
        );
        fetchEvents();
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
                                    page * pageSize,
                                    page * pageSize + pageSize,
                                )
                                .map(
                                    ({
                                        moderation_id: moderationId,
                                        created_at: createdAt,
                                        cleaned_data: cleanedData,
                                        contributor_name: contributorName,
                                        source,
                                        status: moderationStatus,
                                        status_change_date: moderationDecisionDate,
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
                count={count}
                rowsPerPage={pageSize}
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
    count: 0,
    page: INITIAL_PAGE_INDEX,
    maxPage: INITIAL_PAGE_INDEX,
    pageSize: DEFAULT_ROWS_PER_PAGE,
};

DashboardModerationQueueListTable.propTypes = {
    events: moderationEventsPropType,
    count: number,
    page: number,
    maxPage: number,
    pageSize: number,
    fetching: bool.isRequired,
    fetchEvents: func.isRequired,
    classes: object.isRequired,
};

export default withRouter(
    withStyles(makeDashboardModerationQueueListTableStyles)(
        DashboardModerationQueueListTable,
    ),
);
