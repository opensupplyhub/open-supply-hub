import React, { useState } from 'react';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import Button from '@material-ui/core/Button';
import CircularProgress from '@material-ui/core/CircularProgress';
import MenuItem from '@material-ui/core/MenuItem';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import TextField from '@material-ui/core/TextField';

import AppGrid from '../AppGrid';
import AppOverflow from '../AppOverflow';
import RequireAuthNotice from '../RequireAuthNotice';
import BarList from './BarList';
import DashboardFacilityDialog from './DashboardFacilityDialog';
import DashboardListMatchReport from './DashboardListMatchReport';
import DashboardRecentlyViewed from './DashboardRecentlyViewed';
import DashboardUsage from './DashboardUsage';
import Pager from './Pager';
import {
    useCurrentOrganization,
    useDashboardFacilities,
    useDashboardSummary,
    useOrganizationMembers,
} from './hooks';
import {
    CLAIMED_FILTER,
    DASHBOARD_PAGE_SIZE,
    DEFAULT_DASHBOARD_FILTERS,
    monthLabel,
    percentOf,
} from './utils';
import { formatDate } from '../../util/util';
import {
    DATE_FORMATS,
    USER_DEFAULT_STATE,
    organizationRoute,
} from '../../util/constants';
import styles from './styles';

const TITLE = 'Organization dashboard';

const Tile = ({ value, label }) => (
    <div style={styles.card}>
        <div style={styles.tileValue}>{value}</div>
        <p style={styles.tileLabel}>{label}</p>
    </div>
);

const Notice = ({ children }) => (
    <AppGrid title={TITLE}>
        <div style={styles.emptyState}>{children}</div>
    </AppGrid>
);

/*
 * Totals, breakdowns and the table of submitted production locations
 * for one organization. Rendered only once the organization is known
 * and its dashboard is switched on.
 */
