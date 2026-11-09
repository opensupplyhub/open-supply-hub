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
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';
import InfoOutlined from '@material-ui/icons/InfoOutlined';

import AppOverflow from '../AppOverflow';
import RequireAuthNotice from '../RequireAuthNotice';
import StyledTooltip from '../StyledTooltip';
import { fetchClaimCampaigns } from '../../actions/claimCampaigns';
import apiRequest from '../../util/apiRequest';
import { sendClaimInvite } from '../../util/claimInvite';
import {
    CLAIM_INVITE,
    claimIntroRoute,
    makeClaimCampaignCandidatesURL,
    newClaimCampaignRoute,
} from '../../util/constants';
import {
    convertFeatureFlagsObjectToListOfActiveFlags,
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

const INVITE_MODES = Object.freeze({
    email: 'email',
    link: 'link',
});

const CONTACT_COLUMN_HELP =
    'Enter the email address of your contact at the facility and OS Hub will send them an invite to claim, or copy the link and send it yourself. Each link is unique to one facility, so make sure you send each facility its own link.';

const lastInvitePropType = shape({
    recipient_email: string.isRequired,
    created_at: string.isRequired,
});

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
            last_invite: lastInvitePropType,
        }),
    ).isRequired,
});

const makeCampaignClaimLink = (osID, code) =>
    `${window.location.origin}${claimIntroRoute.replace(
        ':osID',
        osID,
    )}?campaign=${code}`;

// Exports the rows currently shown, so filtering to "Not started" first
// yields exactly the outreach list.
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
                s.name,
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

const InvitedNote = ({ invite, classes }) => (
    <span className={classes.invitedNote}>
        Invited {invite.recipient_email} ·{' '}
        {moment(invite.created_at).format('D MMM YYYY')}
    </span>
);

InvitedNote.propTypes = {
    invite: lastInvitePropType.isRequired,
    classes: object.isRequired,
};

// Sends one supplier the campaign's claim invite by email. Claimed and
// pending suppliers can't be invited, so they get a note instead.
const EmailInviteCell = ({ supplier, campaignCode, lastInvite, onSent, classes }) => {
    const [email, setEmail] = useState('');
    const [sending, setSending] = useState(false);
    const [error, setError] = useState(null);

    if (supplier.claim_status !== 'unclaimed') {
        return (
            <span className={classes.invitedNote}>
                {supplier.claim_status === 'claimed'
                    ? 'Already claimed'
                    : 'Claim in review'}
            </span>
        );
    }

    const send = event => {
        event.preventDefault();
        setSending(true);
        setError(null);
        sendClaimInvite(supplier.os_id, {
            recipientEmail: email.trim(),
            campaign: campaignCode,
        })
            .then(({ data }) => {
                onSent(supplier.os_id, {
                    recipient_email: data.recipient_email,
                    created_at: new Date().toISOString(),
                });
                setEmail('');
            })
            .catch(err => setError(err.message))
            .finally(() => setSending(false));
    };

    return (
        <form className={classes.emailInvite} onSubmit={send}>
            <div className={classes.emailInviteRow}>
                <TextField
                    type="email"
                    placeholder="contact@facility.com"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    disabled={sending}
                    className={classes.emailField}
                    inputProps={{
                        'aria-label': `Email address for ${supplier.name}`,
                    }}
                    required
                />
                <Button
                    type="submit"
                    color="primary"
                    size="small"
                    disabled={sending || !email.trim()}
                >
                    {sending ? 'Sending…' : 'Send'}
                </Button>
            </div>
            {error && <span className={classes.inviteError}>{error}</span>}
            {!error && lastInvite && (
                <InvitedNote invite={lastInvite} classes={classes} />
            )}
        </form>
    );
};

EmailInviteCell.defaultProps = {
    lastInvite: null,
};

EmailInviteCell.propTypes = {
    supplier: shape({
        os_id: string.isRequired,
        name: string.isRequired,
        claim_status: string.isRequired,
    }).isRequired,
    campaignCode: string.isRequired,
    lastInvite: lastInvitePropType,
    onSent: func.isRequired,
    classes: object.isRequired,
};

const InviteModeToggle = ({ mode, onChange, classes }) => (
    <div className={classes.modeToggle} role="group" aria-label="Invite by">
        <span className={classes.modeLabel}>Invite by</span>
        {[
            [INVITE_MODES.email, 'Email'],
            [INVITE_MODES.link, 'Link'],
        ].map(([value, label]) => (
            <Button
                key={value}
                size="small"
                color="primary"
                variant={mode === value ? 'contained' : 'outlined'}
                aria-pressed={mode === value}
                onClick={() => onChange(value)}
                className={classes.modeButton}
            >
                {label}
            </Button>
        ))}
    </div>
);

