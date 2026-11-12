import React from 'react';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';

import { useDashboardUsage } from './hooks';
import { apiLimitLabel, formatCount } from './utils';
import styles from './styles';

const Tile = ({ value, label }) => (
    <div style={styles.card}>
        <div style={styles.tileValue}>{value}</div>
        <p style={styles.tileLabel}>{label}</p>
    </div>
);

/*
 * Downloads and API calls of the organization's current members. Each
 * member has their own download allowance and API limit; the totals
 * only add up what the members did, nothing is pooled.
 */
const DashboardUsage = ({ organizationUUID }) => {
    const { usage, error } = useDashboardUsage(organizationUUID);

    return (
        <div style={styles.section} data-testid="dashboard-usage">
            <h3 style={styles.sectionTitle}>Download and API usage</h3>
            <p style={styles.sectionHint}>
                What your organization&apos;s current members downloaded and how
                often they called the API
                {usage ? ` in the last ${usage.period_days} days` : ''}. Each
                member has their own download allowance and API limit.
            </p>
            {error && <p style={styles.error}>{error}</p>}
            {usage && (
                <>
                    <div
                        style={styles.tiles}
                        data-testid="dashboard-usage-tiles"
                    >
                        <Tile
                            value={formatCount(usage.totals.downloads)}
                            label="Downloads"
                        />
                        <Tile
                            value={formatCount(usage.totals.downloaded_records)}
                            label="Records downloaded"
                        />
                        <Tile
                            value={formatCount(usage.totals.api_calls)}
                            label="API calls"
                        />
                    </div>
                    <div style={styles.tableWrapper}>
                        <Table>
                            <TableHead>
                                <TableRow>
                                    <TableCell>Member</TableCell>
                                    <TableCell numeric>Downloads</TableCell>
                                    <TableCell numeric>
                                        Records downloaded
                                    </TableCell>
                                    <TableCell numeric>
                                        Records this year
                                    </TableCell>
                                    <TableCell numeric>
                                        Free records left
                                    </TableCell>
                                    <TableCell numeric>
                                        Paid records left
                                    </TableCell>
                                    <TableCell numeric>API calls</TableCell>
                                    <TableCell>API limit used</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {usage.members.map(member => (
                                    <TableRow key={member.membership_uuid}>
                                        <TableCell>
                                            {member.contributor_name ||
                                                member.email}
                                            <div style={styles.meta}>
                                                {member.email}
                                            </div>
                                        </TableCell>
                                        <TableCell numeric>
                                            {formatCount(
                                                member.downloads.count,
                                            )}
                                        </TableCell>
                                        <TableCell numeric>
                                            {formatCount(
                                                member.downloads.records,
                                            )}
                                        </TableCell>
                                        <TableCell numeric>
                                            {formatCount(
                                                member.downloads
                                                    .records_this_year,
                                            )}
                                        </TableCell>
                                        <TableCell numeric>
                                            {formatCount(
                                                member.downloads
                                                    .free_records_left,
                                            )}
                                        </TableCell>
                                        <TableCell numeric>
                                            {formatCount(
                                                member.downloads
                                                    .paid_records_left,
                                            )}
                                        </TableCell>
                                        <TableCell numeric>
                                            {member.api
                                                ? formatCount(member.api.calls)
                                                : '–'}
                                        </TableCell>
                                        <TableCell>
                                            {apiLimitLabel(member.api)}
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </div>
                </>
            )}
        </div>
    );
};

export default DashboardUsage;
