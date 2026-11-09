import React, { useEffect, useState } from 'react';
import { arrayOf, bool, func, number, object, shape, string } from 'prop-types';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { withStyles } from '@material-ui/core/styles';
import { CopyToClipboard } from 'react-copy-to-clipboard';
import moment from 'moment';
import Button from '@material-ui/core/Button';
import Chip from '@material-ui/core/Chip';
import CircularProgress from '@material-ui/core/CircularProgress';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import MenuItem from '@material-ui/core/MenuItem';
import Paper from '@material-ui/core/Paper';
import Select from '@material-ui/core/Select';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableFooter from '@material-ui/core/TableFooter';
import TableHead from '@material-ui/core/TableHead';
import TablePagination from '@material-ui/core/TablePagination';
import TableRow from '@material-ui/core/TableRow';
import TableSortLabel from '@material-ui/core/TableSortLabel';
import Typography from '@material-ui/core/Typography';
import InfoOutlined from '@material-ui/icons/InfoOutlined';
import KeyboardArrowRight from '@material-ui/icons/KeyboardArrowRight';

import AppOverflow from '../AppOverflow';
import RequireAuthNotice from '../RequireAuthNotice';
import StyledTooltip from '../StyledTooltip';
import { fetchClaimCampaigns } from '../../actions/claimCampaigns';
import apiRequest from '../../util/apiRequest';
import {
    claimCampaignsRoute,
    claimIntroRoute,
    makeClaimCampaignCandidatesURL,
    makeClaimCampaignRoute,
    makeCloseClaimCampaignURL,
    newClaimCampaignRoute,
} from '../../util/constants';
import {
    hasClaimCampaignAccess,
    DownloadCSV,
    joinDataIntoCSVString,
} from '../../util/util';
import COLOURS from '../../util/COLOURS';
import { claimCampaignsStyles } from './styles';

const STATUS_LABELS = Object.freeze({
    claimed: 'Claimed',
    pending: 'Pending review',
    unclaimed: 'Not started',
});

const STATUS_COLORS = Object.freeze({
    claimed: COLOURS.MATERIAL_GREEN,
    pending: COLOURS.ORANGE,
    unclaimed: COLOURS.DARK_GREY,
});

const STATUS_ORDER = Object.freeze(['claimed', 'pending', 'unclaimed']);

const ROWS_PER_PAGE_OPTIONS = Object.freeze([10, 25, 50, 100]);

const SORT_DIRECTIONS = Object.freeze({ asc: 'asc', desc: 'desc' });

const compareText = (a, b) =>
    (a || '').localeCompare(b || '', undefined, {
        sensitivity: 'base',
        numeric: true,
    });

const statusRank = status => {
    const rank = STATUS_ORDER.indexOf(status);
    return rank === -1 ? STATUS_ORDER.length : rank;
};

// The sortable supplier columns. Claim status sorts by progress
// (Claimed, Pending review, Not started), not alphabetically.
const SUPPLIER_SORTS = Object.freeze({
    name: (a, b) => compareText(a.name, b.name),
    country: (a, b) => compareText(a.country_code, b.country_code),
    status: (a, b) => statusRank(a.claim_status) - statusRank(b.claim_status),
});

// Ties always break by facility name A–Z (then OS ID), whichever way
// the chosen column runs, so the order is stable and predictable.
const breakTies = (a, b) =>
    compareText(a.name, b.name) || compareText(a.os_id, b.os_id);

export const sortSuppliers = (suppliers, orderBy, order) => {
    const compare = SUPPLIER_SORTS[orderBy];
    if (!compare) {
        return suppliers;
    }
    const sign = order === SORT_DIRECTIONS.desc ? -1 : 1;
    return [...suppliers].sort(
        (a, b) => sign * compare(a, b) || breakTies(a, b),
    );
};

const CONTACT_COLUMN_HELP =
    'Copy the link and send it to your contact at the facility, or download the CSV of all links. Each link is unique to one facility, so make sure you send each facility its own link.';

