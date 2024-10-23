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
import COLOURS from '../../util/COLOURS';

const makeDashboardModerationQueueListTableStyles = Object.freeze({
    tableContainerStyles: Object.freeze({
        overflowX: 'auto',
    }),
    rowStyles: Object.freeze({
        cursor: 'pointer',
    }),
    emptyRowStyles: Object.freeze({
        height: '5px',
    }),
    loaderStyles: Object.freeze({
        display: 'block',
        margin: 'auto',
    }),
    slcRowStyles: Object.freeze({
        backgroundColor: COLOURS.PALE_BLUE,
    }),
    apiRowStyles: Object.freeze({
        backgroundColor: COLOURS.LAVENDER_GREY,
    }),
    defaultRowStyles: Object.freeze({
        backgroundColor: 'inherit',
    }),
});

function DashboardModerationQueueListTable({ events, fetching, classes }) {
    const [order, setOrder] = useState('desc');
    const [orderBy, setOrderBy] = useState('created_at');
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(5);

    function handleChangePage(event, newPage) {
        setPage(newPage);
    }

    function handleChangeRowsPerPage(event) {
        setRowsPerPage(event.target.value);
    }

    const handleRequestSort = (event, property) => {
        const isDesc = orderBy === property && order === 'desc';
        setOrder(isDesc ? 'asc' : 'desc');
        setOrderBy(property);
    };

    const getRowClassName = source => {
        if (source === SOURCE_TYPES.SLC) {
            return classes.slcRowStyles;
        }
        if (source === SOURCE_TYPES.API) {
            return classes.apiRowStyles;
        }
        return classes.defaultRowStyles;
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
                                .map(event => (
                                    <TableRow
                                        hover
                                        key={event.moderation_id}
                                        className={`${
                                            classes.rowStyles
                                        } ${getRowClassName(event.source)}`}
                                    >
                                        <TableCell padding="dense">
                                            {moment(event.created_at).format(
                                                'LL',
                                            )}
                                        </TableCell>
                                        <TableCell>{event.name}</TableCell>
                                        <TableCell padding="dense">
                                            {event.country.name}
                                        </TableCell>
                                        <TableCell>
                                            {event.contributor_name}
                                        </TableCell>
                                        <TableCell>{event.source}</TableCell>
                                        <TableCell>
                                            {event.moderation_status}
                                        </TableCell>
                                        <TableCell padding="dense">
                                            {event.moderation_decision_date !==
                                            null
                                                ? moment(
                                                      event.moderation_decision_date,
                                                  ).format('LL')
                                                : EMPTY_PLACEHOLDER}
                                        </TableCell>
                                        <TableCell padding="dense">
                                            {moment(event.updated_at).format(
                                                'LL',
                                            )}
                                        </TableCell>
                                    </TableRow>
                                ))}
                        </TableBody>
                    )}
                </Table>
            </div>
            <TablePagination
                rowsPerPageOptions={[5, 10, 25]}
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
