import React from 'react';
import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';
import { withStyles } from '@material-ui/core/styles';
import Paper from '@material-ui/core/Paper';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TablePagination from '@material-ui/core/TablePagination';
import TableRow from '@material-ui/core/TableRow';
import TableSortLabel from '@material-ui/core/TableSortLabel';
import CircularProgress from '@material-ui/core/CircularProgress';
import moment from 'moment';

import { CandidateStateChip } from './CandidateBadge';
import {
    CANDIDATE_LIST_COPY,
    formatCandidateTally,
} from '../../util/candidateCopy';
import {
    CANDIDATE_LIST_PAGE_SIZE,
    CANDIDATE_LIST_SORT_FIELDS,
    formatConfidence,
    formatDistance,
    totalVotes,
} from '../../util/candidates';
import { makeFacilityDetailLink } from '../../util/util';
import { candidateListTableStyles } from './styles';

const COLUMNS = [
    { key: 'os_id', label: CANDIDATE_LIST_COPY.columnOsId },
    {
        key: 'confidence',
        label: CANDIDATE_LIST_COPY.columnConfidence,
        sortField: CANDIDATE_LIST_SORT_FIELDS.CONFIDENCE,
        // The reviewer wants the least certain detections first.
        defaultDirection: 'asc',
    },
    { key: 'state', label: CANDIDATE_LIST_COPY.columnState },
    { key: 'votes', label: CANDIDATE_LIST_COPY.columnVotes },
    {
        key: 'nearby',
        label: CANDIDATE_LIST_COPY.columnNearby,
        sortField: CANDIDATE_LIST_SORT_FIELDS.NEARBY_COUNT,
        defaultDirection: 'desc',
    },
    {
        key: 'nearest',
        label: CANDIDATE_LIST_COPY.columnNearest,
        sortField: CANDIDATE_LIST_SORT_FIELDS.NEAREST_M,
        defaultDirection: 'asc',
    },
    {
        key: 'detected',
        label: CANDIDATE_LIST_COPY.columnDetected,
        sortField: CANDIDATE_LIST_SORT_FIELDS.CREATED_AT,
        defaultDirection: 'desc',
    },
    { key: 'country', label: CANDIDATE_LIST_COPY.columnCountry },
];

/** 'confidence' | '-confidence' -> { field, direction } */
export const parseSort = sort => ({
    field: sort.replace(/^-/, ''),
    direction: sort.startsWith('-') ? 'desc' : 'asc',
});

/**
 * The sort to apply when a header is clicked: first click uses the
 * column's natural direction, a second click flips it.
 */
export const nextSortFor = (column, currentSort) => {
    const current = parseSort(currentSort);
    const direction =
        current.field === column.sortField
            ? current.direction === 'asc'
                ? 'desc'
                : 'asc'
            : column.defaultDirection;
    return direction === 'desc' ? `-${column.sortField}` : column.sortField;
};

const NearestCell = ({ classes, row }) => {
    if (!row.nearest) {
        return (
            <span className={classes.muted}>
                {CANDIDATE_LIST_COPY.nearestNone}
            </span>
        );
    }
    return (
        <>
            <Link
                to={makeFacilityDetailLink(row.nearest.osId)}
                className={classes.osIdLink}
                onClick={event => event.stopPropagation()}
                data-testid="candidate-nearest-link"
            >
                {row.nearest.osId}
            </Link>{' '}
            <span className={classes.muted}>
                {formatDistance(row.nearest.distanceM)}
            </span>
            {row.nearest.name && (
                <span className={classes.nearestName} title={row.nearest.name}>
                    {row.nearest.name}
                </span>
            )}
        </>
    );
};

NearestCell.propTypes = {
    classes: PropTypes.object.isRequired,
    row: PropTypes.object.isRequired,
};

/**
 * Paged table of candidates (OSDEV-3755). Sorting and paging are reported
 * upward; the page owns the query. Rows are selectable (the inline panel
 * opens for the selected one); the OS ID link goes to the candidate page
 * without selecting the row.
 */