const campaignPropType = shape({
    id: number.isRequired,
    code: string.isRequired,
    name: string.isRequired,
    status: string.isRequired,
    created_at: string.isRequired,
    suppliers: arrayOf(
        shape({
            os_id: string.isRequired,
            name: string.isRequired,
            country_code: string.isRequired,
            claim_status: string.isRequired,
        }),
    ).isRequired,
});

const makeCampaignClaimLink = (osID, code) =>
    `${window.location.origin}${claimIntroRoute.replace(
        ':osID',
        osID,
    )}?campaign=${code}`;

// Spreadsheet apps run a cell starting with = + - @ (or a tab/CR) as a
// formula. Facility names come from any contributor's uploads, so prefix
// such cells with an apostrophe to keep them plain text.
export const neutralizeCSVFormula = value =>
    /^[=+\-@\t\r]/.test(value) ? `'${value}` : value;

// Exports the rows currently shown, in the order shown, so filtering to
// "Not started" first yields exactly the outreach list.
const downloadSupplierCSV = (campaign, suppliers) =>
    DownloadCSV(
        joinDataIntoCSVString([
            [
                'facility_name',
                'os_id',
                'country_code',
                'claim_status',
                'claim_link',
            ],
            ...suppliers.map(s => [
                neutralizeCSVFormula(s.name),
                s.os_id,
                s.country_code,
                STATUS_LABELS[s.claim_status] || s.claim_status,
                makeCampaignClaimLink(s.os_id, campaign.code),
            ]),
        ]),
        `${campaign.code}_suppliers.csv`,
    );

const StatusSquare = ({ status, classes }) => (
    <span
        className={classes.statusSquare}
        style={{ backgroundColor: STATUS_COLORS[status] }}
    />
);

StatusSquare.propTypes = {
    status: string.isRequired,
    classes: object.isRequired,
};

const SupplierStatusChip = ({ status, classes }) => (
    <Chip
        label={
            <span className={classes.chipContent}>
                <span
                    className={classes.statusDot}
                    style={{ backgroundColor: STATUS_COLORS[status] }}
                />
                {STATUS_LABELS[status] || status}
            </span>
        }
        className={
            {
                claimed: classes.statusClaimed,
                pending: classes.statusPending,
            }[status] || classes.statusUnclaimed
        }
    />
);

SupplierStatusChip.propTypes = {
    status: string.isRequired,
    classes: object.isRequired,
};

const SortableHeader = ({
    column,
    label,
    orderBy,
    order,
    onSort,
    className,
}) => (
    <TableCell
        className={className}
        sortDirection={orderBy === column ? order : false}
    >
        <TableSortLabel
            active={orderBy === column}
            direction={orderBy === column ? order : SORT_DIRECTIONS.asc}
            onClick={() => onSort(column)}
        >
            {label}
        </TableSortLabel>
    </TableCell>
);

SortableHeader.defaultProps = {
    orderBy: null,
};

SortableHeader.propTypes = {
    column: string.isRequired,
    label: string.isRequired,
    orderBy: string,
    order: string.isRequired,
    onSort: func.isRequired,
    className: string.isRequired,
};

const KpiTile = ({ value, label, status, classes }) => (
    <div className={classes.kpiTile}>
        <span className={classes.kpiValue}>{value}</span>
        <span className={classes.kpiLabel}>
            {status && <StatusSquare status={status} classes={classes} />}
            {label}
        </span>
    </div>
);

KpiTile.defaultProps = {
    status: null,
};

KpiTile.propTypes = {
    value: number.isRequired,
    label: string.isRequired,
    status: string,
    classes: object.isRequired,
};

