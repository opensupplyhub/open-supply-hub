import React from 'react';
import { Link } from 'react-router-dom';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';

import { useDashboardListMatchReport } from './hooks';
import { formatCount } from './utils';
import { formatDate, makeFacilityListItemsDetailLink } from '../../util/util';
import { DATE_FORMATS } from '../../util/constants';
import styles from './styles';

const COUNT_COLUMNS = Object.freeze([
    Object.freeze({ key: 'total', label: 'Rows' }),
    Object.freeze({ key: 'matched_existing', label: 'Matched existing' }),
    Object.freeze({ key: 'new_locations', label: 'New to OS Hub' }),
    Object.freeze({ key: 'needs_review', label: 'To confirm' }),
    Object.freeze({ key: 'failed', label: 'Failed' }),
    Object.freeze({ key: 'duplicates', label: 'Duplicates' }),
    Object.freeze({ key: 'removed', label: 'Removed' }),
    Object.freeze({ key: 'in_progress', label: 'Processing' }),
]);

/*
 * What became of each row of the lists the organization uploaded. A
 * list's own page is only open to the account that uploaded it, so the
 * name is a link for that member alone; `ownContributorID` is the
 * signed-in member's contributor id.
 */
const DashboardListMatchReport = ({ organizationUUID, ownContributorID }) => {
    const { lists, loaded, error } = useDashboardListMatchReport(
        organizationUUID,
    );

    return (
        <div style={styles.section} data-testid="dashboard-list-match-report">
            <h3 style={styles.sectionTitle}>List match report</h3>
            <p style={styles.sectionHint}>
                For each uploaded list, how many rows matched a production
                location OS Hub already had and how many were new. Rows &quot;to
                confirm&quot; wait for the uploader to accept or reject a
                possible match.
            </p>
            {error && <p style={styles.error}>{error}</p>}
            {loaded && lists.length === 0 && (
                <p style={styles.meta}>
                    Your organization has not uploaded a list yet.
                </p>
            )}
            {lists.length > 0 && (
                <div style={styles.tableWrapper}>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell padding="dense">List</TableCell>
                                <TableCell padding="dense">Uploaded</TableCell>
                                <TableCell padding="dense">By</TableCell>
                                {COUNT_COLUMNS.map(column => (
                                    <TableCell
                                        key={column.key}
                                        numeric
                                        padding="dense"
                                    >
                                        {column.label}
                                    </TableCell>
                                ))}
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {lists.map(list => {
                                const isOwn =
                                    list.submitted_by &&
                                    ownContributorID !== null &&
                                    list.submitted_by.contributor_id ===
                                        ownContributorID;
                                return (
                                    <TableRow key={list.id}>
                                        <TableCell padding="dense">
                                            {isOwn ? (
                                                <Link
                                                    to={makeFacilityListItemsDetailLink(
                                                        list.id,
                                                    )}
                                                >
                                                    {list.name}
                                                </Link>
                                            ) : (
                                                list.name
                                            )}
                                            {!list.is_active && (
                                                <span style={styles.meta}>
                                                    {' '}
                                                    (replaced or inactive)
                                                </span>
                                            )}
                                        </TableCell>
                                        <TableCell
                                            padding="dense"
                                            style={styles.noWrap}
                                        >
                                            {formatDate(
                                                list.uploaded_at,
                                                DATE_FORMATS.LONG,
                                            )}
                                        </TableCell>
                                        <TableCell padding="dense">
                                            {list.submitted_by
                                                ? list.submitted_by
                                                      .contributor_name
                                                : ''}
                                        </TableCell>
                                        {COUNT_COLUMNS.map(column => (
                                            <TableCell
                                                key={column.key}
                                                numeric
                                                padding="dense"
                                            >
                                                {formatCount(list[column.key])}
                                            </TableCell>
                                        ))}
                                    </TableRow>
                                );
                            })}
                        </TableBody>
                    </Table>
                </div>
            )}
        </div>
    );
};

export default DashboardListMatchReport;
