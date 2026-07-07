import React, { useEffect, useState } from 'react';
import { arrayOf, bool, func, number, object, shape, string } from 'prop-types';
import { connect } from 'react-redux';
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
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Typography from '@material-ui/core/Typography';

import AppOverflow from '../AppOverflow';
import RequireAuthNotice from '../RequireAuthNotice';
import { fetchClaimCampaigns } from '../../actions/claimCampaigns';
import { claimIntroRoute } from '../../util/constants';
import { DownloadCSV, joinDataIntoCSVString } from '../../util/util';
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

const CampaignCard = ({ campaign, classes }) => {
    const [statusFilter, setStatusFilter] = useState('ALL');

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
                <Typography variant="subheading">Suppliers</Typography>
                <div className={classes.tableToolsActions}>
                    <Select
                        value={statusFilter}
                        onChange={e => setStatusFilter(e.target.value)}
                    >
                        <MenuItem value="ALL">All statuses</MenuItem>
                        <MenuItem value="claimed">Claimed</MenuItem>
                        <MenuItem value="pending">Pending review</MenuItem>
                        <MenuItem value="unclaimed">Not started</MenuItem>
                    </Select>
                    <Button
                        variant="outlined"
                        color="primary"
                        onClick={() => downloadSupplierCSV(campaign, suppliers)}
                    >
                        Download CSV
                    </Button>
                </div>
            </div>

            <Table>
                <TableHead>
                    <TableRow>
                        <TableCell>Facility</TableCell>
                        <TableCell>OS ID</TableCell>
                        <TableCell>Country</TableCell>
                        <TableCell>Claim status</TableCell>
                        <TableCell>Unique claim link</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {suppliers.map(supplier => (
                        <TableRow key={supplier.os_id}>
                            <TableCell>{supplier.name}</TableCell>
                            <TableCell>{supplier.os_id}</TableCell>
                            <TableCell>{supplier.country_code}</TableCell>
                            <TableCell>
                                <SupplierStatusChip
                                    status={supplier.claim_status}
                                    classes={classes}
                                />
                            </TableCell>
                            <TableCell>
                                <CopyToClipboard
                                    text={makeCampaignClaimLink(
                                        supplier.os_id,
                                        campaign.code,
                                    )}
                                >
                                    <Button color="primary">Copy link</Button>
                                </CopyToClipboard>
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </Paper>
    );
};

CampaignCard.propTypes = {
    campaign: campaignPropType.isRequired,
    classes: object.isRequired,
};

const ClaimCampaigns = ({
    classes,
    userHasSignedIn,
    fetching,
    campaigns,
    error,
    fetchCampaigns,
}) => {
    useEffect(() => {
        if (userHasSignedIn) {
            fetchCampaigns();
        }
    }, [userHasSignedIn, fetchCampaigns]);

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
                <Typography
                    variant="title"
                    component="h1"
                    className={classes.title}
                >
                    Claims Campaigns
                </Typography>
                <Typography className={classes.subtitle}>
                    Track which of your suppliers have claimed their production
                    location profiles.
                </Typography>

                {!campaigns || campaigns.length === 0 ? (
                    <Typography className={classes.emptyMessage}>
                        Your account has no claims campaigns yet. Campaigns are
                        created for you by the OS Hub team — contact your
                        account manager to get started.
                    </Typography>
                ) : (
                    campaigns.map(campaign => (
                        <CampaignCard
                            key={campaign.id}
                            campaign={campaign}
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
};

ClaimCampaigns.propTypes = {
    classes: object.isRequired,
    userHasSignedIn: bool.isRequired,
    fetching: bool.isRequired,
    campaigns: arrayOf(campaignPropType),
    error: arrayOf(string),
    fetchCampaigns: func.isRequired,
};

const mapStateToProps = ({
    auth: {
        user: { user },
    },
    claimCampaigns: { fetching, data, error },
}) => ({
    userHasSignedIn: !user.isAnon,
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