// Asks before closing: a closed campaign stops counting new claims and
// can't send invites, and brands can't reopen it themselves.
export const CloseCampaignDialog = ({
    open,
    campaign,
    closing,
    error,
    onCancel,
    onConfirm,
}) => (
    <Dialog open={open} onClose={closing ? undefined : onCancel}>
        <DialogTitle>Close {campaign.name}?</DialogTitle>
        <DialogContent>
            <DialogContentText>
                Once it&apos;s closed, new claims from these suppliers
                won&apos;t count toward this campaign, and you can&apos;t send
                invites from it. Claims already made stay in its numbers. To
                reopen it, contact the OS Hub team.
            </DialogContentText>
            {error && (
                <DialogContentText color="error" role="alert">
                    {error}
                </DialogContentText>
            )}
        </DialogContent>
        <DialogActions>
            <Button onClick={onCancel} disabled={closing}>
                Keep it open
            </Button>
            <Button onClick={onConfirm} color="primary" disabled={closing}>
                {closing ? 'Closing…' : 'Close campaign'}
            </Button>
        </DialogActions>
    </Dialog>
);

CloseCampaignDialog.defaultProps = {
    error: null,
};

CloseCampaignDialog.propTypes = {
    open: bool.isRequired,
    campaign: shape({ name: string.isRequired }).isRequired,
    closing: bool.isRequired,
    error: string,
    onCancel: func.isRequired,
    onConfirm: func.isRequired,
};

// Counts per public claim status, the total and the share claimed.
export const summarizeCampaign = campaign => {
    const counts = { claimed: 0, pending: 0, unclaimed: 0 };
    campaign.suppliers.forEach(s => {
        counts[s.claim_status] = (counts[s.claim_status] || 0) + 1;
    });
    const total = campaign.suppliers.length;
    const percentClaimed = total
        ? Math.round((counts.claimed / total) * 100)
        : 0;
    return { counts, total, percentClaimed };
};

const CampaignProgress = ({ campaign, classes }) => {
    const { counts, total, percentClaimed } = summarizeCampaign(campaign);
    return (
        <div className={classes.progressPanel}>
            <div className={classes.progressHeader}>
                <Typography className={classes.progressTitle}>
                    Campaign progress
                </Typography>
                <Typography className={classes.campaignMeta}>
                    {percentClaimed}% of suppliers claimed
                </Typography>
            </div>
            <div className={classes.segmentBar}>
                {STATUS_ORDER.map(
                    status =>
                        counts[status] > 0 && (
                            <span
                                key={status}
                                className={classes.segment}
                                style={{
                                    width: `${(counts[status] / total) * 100}%`,
                                    backgroundColor: STATUS_COLORS[status],
                                }}
                            >
                                {counts[status]}
                            </span>
                        ),
                )}
            </div>
            <div className={classes.legend}>
                {STATUS_ORDER.map(status => (
                    <span key={status} className={classes.legendItem}>
                        <StatusSquare status={status} classes={classes} />
                        {STATUS_LABELS[status]} ({counts[status]})
                    </span>
                ))}
            </div>
        </div>
    );
};

CampaignProgress.propTypes = {
    campaign: campaignPropType.isRequired,
    classes: object.isRequired,
};

const CampaignMeta = ({ campaign, classes }) => (
    <Typography className={classes.campaignMeta}>
        {campaign.suppliers.length} suppliers ·{' '}
        {campaign.status === 'ACTIVE' ? 'Active' : 'Closed'} campaign · created{' '}
        {moment(campaign.created_at).format('D MMM YYYY')}
    </Typography>
);

CampaignMeta.propTypes = {
    campaign: campaignPropType.isRequired,
    classes: object.isRequired,
};

