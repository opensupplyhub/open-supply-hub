import React, { useCallback } from 'react';
import { useDispatch } from 'react-redux';
import { bool, object, number, func } from 'prop-types';
import { withRouter } from 'react-router-dom';
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
import { moderationEventsListPropType } from '../../util/propTypes';
import {
    EMPTY_PLACEHOLDER,
    DATE_FORMATS,
    MODERATION_STATUS_COLORS,
    MODERATION_INITIAL_PAGE_INDEX,
    MODERATION_DEFAULT_ROWS_PER_PAGE,
} from '../../util/constants';
import { makeDashboardModerationQueueListTableStyles } from '../../util/styles';
import {
    formatUTCDate,
    openInNewTab,
    makeContributionRecordLink,
} from '../../util/util';

const ROWS_PER_PAGE_OPTIONS = [25, 50, 100];
function DashboardModerationQueueListTable({
    moderationEventsList,
    count,
    page,
    maxPage,
    pageSize,
    sort: { sortBy, orderBy },
    fetching,
    fetchModerationEvents,
    classes,
}) {
    const dispatch = useDispatch();

    const handleChangePage = (_, newPage) => {
        const isNewMaxPage = newPage > maxPage;

        dispatch(
            updateModerationEventsPage({
                page: newPage,
                maxPage: isNewMaxPage ? newPage : maxPage,
                pageSize,
            }),
        );
        if (isNewMaxPage) {
            fetchModerationEvents();
        }
    };
    const handleRowClick = useCallback(
        id => () => {
            try {
                const url = makeContributionRecordLink(id);
                openInNewTab(url);
            } catch (error) {
                console.error(
                    `Failed to open contribution record: ${error.detail}`,
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
                page: MODERATION_INITIAL_PAGE_INDEX,
                maxPage: MODERATION_INITIAL_PAGE_INDEX,
                pageSize: newRowsPerPage,
            }),
        );
        fetchModerationEvents();
    };

    const handleRequestSort = (_, property) => {
        const isDesc = sortBy === property && orderBy === 'desc';
        const newOrder = isDesc ? 'asc' : 'desc';

        dispatch(clearModerationEvents());
        dispatch(
            updateModerationEventsOrder({
                sortBy: property,
                orderBy: newOrder,
            }),
        );
        dispatch(
            updateModerationEventsPage({
                page: MODERATION_INITIAL_PAGE_INDEX,
                maxPage: MODERATION_INITIAL_PAGE_INDEX,
                pageSize,
            }),
        );
        fetchModerationEvents();
    };

    return (
        <>
            <div className={classes.tableContainerStyles}>
                <Table>
                    <DashboardModerationQueueListTableHeader
                        order={orderBy}
                        orderBy={sortBy}
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
                            {moderationEventsList
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
                                        contributor_id: contributorId,
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
                                                {formatUTCDate(
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
                                            <TableCell padding="dense">
                                                {contributorId || EMPTY_PLACEHOLDER}
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
                                                {moderationDecisionDate
                                                    ? formatUTCDate(
                                                          moderationDecisionDate,
                                                          DATE_FORMATS.LONG,
                                                      )
                                                    : EMPTY_PLACEHOLDER}
                                            </TableCell>
                                            <TableCell padding="dense">
                                                {formatUTCDate(
                                                    updatedAt,
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
    moderationEventsList: [],
    count: 0,
    page: MODERATION_INITIAL_PAGE_INDEX,
    maxPage: MODERATION_INITIAL_PAGE_INDEX,
    pageSize: MODERATION_DEFAULT_ROWS_PER_PAGE,
    sort: {
        sortBy: 'created_at',
        orderBy: 'desc',
    },
};

DashboardModerationQueueListTable.propTypes = {
    moderationEventsList: moderationEventsListPropType,
    count: number,
    page: number,
    maxPage: number,
    pageSize: number,
    sort: object,
    fetching: bool.isRequired,
    fetchModerationEvents: func.isRequired,
    classes: object.isRequired,
};

export default withRouter(
    withStyles(makeDashboardModerationQueueListTableStyles)(
        DashboardModerationQueueListTable,
    ),
);
