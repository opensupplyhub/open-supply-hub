import React, { useState } from 'react';
import Button from '@material-ui/core/Button';
import CircularProgress from '@material-ui/core/CircularProgress';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';

import Pager from './Pager';
import { useOrganizationContributions } from './hooks';
import {
    CONTRIBUTION_TYPES,
    CONTRIBUTION_TYPE_LABELS,
    DASHBOARD_PAGE_SIZE,
} from './utils';
import { formatDate } from '../../util/util';
import { DATE_FORMATS } from '../../util/constants';
import styles from './styles';

const submitter = row =>
    row.submitted_by
        ? `${row.submitted_by.contributor_name} (${row.submitted_by.email})`
        : '';

const submittedOn = row => formatDate(row.created_at, DATE_FORMATS.LONG);

/* Columns per contribution type: [header, cell renderer]. */
const COLUMNS = Object.freeze({
    [CONTRIBUTION_TYPES.LISTS]: [
        ['List', row => row.name],
        ['Status', row => row.status],
        ['Submitted by', submitter],
        ['Submitted', submittedOn],
    ],
    [CONTRIBUTION_TYPES.CONTRIBUTIONS]: [
        ['Production location', row => row.name || row.os_id || ''],
        ['Country', row => row.country_code || ''],
        ['Type', row => row.request_type],
        ['Status', row => row.status],
        ['Submitted by', submitter],
        ['Submitted', submittedOn],
    ],
    [CONTRIBUTION_TYPES.CLAIMS]: [
        ['Production location', row => row.facility_name],
        ['OS ID', row => row.os_id],
        ['Status', row => row.status],
        ['Submitted by', submitter],
        ['Submitted', submittedOn],
    ],
});

const rowKey = row => row.id || row.moderation_id;

/*
 * A read-only list of what the organization's members submitted, with
 * who submitted each. It never offers edits: managing a list or a claim
 * stays with the account that owns it.
 */
const OrganizationContributions = ({ organization }) => {
    const [type, setType] = useState(CONTRIBUTION_TYPES.LISTS);
    const [page, setPage] = useState(1);
    const { rows, count, fetching, error } = useOrganizationContributions(
        organization.uuid,
        type,
        page,
    );
    const columns = COLUMNS[type];

    const changeType = nextType => {
        setType(nextType);
        setPage(1);
    };

    return (
        <div style={styles.section} data-testid="organization-contributions">
            <h3 style={styles.sectionTitle}>Contributions</h3>
            <p style={styles.sectionHint}>
                Everything members submitted for the organization, including
                what they submitted before joining.
            </p>
            <div style={styles.subTabs}>
                {Object.values(CONTRIBUTION_TYPES).map(value => (
                    <Button
                        key={value}
                        size="small"
                        variant={value === type ? 'contained' : 'outlined'}
                        color={value === type ? 'primary' : 'default'}
                        onClick={() => changeType(value)}
                    >
                        {CONTRIBUTION_TYPE_LABELS[value]}
                    </Button>
                ))}
            </div>
            {error && <p style={styles.error}>{error}</p>}
            {fetching && !rows.length ? (
                <CircularProgress />
            ) : (
                <>
                    <div style={styles.tableWrapper}>
                        <Table>
                            <TableHead>
                                <TableRow>
                                    {columns.map(([header]) => (
                                        <TableCell key={header}>
                                            {header}
                                        </TableCell>
                                    ))}
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {rows.length === 0 && (
                                    <TableRow>
                                        <TableCell colSpan={columns.length}>
                                            Nothing submitted yet.
                                        </TableCell>
                                    </TableRow>
                                )}
                                {rows.map(row => (
                                    <TableRow key={rowKey(row)}>
                                        {columns.map(([header, render]) => (
                                            <TableCell key={header}>
                                                {render(row)}
                                            </TableCell>
                                        ))}
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </div>
                    <Pager
                        page={page}
                        pageSize={DASHBOARD_PAGE_SIZE}
                        count={count}
                        onChange={setPage}
                        disabled={fetching}
                    />
                </>
            )}
        </div>
    );
};

export default OrganizationContributions;