const CandidateListTable = ({
    classes,
    rows,
    count,
    page,
    sort,
    loading,
    selectedOsId,
    onSelect,
    onSortChange,
    onPageChange,
}) => {
    const current = parseSort(sort);
    return (
        <Paper className={classes.root} elevation={0}>
            <div className={classes.scroll}>
                <Table data-testid="candidate-list-table">
                    <TableHead>
                        <TableRow>
                            {COLUMNS.map(column => (
                                <TableCell
                                    key={column.key}
                                    className={classes.headCell}
                                    sortDirection={
                                        column.sortField === current.field
                                            ? current.direction
                                            : false
                                    }
                                >
                                    {column.sortField ? (
                                        <TableSortLabel
                                            active={
                                                column.sortField ===
                                                current.field
                                            }
                                            direction={current.direction}
                                            onClick={() =>
                                                onSortChange(
                                                    nextSortFor(column, sort),
                                                )
                                            }
                                            data-testid={`candidate-sort-${column.sortField}`}
                                        >
                                            {column.label}
                                        </TableSortLabel>
                                    ) : (
                                        column.label
                                    )}
                                </TableCell>
                            ))}
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {rows.map(row => {
                            const selected = row.osId === selectedOsId;
                            const votes = totalVotes(row.validation.tally);
                            return (
                                <TableRow
                                    key={row.osId}
                                    hover
                                    selected={selected}
                                    className={`${classes.row} ${
                                        selected ? classes.rowSelected : ''
                                    }`}
                                    onClick={() => onSelect(row.osId)}
                                    data-testid="candidate-list-row"
                                    data-os-id={row.osId}
                                    data-state={row.validation.state}
                                    aria-selected={selected}
                                >
                                    <TableCell className={classes.cell}>
                                        <Link
                                            to={makeFacilityDetailLink(
                                                row.osId,
                                            )}
                                            className={classes.osIdLink}
                                            onClick={event =>
                                                event.stopPropagation()
                                            }
                                            data-testid="candidate-os-id-link"
                                        >
                                            {row.osId}
                                        </Link>
                                    </TableCell>
                                    <TableCell className={classes.cell}>
                                        {formatConfidence(row.confidence)}
                                    </TableCell>
                                    <TableCell className={classes.cell}>
                                        <CandidateStateChip
                                            state={row.validation.state}
                                        />
                                    </TableCell>
                                    <TableCell
                                        className={classes.cell}
                                        data-testid="candidate-row-tally"
                                    >
                                        {votes === 0
                                            ? CANDIDATE_LIST_COPY.noVotes
                                            : formatCandidateTally(
                                                  row.validation.tally,
                                              )}
                                    </TableCell>
                                    <TableCell className={classes.cell}>
                                        {row.nearbyCount}
                                    </TableCell>
                                    <TableCell className={classes.cell}>
                                        <NearestCell
                                            classes={classes}
                                            row={row}
                                        />
                                    </TableCell>
                                    <TableCell className={classes.cell}>
                                        {row.createdAt
                                            ? moment(row.createdAt).format('ll')
                                            : '—'}
                                    </TableCell>
                                    <TableCell className={classes.cell}>
                                        {row.countryCode || '—'}
                                    </TableCell>
                                </TableRow>
                            );
                        })}
                    </TableBody>
                </Table>
                {loading && (
                    <div
                        className={classes.loading}
                        data-testid="candidate-list-loading"
                    >
                        <CircularProgress size={28} />
                    </div>
                )}
            </div>
            {/* MUI's TablePagination clamps an out-of-range page and calls
                onChangePage with the clamp; before the first response the
                count is unknown, so a URL that starts on page 2 would be
                pulled back to page 1. Hold the control until the count is in. */}
            {!(loading && count === 0) && (
                <TablePagination
                    component="div"
                    count={count}
                    page={Math.max(0, page - 1)}
                    rowsPerPage={CANDIDATE_LIST_PAGE_SIZE}
                    rowsPerPageOptions={[CANDIDATE_LIST_PAGE_SIZE]}
                    onChangePage={(_, zeroBasedPage) =>
                        onPageChange(zeroBasedPage + 1)
                    }
                    backIconButtonProps={{ 'aria-label': 'Previous page' }}
                    nextIconButtonProps={{ 'aria-label': 'Next page' }}
                />
            )}
        </Paper>
    );
};

CandidateListTable.propTypes = {
    classes: PropTypes.object.isRequired,
    rows: PropTypes.arrayOf(
        PropTypes.shape({
            osId: PropTypes.string.isRequired,
            confidence: PropTypes.number,
            validation: PropTypes.shape({
                state: PropTypes.string,
                tally: PropTypes.object,
            }).isRequired,
            nearbyCount: PropTypes.number,
            nearest: PropTypes.shape({
                osId: PropTypes.string,
                name: PropTypes.string,
                distanceM: PropTypes.number,
            }),
            createdAt: PropTypes.string,
            countryCode: PropTypes.string,
        }),
    ).isRequired,
    count: PropTypes.number.isRequired,
    page: PropTypes.number.isRequired,
    sort: PropTypes.string.isRequired,
    loading: PropTypes.bool,
    selectedOsId: PropTypes.string,
    onSelect: PropTypes.func.isRequired,
    onSortChange: PropTypes.func.isRequired,
    onPageChange: PropTypes.func.isRequired,
};

CandidateListTable.defaultProps = {
    loading: false,
    selectedOsId: null,
};

export default withStyles(candidateListTableStyles)(CandidateListTable);