InviteModeToggle.propTypes = {
    mode: string.isRequired,
    onChange: func.isRequired,
    classes: object.isRequired,
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

const CampaignCard = ({ campaign, canEmail, classes }) => {
    const [statusFilter, setStatusFilter] = useState('ALL');
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(25);
    const [inviteMode, setInviteMode] = useState(
        canEmail ? INVITE_MODES.email : INVITE_MODES.link,
    );
    // Invites sent from this page since it loaded, by OS ID.
    const [sentInvites, setSentInvites] = useState({});
    const recordSent = (osID, invite) =>
        setSentInvites(current => ({ ...current, [osID]: invite }));

    const counts = { claimed: 0, pending: 0, unclaimed: 0 };
    campaign.suppliers.forEach(s => {
        counts[s.claim_status] = (counts[s.claim_status] || 0) + 1;
    });
    const total = campaign.suppliers.length;
    const percentClaimed = total
        ? Math.round((counts.claimed / total) * 100)
        : 0;

    const suppliers =
        statusFilter === 'ALL'
            ? campaign.suppliers
            : campaign.suppliers.filter(s => s.claim_status === statusFilter);
    const pageSuppliers = suppliers.slice(
        page * rowsPerPage,
        page * rowsPerPage + rowsPerPage,
    );
    const showEmail = canEmail && inviteMode === INVITE_MODES.email;

    return (
        <Paper className={classes.campaignCard}>
            <div className={classes.campaignHeader}>
                <div>
                    <span className={classes.campaignName}>
                        {campaign.name}
                    </span>
                    <Typography className={classes.campaignMeta}>
                        {total} suppliers ·{' '}
                        {campaign.status === 'ACTIVE' ? 'Active' : 'Closed'}{' '}
                        campaign · created{' '}
                        {moment(campaign.created_at).format('D MMM YYYY')}
                    </Typography>
                </div>
                <div className={classes.codeBox}>
                    <span className={classes.codeLabel}>Campaign code</span>
                    <span className={classes.code}>{campaign.code}</span>
                    <CopyToClipboard text={campaign.code}>
                        <Button size="small" color="primary">
                            Copy
                        </Button>
                    </CopyToClipboard>
                </div>
            </div>

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
                                        width: `${
                                            (counts[status] / total) * 100
                                        }%`,
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
                    {canEmail && (
                        <InviteModeToggle
                            mode={inviteMode}
                            onChange={setInviteMode}
                            classes={classes}
                        />
                    )}
                    {/* The CSV is the links, for the brand's own mail merge. */}
                    {!showEmail && (
                        <Button
                            variant="outlined"
                            color="primary"
                            onClick={() =>
                                downloadSupplierCSV(campaign, suppliers)
                            }
                        >
                            Download CSV
                        </Button>
                    )}
                </div>
            </div>

            <div className={classes.tableWrap}>
                <Table className={classes.supplierTable}>
                    <TableHead>
                        <TableRow>
                            <TableCell className={classes.colFacility}>
                                Facility
                            </TableCell>
                            <TableCell className={classes.colOsId}>
                                OS ID
                            </TableCell>
                            <TableCell className={classes.colCountry}>
                                Country
                            </TableCell>
                            <TableCell className={classes.colStatus}>
                                Claim status
                            </TableCell>
                            <TableCell className={classes.colContact}>
                                <span className={classes.headerWithHelp}>
                                    {showEmail
                                        ? 'Contact email'
                                        : 'Unique claim link'}
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
                                </TableCell>
                                <TableCell className={classes.cell}>
                                    {showEmail ? (
                                        <EmailInviteCell
                                            supplier={supplier}
                                            campaignCode={campaign.code}
                                            lastInvite={
                                                sentInvites[supplier.os_id] ||
                                                supplier.last_invite
                                            }
                                            onSent={recordSent}
                                            classes={classes}
                                        />
                                    ) : (
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
                                    )}
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
    canEmail: bool.isRequired,
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
    canEmail,
}) => {
    // Brands enabled for self-serve can reach the candidates endpoint;
    // everyone else gets a 404 and sees no "New campaign" button.
    const [canCreate, setCanCreate] = useState(false);

    useEffect(() => {
        if (userHasSignedIn) {
            fetchCampaigns();
            apiRequest
                .get(makeClaimCampaignCandidatesURL())
                .then(() => setCanCreate(true))
                .catch(() => setCanCreate(false));
        }
    }, [userHasSignedIn, fetchCampaigns]);

    const newCampaignID = Number(
        new URLSearchParams((location && location.search) || '').get('new'),
    );
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
                            {canEmail
                                ? ' Enter a contact email for each supplier below and we\'ll send them an invite, or copy their links or download the CSV to send them yourself.'
                                : ' Copy each claim link below, or download the CSV to send them from your own email.'}
                        </Typography>
                    </Paper>
                )}

                {!campaigns || campaigns.length === 0 ? (
                    <Typography className={classes.emptyMessage}>
                        {canCreate
                            ? 'Your account has no claims campaigns yet. Use "New campaign" to invite suppliers from one of your lists.'
                            : 'Your account has no claims campaigns yet. Campaigns are created for you by the OS Hub team — contact your account manager to get started.'}
                    </Typography>
                ) : (
                    campaigns.map(campaign => (
                        <CampaignCard
                            key={campaign.id}
                            campaign={campaign}
                            canEmail={canEmail}
                            classes={classes}
                        />
                    ))
                )}
            </div>
        </AppOverflow>
    );
};

ClaimCampaigns.defaultProps = {
    campaigns: null,
    error: null,
    location: null,
};

ClaimCampaigns.propTypes = {
    classes: object.isRequired,
    userHasSignedIn: bool.isRequired,
    fetching: bool.isRequired,
    campaigns: arrayOf(campaignPropType),
    error: arrayOf(string),
    fetchCampaigns: func.isRequired,
    location: shape({ search: string }),
    canEmail: bool.isRequired,
};

const mapStateToProps = ({
    auth: {
        user: { user },
    },
    claimCampaigns: { fetching, data, error },
    featureFlags: { flags },
}) => ({
    userHasSignedIn: !user.isAnon,
    canEmail: convertFeatureFlagsObjectToListOfActiveFlags(flags).includes(
        CLAIM_INVITE,
    ),
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