// One row of the dashboard roll-up shown when a brand has two or more
// campaigns: name, code, size and date, status, a thin progress bar and
// the share claimed. The name and the arrow open the campaign's own page.
export const CampaignRollupRow = ({ campaign, classes }) => {
    const { counts, total, percentClaimed } = summarizeCampaign(campaign);
    const isActive = campaign.status === 'ACTIVE';
    const route = makeClaimCampaignRoute(campaign.id);
    return (
        <div className={classes.rollupRow}>
            <div className={classes.rollupText}>
                <Link to={route} className={classes.campaignNameLink}>
                    {campaign.name}
                </Link>
                <Typography className={classes.campaignMeta}>
                    Code{' '}
                    <span className={classes.rollupCode}>{campaign.code}</span>{' '}
                    · {total} supplier{total === 1 ? '' : 's'} · created{' '}
                    {moment(campaign.created_at).format('D MMM YYYY')}
                </Typography>
            </div>
            <div className={classes.rollupStats}>
                <span
                    className={
                        isActive ? classes.activeChip : classes.closedChip
                    }
                >
                    {isActive ? 'Active' : 'Closed'}
                </span>
                <div
                    className={classes.miniBar}
                    role="img"
                    aria-label={STATUS_ORDER.map(
                        status => `${STATUS_LABELS[status]}: ${counts[status]}`,
                    ).join(', ')}
                >
                    {STATUS_ORDER.map(
                        status =>
                            counts[status] > 0 && (
                                <span
                                    key={status}
                                    style={{
                                        width: `${
                                            (counts[status] / total) * 100
                                        }%`,
                                        backgroundColor: STATUS_COLORS[status],
                                    }}
                                />
                            ),
                    )}
                </div>
                <span
                    className={classes.rollupPercent}
                    title="Share of suppliers claimed"
                >
                    {percentClaimed}%
                </span>
                <Link
                    to={route}
                    className={classes.rollupOpen}
                    aria-label={`Open ${campaign.name}`}
                >
                    <KeyboardArrowRight />
                </Link>
            </div>
        </div>
    );
};

CampaignRollupRow.propTypes = {
    campaign: campaignPropType.isRequired,
    classes: object.isRequired,
};