const DashboardContent = ({ organization, userID }) => {
    const [filters, setFilters] = useState(DEFAULT_DASHBOARD_FILTERS);
    const [page, setPage] = useState(1);
    const [openOsID, setOpenOsID] = useState(null);

    const { members } = useOrganizationMembers(organization.uuid);
    const {
        summary,
        fetching: fetchingSummary,
        error: summaryError,
    } = useDashboardSummary(organization.uuid, filters);
    const {
        rows,
        count,
        fetching: fetchingRows,
        error: rowsError,
    } = useDashboardFacilities(organization.uuid, filters, page);

    // A list's own page is only open to whoever uploaded it, so the
    // match report links a list for that member alone.
    const self = members.find(member => member.is_self);
    const ownContributorID = self ? self.contributor_id : null;

    // Every filter change starts the table again from its first page.
    const setFilter = name => event => {
        setFilters({ ...filters, [name]: event.target.value });
        setPage(1);
    };

    const resetFilters = () => {
        setFilters(DEFAULT_DASHBOARD_FILTERS);
        setPage(1);
    };

    return (
        <div style={styles.root} data-testid="organization-dashboard">
            <div style={styles.headerRow}>
                <div>
                    <h2 style={styles.organizationName}>{organization.name}</h2>
                    <p style={styles.meta}>
                        Production locations your organization&apos;s members
                        submitted, including what they submitted before joining.
                    </p>
                </div>
                <Button component={Link} to={organizationRoute}>
                    Back to organization
                </Button>
            </div>

            <div style={styles.filters}>
                <TextField
                    id="dashboard-filter-member"
                    select
                    label="Member"
                    value={filters.member}
                    onChange={setFilter('member')}
                    style={styles.filterField}
                    SelectProps={{ displayEmpty: true }}
                    InputLabelProps={{ shrink: true }}
                >
                    <MenuItem value="">All members</MenuItem>
                    {members
                        .filter(member => member.contributor_id)
                        .map(member => (
                            <MenuItem
                                key={member.uuid}
                                value={String(member.contributor_id)}
                            >
                                {member.contributor_name} ({member.email})
                            </MenuItem>
                        ))}
                </TextField>
                <TextField
                    id="dashboard-filter-date-from"
                    label="Submitted from"
                    type="date"
                    value={filters.dateFrom}
                    onChange={setFilter('dateFrom')}
                    InputLabelProps={{ shrink: true }}
                />
                <TextField
                    id="dashboard-filter-date-to"
                    label="Submitted to"
                    type="date"
                    value={filters.dateTo}
                    onChange={setFilter('dateTo')}
                    InputLabelProps={{ shrink: true }}
                />
                <TextField
                    id="dashboard-filter-claimed"
                    select
                    label="Claim status"
                    value={filters.claimed}
                    onChange={setFilter('claimed')}
                    style={styles.filterField}
                >
                    <MenuItem value={CLAIMED_FILTER.ALL}>
                        Claimed and unclaimed
                    </MenuItem>
                    <MenuItem value={CLAIMED_FILTER.CLAIMED}>
                        Claimed only
                    </MenuItem>
                    <MenuItem value={CLAIMED_FILTER.UNCLAIMED}>
                        Unclaimed only
                    </MenuItem>
                </TextField>
                <Button onClick={resetFilters}>Reset</Button>
            </div>

            {summaryError && <p style={styles.error}>{summaryError}</p>}
            {!summary && fetchingSummary && <CircularProgress />}
            {summary && (
                <>
                    <div style={styles.tiles} data-testid="dashboard-tiles">
                        <Tile
                            value={summary.total_facilities}
                            label="Production locations submitted"
                        />
                        <Tile
                            value={summary.total_submissions}
                            label="Submissions"
                        />
                        <Tile
                            value={`${summary.claimed_facilities} (${percentOf(
                                summary.claimed_facilities,
                                summary.total_facilities,
                            )}%)`}
                            label="Claimed"
                        />
                        <Tile
                            value={summary.unclaimed_facilities}
                            label="Not claimed yet"
                        />
                        <Tile
                            value={summary.pending_moderation}
                            label="Contributions awaiting moderation"
                        />
                    </div>
                    <div style={styles.charts}>
                        <BarList
                            title="Submissions per month"
                            rows={summary.by_month.map(row => ({
                                label: monthLabel(row.month),
                                value: row.submissions,
                            }))}
                        />
                        <BarList
                            title="Production locations by member"
                            rows={summary.by_member.map(row => ({
                                label: row.contributor_name,
                                value: row.facilities,
                            }))}
                        />
                        <BarList
                            title="Production locations by country"
                            rows={summary.by_country.map(row => ({
                                label: row.country_name,
                                value: row.facilities,
                            }))}
                        />
                        <BarList
                            title="Production locations by sector"
                            rows={summary.by_sector.map(row => ({
                                label: row.sector,
                                value: row.facilities,
                            }))}
                        />
                        <BarList
                            title="How they were submitted"
                            rows={[
                                {
                                    label: 'Lists',
                                    value:
                                        summary.by_source_type.list.submissions,
                                },
                                {
                                    label: 'Single contributions',
                                    value:
                                        summary.by_source_type.single
                                            .submissions,
                                },
                            ]}
                        />
                    </div>
                </>
            )}

            <div style={styles.section}>
                <h3 style={styles.sectionTitle}>
                    Submitted production locations
                </h3>
                <p style={styles.sectionHint}>
                    One row per production location and submission, newest
                    first. Open a row to see the data its claimant added.
                </p>
                {rowsError && <p style={styles.error}>{rowsError}</p>}
                <div style={styles.tableWrapper}>
                    <Table data-testid="dashboard-facilities-table">
                        <TableHead>
                            <TableRow>
                                <TableCell>Production location</TableCell>
                                <TableCell>OS ID</TableCell>
                                <TableCell>Country</TableCell>
                                <TableCell>Submitted by</TableCell>
                                <TableCell>Submitted</TableCell>
                                <TableCell>Through</TableCell>
                                <TableCell>Claimed</TableCell>
                                <TableCell />
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {rows.length === 0 && !fetchingRows && (
                                <TableRow>
                                    <TableCell colSpan={8}>
                                        No production locations match these
                                        filters.
                                    </TableCell>
                                </TableRow>
                            )}
                            {rows.map(row => (
                                <TableRow key={row.submission_id}>
                                    <TableCell>{row.name}</TableCell>
                                    <TableCell>{row.os_id}</TableCell>
                                    <TableCell>{row.country_name}</TableCell>
                                    <TableCell>
                                        {row.submitted_by
                                            ? row.submitted_by.contributor_name
                                            : ''}
                                    </TableCell>
                                    <TableCell style={styles.noWrap}>
                                        {formatDate(
                                            row.submitted_at,
                                            DATE_FORMATS.LONG,
                                        )}
                                    </TableCell>
                                    <TableCell>
                                        {row.list
                                            ? row.list.name
                                            : 'Single contribution'}
                                    </TableCell>
                                    <TableCell>
                                        {row.is_claimed ? (
                                            <span style={styles.chipClaimed}>
                                                {row.claimed_at
                                                    ? `Since ${formatDate(
                                                          row.claimed_at,
                                                          DATE_FORMATS.LONG,
                                                      )}`
                                                    : 'Yes'}
                                            </span>
                                        ) : (
                                            'No'
                                        )}
                                    </TableCell>
                                    <TableCell>
                                        <Button
                                            size="small"
                                            onClick={() =>
                                                setOpenOsID(row.os_id)
                                            }
                                        >
                                            Details
                                        </Button>
                                    </TableCell>
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
                    disabled={fetchingRows}
                />
            </div>

            <DashboardListMatchReport
                organizationUUID={organization.uuid}
                ownContributorID={ownContributorID}
            />
            <DashboardUsage organizationUUID={organization.uuid} />
            <DashboardRecentlyViewed userID={userID} />

            {openOsID && (
                <DashboardFacilityDialog
                    organizationUUID={organization.uuid}
                    osID={openOsID}
                    onClose={() => setOpenOsID(null)}
                />
            )}
        </div>
    );
};

/*
 * The paid organization dashboard page. Every member of an organization
 * whose dashboard OS Hub has switched on can open it; everyone else is
 * told why they can't.
 */
function OrganizationDashboard({ user, fetchingSessionSignIn }) {
    const signedIn = !fetchingSessionSignIn && !user.isAnon;

    if (fetchingSessionSignIn) {
        return (
            <AppGrid title={TITLE}>
                <CircularProgress />
            </AppGrid>
        );
    }

    if (!signedIn) {
        return (
            <RequireAuthNotice
                title={TITLE}
                text="Log in to see your organization's dashboard"
            />
        );
    }

    return <SignedInDashboard userID={user.id} />;
}

function SignedInDashboard({ userID }) {
    const { organization, loaded, error } = useCurrentOrganization();

    if (error) return <Notice>{error}</Notice>;

    if (!loaded) {
        return (
            <AppGrid title={TITLE}>
                <CircularProgress />
            </AppGrid>
        );
    }

    if (!organization) {
        return (
            <Notice>
                You don&apos;t belong to an organization, so there is no
                dashboard to show. Organizations are set up by the Open Supply
                Hub team.
            </Notice>
        );
    }

    if (!organization.dashboard_enabled) {
        return (
            <Notice>
                The dashboard is a paid add-on and is not switched on for{' '}
                {organization.name}. Contact Open Supply Hub to enable it.{' '}
                <Link to={organizationRoute}>Back to organization</Link>
            </Notice>
        );
    }

    return (
        <AppOverflow>
            <AppGrid title={TITLE}>
                <DashboardContent organization={organization} userID={userID} />
            </AppGrid>
        </AppOverflow>
    );
}

OrganizationDashboard.defaultProps = {
    user: USER_DEFAULT_STATE,
};

function mapStateToProps({
    auth: {
        user: { user },
        session: { fetching },
    },
}) {
    return {
        user,
        fetchingSessionSignIn: fetching,
    };
}

export default connect(mapStateToProps)(OrganizationDashboard);
