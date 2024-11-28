import React, { useState, useCallback, useEffect } from 'react';
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
    index,
    maxIndex,
    fetching,
    fetchEvents,
    classes,
}) {
    const [order, setOrder] = useState('desc');
    const [orderBy, setOrderBy] = useState('created_at');
    const [page, setPage] = useState(INITIAL_PAGE_INDEX);
    const [maxPage, setMaxPage] = useState(INITIAL_PAGE_INDEX);
    const [rowsPerPage, setRowsPerPage] = useState(DEFAULT_ROWS_PER_PAGE);

    const dispatch = useDispatch();

    useEffect(() => {
        setPage(index);
        setMaxPage(maxIndex);
    }, [index, maxIndex]);

    const handleChangePage = (_, newPage) => {
        if (newPage > page && newPage > maxPage) {
            dispatch(
                updateModerationEventsPage({
                    page: newPage,
                    maxPage: newPage,
                    pageSize: rowsPerPage,
                }),
            );
            fetchEvents();
        } else {
            setPage(newPage);
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
        setRowsPerPage(newRowsPerPage);

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
                pageSize: rowsPerPage,
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
                count={count}
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
    count: 0,
    index: INITIAL_PAGE_INDEX,
    maxIndex: INITIAL_PAGE_INDEX,
};

DashboardModerationQueueListTable.propTypes = {
    events: moderationEventsPropType,
    count: number,
    index: number,
    maxIndex: number,
    fetching: bool.isRequired,
    fetchEvents: func.isRequired,
    classes: object.isRequired,
};

export default withRouter(
    withStyles(makeDashboardModerationQueueListTableStyles)(
        DashboardModerationQueueListTable,
    ),
);