const CampaignCard = ({ campaign, onClosed, classes }) => {
    const isActive = campaign.status === 'ACTIVE';
    const [confirmClose, setConfirmClose] = useState(false);
    const [closing, setClosing] = useState(false);
    const [closeError, setCloseError] = useState(null);
    const closeCampaign = () => {
        setClosing(true);
        setCloseError(null);
        apiRequest
            .post(makeCloseClaimCampaignURL(campaign.id))
            .then(() => {
                setClosing(false);
                setConfirmClose(false);
                onClosed();
            })
            .catch(() => {
                setClosing(false);
                setCloseError(
                    'The campaign could not be closed. Please try again.',
                );
            });
    };
    const [statusFilter, setStatusFilter] = useState('ALL');
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(25);
    // Unsorted (server order, i.e. the order suppliers were added) until
    // the brand clicks a column header.
    const [orderBy, setOrderBy] = useState(null);
    const [order, setOrder] = useState(SORT_DIRECTIONS.asc);

    const { counts, total } = summarizeCampaign(campaign);

    const sortBy = column => {
        const reverse = orderBy === column && order === SORT_DIRECTIONS.asc;
        setOrder(reverse ? SORT_DIRECTIONS.desc : SORT_DIRECTIONS.asc);
        setOrderBy(column);
        setPage(0);
    };

    const suppliers = sortSuppliers(
        statusFilter === 'ALL'
            ? campaign.suppliers
            : campaign.suppliers.filter(s => s.claim_status === statusFilter),
        orderBy,
        order,
    );
    const pageSuppliers = suppliers.slice(
        page * rowsPerPage,
        page * rowsPerPage + rowsPerPage,
    );

    return (
        <Paper className={classes.campaignCard}>
            <div className={classes.campaignHeader}>
                <div>
                    <span className={classes.campaignName}>
                        {campaign.name}
                    </span>
                    <CampaignMeta campaign={campaign} classes={classes} />
                </div>
                <div className={classes.campaignActions}>
                    <div className={classes.codeBox}>
                        <span className={classes.codeLabel}>Campaign code</span>
                        <span className={classes.code}>{campaign.code}</span>
                        <CopyToClipboard text={campaign.code}>
                            <Button size="small" color="primary">
                                Copy
                            </Button>
                        </CopyToClipboard>
                    </div>
                    {isActive && (
                        <Button
                            size="small"
                            variant="outlined"
                            onClick={() => setConfirmClose(true)}
                        >
                            Close campaign
                        </Button>
                    )}
                </div>
            </div>
            {!isActive && (
                <Typography className={classes.closedNote} role="status">
                    This campaign is closed. New claims from these suppliers no
                    longer count toward it.
                </Typography>
            )}
            <CloseCampaignDialog
                open={confirmClose}
                campaign={campaign}
                closing={closing}
                error={closeError}
                onCancel={() => {
                    setConfirmClose(false);
                    setCloseError(null);
                }}
                onConfirm={closeCampaign}
            />

            <div className={classes.kpiRow}>
                <KpiTile
                    value={total}
                    label="Suppliers invited"
                    classes={classes}
                />
                {STATUS_ORDER.map(status => (
                    <KpiTile
                        key={status}
                        value={counts[status]}
                        label={STATUS_LABELS[status]}
                        status={status}
                        classes={classes}
                    />
                ))}
            </div>

            <CampaignProgress campaign={campaign} classes={classes} />

            <div className={classes.tableTools}>
                <h2 className={classes.sectionTitle}>Suppliers</h2>
                <div className={classes.tableToolsActions}>
                    <Select
                        value={statusFilter}
                        onChange={e => {
                            setStatusFilter(e.target.value);
                            setPage(0);
                        }}
                        aria-label="Filter by claim status"
                    >
                        <MenuItem value="ALL">All statuses</MenuItem>
                        <MenuItem value="claimed">Claimed</MenuItem>
                        <MenuItem value="pending">Pending review</MenuItem>
                        <MenuItem value="unclaimed">Not started</MenuItem>
                    </Select>
                    {/* The CSV is the links, for the brand's own mail merge. */}
                    <Button
                        variant="outlined"
                        color="primary"
                        onClick={() => downloadSupplierCSV(campaign, suppliers)}
                    >
                        Download CSV
                    </Button>
                </div>
            </div>

            <div className={classes.tableWrap}>
                <Table className={classes.supplierTable}>
                    <TableHead>
                        <TableRow>
                            <SortableHeader
                                column="name"
                                label="Facility"
                                orderBy={orderBy}
                                order={order}
                                onSort={sortBy}
                                className={classes.colFacility}
                            />
                            <TableCell className={classes.colOsId}>
                                OS ID
                            </TableCell>
                            <SortableHeader
                                column="country"
                                label="Country"
                                orderBy={orderBy}
                                order={order}
                                onSort={sortBy}
                                className={classes.colCountry}
                            />
                            <SortableHeader
                                column="status"
                                label="Claim status"
                                orderBy={orderBy}
                                order={order}
                                onSort={sortBy}
                                className={classes.colStatus}
                            />
                            <TableCell className={classes.colContact}>
                                <span className={classes.headerWithHelp}>
                                    Unique claim link
                                    <StyledTooltip
                                        title={CONTACT_COLUMN_HELP}
                                        placement="top"
                                    >
                                        <InfoOutlined
                                            className={classes.helpIcon}
                                            aria-label={CONTACT_COLUMN_HELP}
                                            tabIndex={0}
                                        />
                                    </StyledTooltip>
                                </span>
                            </TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {pageSuppliers.map(supplier => (
                            <TableRow key={supplier.os_id}>
                                <TableCell className={classes.cell}>
                                    {supplier.name}
                                </TableCell>
                                <TableCell className={classes.cell}>
                                    {supplier.os_id}
                                </TableCell>
                                <TableCell className={classes.cell}>
                                    {supplier.country_code}
                                </TableCell>
                                <TableCell className={classes.cell}>
                                    <SupplierStatusChip
                                        status={supplier.claim_status}
                                        classes={classes}
                                    />
                                    {supplier.is_closed && (
                                        <span
                                            className={classes.closedTag}
                                            title="This production location has closed since it was added."
                                        >
                                            Closed
                                        </span>
                                    )}
                                </TableCell>
                                <TableCell className={classes.cell}>
                                    <CopyToClipboard
                                        text={makeCampaignClaimLink(
                                            supplier.os_id,
                                            campaign.code,
                                        )}
                                    >
                                        <Button color="primary">
                                            Copy link
                                        </Button>
                                    </CopyToClipboard>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                    {suppliers.length > ROWS_PER_PAGE_OPTIONS[0] && (
                        <TableFooter>
                            <TableRow>
                                <TablePagination
                                    count={suppliers.length}
                                    page={page}
                                    rowsPerPage={rowsPerPage}
                                    rowsPerPageOptions={ROWS_PER_PAGE_OPTIONS}
                                    onChangePage={(_, newPage) =>
                                        setPage(newPage)
                                    }
                                    onChangeRowsPerPage={e => {
                                        setRowsPerPage(Number(e.target.value));
                                        setPage(0);
                                    }}
                                />
                            </TableRow>
                        </TableFooter>
                    )}
                </Table>
            </div>
        </Paper>
    );
};

CampaignCard.propTypes = {
    campaign: campaignPropType.isRequired,
    onClosed: func.isRequired,
    classes: object.isRequired,
};

const ClaimCampaigns = ({
    classes,
    userHasSignedIn,
    fetching,
    campaigns,
    error,
    fetchCampaigns,
    location,
    match,
    hasAccess,
}) => {
    // On /claim-campaigns/{id} the page shows that one campaign in full.
    const campaignID =
        match && match.params && match.params.campaignId
            ? Number(match.params.campaignId)
            : null;
    // Brands enabled for self-serve can reach the candidates endpoint;
    // everyone else gets a 404 and sees no "New campaign" button.
    const [canCreate, setCanCreate] = useState(false);

    useEffect(() => {
        if (userHasSignedIn && hasAccess) {
            fetchCampaigns();
            apiRequest
                .get(makeClaimCampaignCandidatesURL())
                .then(() => setCanCreate(true))
                .catch(() => setCanCreate(false));
        }
    }, [userHasSignedIn, hasAccess, fetchCampaigns]);

    const searchParams = new URLSearchParams(
        (location && location.search) || '',
    );
    const newCampaignID = Number(searchParams.get('new'));
    const leftOut = Number(searchParams.get('left_out')) || 0;
    const newCampaign =
        newCampaignID && campaigns
            ? campaigns.find(c => c.id === newCampaignID)
            : null;

    if (!userHasSignedIn) {
        return (
            <RequireAuthNotice
                title="Claims Campaigns"
                text="Log in to view your claims campaigns"
            />
        );
    }

    if (!hasAccess) {
        return (
            <AppOverflow>
                <div className={classes.container}>
                    <Typography
                        variant="title"
                        component="h1"
                        className={classes.title}
                    >
                        Claims Campaigns
                    </Typography>
                    <Typography className={classes.emptyMessage}>
                        Claims campaigns aren&apos;t turned on for your account.
                        They help brands invite their suppliers to claim their
                        production locations on OS Hub. To find out more,
                        contact your OS Hub account manager.
                    </Typography>
                </div>
            </AppOverflow>
        );
    }

    if (fetching) {
        return (
            <div className={classes.emptyMessage}>
                <CircularProgress />
            </div>
        );
    }

    if (error) {
        return (
            <Typography className={classes.emptyMessage}>
                An error prevented loading your claims campaigns.
            </Typography>
        );
    }

    const renderCard = campaign => (
        <CampaignCard
            key={campaign.id}
            campaign={campaign}
            onClosed={fetchCampaigns}
            classes={classes}
        />
    );

    if (campaignID !== null) {
        const campaign = (campaigns || []).find(c => c.id === campaignID);
        return (
            <AppOverflow>
                <div className={classes.container}>
                    <nav aria-label="Breadcrumb" className={classes.breadcrumb}>
                        <Link to={claimCampaignsRoute}>Claims Campaigns</Link>
                        <span aria-hidden="true"> › </span>
                        <span aria-current="page">
                            {campaign ? campaign.name : 'Campaign'}
                        </span>
                    </nav>
                    {campaign ? (
                        renderCard(campaign)
                    ) : (
                        <Typography className={classes.emptyMessage}>
                            This campaign wasn&apos;t found. It may belong to
                            another account.
                        </Typography>
                    )}
                </div>
            </AppOverflow>
        );
    }

    // With two or more campaigns the dashboard lists them collapsed, and
    // each opens on its own page; a single campaign is shown in full.
    const collapsed = !!campaigns && campaigns.length > 1;

    // Nothing yet, one campaign in full, or a roll-up of several.
    let campaignList;
    if (!campaigns || campaigns.length === 0) {
        campaignList = (
            <Typography className={classes.emptyMessage}>
                {canCreate
                    ? 'Your account has no claims campaigns yet. Use "New campaign" to invite suppliers from one of your lists.'
                    : 'Your account has no claims campaigns yet. Campaigns are created for you by the OS Hub team — contact your account manager to get started.'}
            </Typography>
        );
    } else if (collapsed) {
        campaignList = (
            <Paper className={classes.rollup}>
                {campaigns.map(campaign => (
                    <CampaignRollupRow
                        key={campaign.id}
                        campaign={campaign}
                        classes={classes}
                    />
                ))}
            </Paper>
        );
    } else {
        campaignList = campaigns.map(renderCard);
    }

    return (
        <AppOverflow>
            <div className={classes.container}>
                <div className={classes.pageHeader}>
                    <div>
                        <Typography
                            variant="title"
                            component="h1"
                            className={classes.title}
                        >
                            Claims Campaigns
                        </Typography>
                        <Typography className={classes.subtitle}>
                            Track which of your suppliers have claimed their
                            production location profiles.
                        </Typography>
                    </div>
                    {canCreate && (
                        <Button
                            variant="contained"
                            color="primary"
                            component={Link}
                            to={newClaimCampaignRoute}
                        >
                            New campaign
                        </Button>
                    )}
                </div>

                {newCampaign && (
                    <Paper className={classes.createdBanner} role="status">
                        <Typography>
                            Campaign <strong>{newCampaign.name}</strong> created
                            with {newCampaign.suppliers.length} supplier
                            {newCampaign.suppliers.length === 1 ? '' : 's'}.
                            {leftOut > 0 &&
                                ` ${leftOut} ${
                                    leftOut === 1 ? 'was' : 'were'
                                } left out because ${
                                    leftOut === 1 ? "it's" : "they've"
                                } been claimed or closed since you chose ${
                                    leftOut === 1 ? 'it' : 'them'
                                }.`}
                            {
                                ' Copy each claim link, or download the CSV to send them from your own email.'
                            }
                            {collapsed && (
                                <>
                                    {' '}
                                    <Link
                                        to={makeClaimCampaignRoute(
                                            newCampaign.id,
                                        )}
                                    >
                                        Open {newCampaign.name}
                                    </Link>
                                </>
                            )}
                        </Typography>
                    </Paper>
                )}

                {campaignList}
                {!canCreate && campaigns && campaigns.length > 0 && (
                    <Typography className={classes.fine}>
                        Campaigns are created for you by the OS Hub team.
                        Questions? Contact your account manager.
                    </Typography>
                )}
            </div>
        </AppOverflow>
    );
};

ClaimCampaigns.defaultProps = {
    campaigns: null,
    error: null,
    location: null,
    match: null,
};

ClaimCampaigns.propTypes = {
    classes: object.isRequired,
    userHasSignedIn: bool.isRequired,
    fetching: bool.isRequired,
    campaigns: arrayOf(campaignPropType),
    error: arrayOf(string),
    fetchCampaigns: func.isRequired,
    location: shape({ search: string }),
    match: shape({ params: shape({ campaignId: string }) }),
    hasAccess: bool.isRequired,
};

const mapStateToProps = ({
    auth: {
        user: { user },
    },
    claimCampaigns: { fetching, data, error },
}) => ({
    userHasSignedIn: !user.isAnon,
    hasAccess: hasClaimCampaignAccess(user),
    fetching,
    campaigns: data,
    error,
});

const mapDispatchToProps = dispatch => ({
    fetchCampaigns: () => dispatch(fetchClaimCampaigns()),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(claimCampaignsStyles)(ClaimCampaigns));
