import React, { useEffect, useMemo, useState } from 'react';
import { bool, number, object } from 'prop-types';
import { connect } from 'react-redux';
import { Link, withRouter } from 'react-router-dom';
import { withStyles } from '@material-ui/core/styles';
import moment from 'moment';
import Button from '@material-ui/core/Button';
import Checkbox from '@material-ui/core/Checkbox';
import Chip from '@material-ui/core/Chip';
import CircularProgress from '@material-ui/core/CircularProgress';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import MenuItem from '@material-ui/core/MenuItem';
import Paper from '@material-ui/core/Paper';
import Radio from '@material-ui/core/Radio';
import Select from '@material-ui/core/Select';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';

import AppOverflow from '../AppOverflow';
import RequireAuthNotice from '../RequireAuthNotice';
import apiRequest from '../../util/apiRequest';
import {
    claimCampaignsRoute,
    contributeRoute,
    makeClaimCampaignCandidatesURL,
    MAX_SUPPLIERS_PER_CAMPAIGN,
} from '../../util/constants';
import { newClaimCampaignStyles } from './styles';
import CampaignSupplierSearch, {
    SEARCH_STATUS_LABELS,
} from './CampaignSupplierSearch';

const SOURCES = Object.freeze({
    list: 'list',
    search: 'search',
});

const FILTERS = Object.freeze([
    { value: 'unclaimed', label: 'Not started' },
    { value: 'pending', label: 'Pending review' },
    { value: 'claimed', label: 'Claimed' },
    { value: 'all', label: 'All' },
]);

const STATUS_LABELS = Object.freeze({
    claimed: 'Claimed',
    pending: 'Pending review',
    unclaimed: 'Not started',
});

// Claimed suppliers have nothing left to do, and closed locations can't
// claim, so neither can be invited.
const isPickable = supplier =>
    supplier.claim_status !== 'claimed' && !supplier.is_closed;

const formatCount = count => count.toLocaleString('en-US');

// A campaign invites at most `limit` suppliers (the backend refuses more),
// so every bulk selection takes suppliers in the order shown, up to the
// limit. Larger lists stay usable: choose another batch for the next
// campaign.
export const defaultSelection = (
    suppliers,
    limit = MAX_SUPPLIERS_PER_CAMPAIGN,
) =>
    new Set(
        suppliers
            .filter(s => s.claim_status === 'unclaimed' && isPickable(s))
            .slice(0, limit)
            .map(s => s.os_id),
    );

// Consecutive batches of at most `size` rows, as {start, end} indexes
// (end exclusive), for choosing which part of a large list to invite.
export const makeBatches = (count, size) =>
    Array.from({ length: Math.ceil(count / size) }, (_, i) => ({
        start: i * size,
        end: Math.min((i + 1) * size, count),
    }));

export const pickerStatusLabel = (supplier, labels) =>
    supplier.is_closed ? 'Closed' : labels[supplier.claim_status];

const firstError = error => {
    const data = error && error.response && error.response.data;
    if (!data) {
        return 'An error prevented creating the campaign.';
    }
    const messages = [].concat(...Object.values(data));
    return messages.length
        ? messages.join(' ')
        : 'An error prevented creating the campaign.';
};

// A list still in moderation or processing may have no matched
// suppliers yet; until it has some there is nothing to choose from it.
// A source with no matched suppliers yet (a list in moderation, or
// API locations still processing or waiting for the brand to confirm a
// match) has nothing to choose from. A list over the server's size
// limit (`too_large`) can't be opened at all.
export const isSelectableList = list =>
    list.supplier_count !== 0 && !list.too_large;

const describeAwaiting = list =>
    list.awaiting_confirmation
        ? ` · ${list.awaiting_confirmation} waiting for you to confirm a match`
        : '';

export const describeListCount = list => {
    if (typeof list.supplier_count !== 'number') {
        return null;
    }
    if (list.supplier_count === 0) {
        return `No suppliers matched yet${describeAwaiting(list)}`;
    }
    const count = `${list.supplier_count} supplier${
        list.supplier_count === 1 ? '' : 's'
    }`;
    if (list.too_large) {
        return `${count} · too large to start a campaign from`;
    }
    return `${
        list.pending ? `${count} matched so far` : count
    }${describeAwaiting(list)}`;
};

export const NewClaimCampaign = ({
    classes,
    userHasSignedIn,
    history,
    maxSuppliers,
}) => {
    const [lists, setLists] = useState(null);
    const [listsError, setListsError] = useState(false);
    const [listId, setListId] = useState(null);
    const [suppliers, setSuppliers] = useState(null);
    const [selected, setSelected] = useState(new Set());
    const [filter, setFilter] = useState('unclaimed');
    const [name, setName] = useState(
        `Supplier onboarding · ${moment().format('MMM YYYY')}`,
    );
    const [creating, setCreating] = useState(false);
    // Where the suppliers come from: one of the brand's lists (the main
    // route) or a search of OS Hub. Each keeps its own selection.
    const [source, setSource] = useState(SOURCES.list);
    // Suppliers added from searches, by OS ID, in the order added.
    const [picked, setPicked] = useState(new Map());
    const [createError, setCreateError] = useState(null);
    // Set when "Add" from search had to leave suppliers out at the limit.
    const [searchLimitNote, setSearchLimitNote] = useState(null);

    useEffect(() => {
        if (!userHasSignedIn) {
            return;
        }
        apiRequest
            .get(makeClaimCampaignCandidatesURL())
            .then(({ data }) => {
                setLists(data);
                const first = data.find(isSelectableList);
                if (first) {
                    setListId(first.id);
                }
            })
            .catch(() => setListsError(true));
    }, [userHasSignedIn]);

    useEffect(() => {
        if (listId === null) {
            return;
        }
        setSuppliers(null);
        apiRequest
            .get(makeClaimCampaignCandidatesURL(listId))
            .then(({ data }) => {
                setSuppliers(data.suppliers);
                setSelected(defaultSelection(data.suppliers, maxSuppliers));
                setFilter('unclaimed');
            })
            .catch(() => setSuppliers([]));
    }, [listId, maxSuppliers]);

    const counts = useMemo(() => {
        const result = { unclaimed: 0, pending: 0, claimed: 0 };
        (suppliers || []).forEach(s => {
            result[s.claim_status] += 1;
        });
        return result;
    }, [suppliers]);

    if (!userHasSignedIn) {
        return (
            <RequireAuthNotice
                title="New claims campaign"
                text="Log in to create a claims campaign"
            />
        );
    }

    if (listsError) {
        return (
            <Typography className={classes.message}>
                Creating campaigns isn&apos;t turned on for your account.
                Contact your OS Hub account manager to get started.
            </Typography>
        );
    }

    if (lists === null) {
        return (
            <div className={classes.message}>
                <CircularProgress />
            </div>
        );
    }

    const shown = (suppliers || []).filter(
        s => filter === 'all' || s.claim_status === filter,
    );
    const shownPickable = shown.filter(isPickable);
    const shownSelectedCount = shownPickable.filter(s => selected.has(s.os_id))
        .length;
    const allShownSelected =
        shownPickable.length > 0 && shownSelectedCount === shownPickable.length;
    const atLimit = selected.size >= maxSuppliers;
    const unclaimedPickableCount = (suppliers || []).filter(
        s => s.claim_status === 'unclaimed' && isPickable(s),
    ).length;
    const pickableCount = (suppliers || []).filter(isPickable).length;
    const shownBatches =
        shownPickable.length > maxSuppliers
            ? makeBatches(shownPickable.length, maxSuppliers)
            : [];

    const toggle = osID => {
        const next = new Set(selected);
        if (next.has(osID)) {
            next.delete(osID);
        } else if (next.size < maxSuppliers) {
            next.add(osID);
        }
        setSelected(next);
    };

    // With some shown suppliers selected, the header box clears them;
    // otherwise it selects the shown ones, in order, up to the limit.
    const toggleAllShown = () => {
        const next = new Set(selected);
        if (shownSelectedCount > 0) {
            shownPickable.forEach(s => next.delete(s.os_id));
        } else {
            shownPickable
                .slice(0, Math.max(maxSuppliers - next.size, 0))
                .forEach(s => next.add(s.os_id));
        }
        setSelected(next);
    };

    // Replaces the selection with one batch of the shown suppliers.
    const selectBatch = index => {
        const { start, end } = shownBatches[index];
        setSelected(new Set(shownPickable.slice(start, end).map(s => s.os_id)));
    };

    const addPicked = toAdd => {
        const next = new Map(picked);
        const fresh = toAdd.filter(s => !next.has(s.os_id));
        const room = Math.max(maxSuppliers - next.size, 0);
        fresh.slice(0, room).forEach(s => next.set(s.os_id, s));
        setPicked(next);
        setSearchLimitNote(
            fresh.length > room
                ? `${formatCount(
                      fresh.length - room,
                  )} not added: a campaign can invite up to ${formatCount(
                      maxSuppliers,
                  )} suppliers.`
                : null,
        );
    };

    const removePicked = osID => {
        const next = new Map(picked);
        next.delete(osID);
        setPicked(next);
        setSearchLimitNote(null);
    };

    const fromSearch = source === SOURCES.search;
    const selectedCount = fromSearch ? picked.size : selected.size;
    const showSteps = fromSearch || listId !== null;

    const create = () => {
        setCreating(true);
        setCreateError(null);
        const payload = fromSearch
            ? { name: name.trim(), os_ids: [...picked.keys()] }
            : {
                  name: name.trim(),
                  list_id: listId,
                  os_ids: (suppliers || [])
                      .filter(s => selected.has(s.os_id))
                      .map(s => s.os_id),
              };
        apiRequest
            .post('/api/claim-campaigns/', payload)
            .then(({ data }) => {
                // Suppliers claimed or closed since they were chosen are
                // left out by the server; the dashboard says how many.
                const leftOut = (data.skipped || []).length;
                history.push(
                    `${claimCampaignsRoute}?new=${data.id}${
                        leftOut ? `&left_out=${leftOut}` : ''
                    }`,
                );
            })
            .catch(error => {
                setCreating(false);
                setCreateError(firstError(error));
            });
    };

    return (
        <AppOverflow>
            <div className={classes.container}>
                <Typography
                    variant="title"
                    component="h1"
                    className={classes.title}
                >
                    New claims campaign
                </Typography>
                <Typography className={classes.subtitle}>
                    Choose which suppliers to invite. Each gets a unique link to
                    claim its OS Hub profile and add its own details. You track
                    who has claimed on the{' '}
                    <Link to={claimCampaignsRoute}>campaign dashboard</Link>.
                </Typography>

                <Typography className={classes.stepHeading}>
                    1. Choose where your suppliers come from
                </Typography>
                <Paper className={classes.panel}>
                    <div className={classes.sourceOptions}>
                        <FormControlLabel
                            control={
                                <Radio
                                    checked={source === SOURCES.list}
                                    onChange={() => setSource(SOURCES.list)}
                                    color="primary"
                                />
                            }
                            label="From my lists or API uploads"
                            classes={{ label: classes.listName }}
                        />
                        <Typography className={classes.sourceHint}>
                            Invite suppliers you&apos;ve already added to OS
                            Hub, by uploading a list or through the API.
                        </Typography>
                        <FormControlLabel
                            control={
                                <Radio
                                    checked={source === SOURCES.search}
                                    onChange={() => setSource(SOURCES.search)}
                                    color="primary"
                                />
                            }
                            label="From a search of OS Hub"
                            classes={{ label: classes.listName }}
                        />
                        <Typography className={classes.sourceHint}>
                            Find any production location with the OS Hub search
                            filters, including ones you haven&apos;t uploaded.
                        </Typography>
                    </div>
                </Paper>

                {source === SOURCES.list && (
                    <>
                        <Typography className={classes.stepHeading}>
                            Choose a source
                        </Typography>
                        {lists.length === 0 ? (
                            <Paper className={classes.panel}>
                                <Typography>
                                    You haven&apos;t added any suppliers yet.{' '}
                                    <Link to={contributeRoute}>
                                        Upload a list
                                    </Link>{' '}
                                    or add locations through the API first, or
                                    choose suppliers from a search instead. If
                                    you don&apos;t want OS Hub to show you as
                                    connected to these suppliers, ask the OS Hub
                                    team to make the list private.
                                </Typography>
                            </Paper>
                        ) : (
                            <Paper className={classes.panel}>
                                {lists.map(list => (
                                    <div
                                        key={list.id}
                                        className={classes.listOption}
                                    >
                                        <FormControlLabel
                                            control={
                                                <Radio
                                                    checked={listId === list.id}
                                                    onChange={() =>
                                                        setListId(list.id)
                                                    }
                                                    disabled={
                                                        !isSelectableList(list)
                                                    }
                                                    color="primary"
                                                />
                                            }
                                            label={list.name}
                                            classes={{
                                                label: classes.listName,
                                            }}
                                        />
                                        <Typography
                                            className={classes.listCount}
                                        >
                                            {describeListCount(list)}
                                        </Typography>
                                        {list.pending && (
                                            <Chip
                                                label="Pending"
                                                className={classes.pendingChip}
                                            />
                                        )}
                                        {list.kind === 'api' && (
                                            <Chip
                                                label="API"
                                                className={classes.publicChip}
                                            />
                                        )}
                                        <Chip
                                            label={
                                                list.is_public
                                                    ? 'Public'
                                                    : 'Private'
                                            }
                                            className={
                                                list.is_public
                                                    ? classes.publicChip
                                                    : classes.privateChip
                                            }
                                        />
                                    </div>
                                ))}
                                <Typography className={classes.fine}>
                                    Inviting suppliers from a private list or
                                    private API uploads doesn&apos;t publish
                                    your connection to them.
                                    {lists.some(list => list.too_large) &&
                                        ' A list that is too large can\u2019t be opened here: use search to choose its suppliers instead.'}
                                    {lists.some(list => list.pending) &&
                                        ' A pending list is still being reviewed or matched by OS Hub. Its suppliers appear here once they are matched.'}
                                    {lists.some(
                                        list => list.awaiting_confirmation,
                                    ) &&
                                        ' Locations waiting for you to confirm a match appear here once you confirm it.'}
                                </Typography>
                            </Paper>
                        )}
                    </>
                )}

                {fromSearch && (
                    <>
                        <Typography className={classes.stepHeading}>
                            2. Find and add suppliers
                        </Typography>
                        <Paper className={classes.panel}>
                            <CampaignSupplierSearch
                                picked={picked}
                                onAdd={addPicked}
                                remaining={Math.max(
                                    maxSuppliers - picked.size,
                                    0,
                                )}
                            />
                            <Typography className={classes.pickedHeading}>
                                Added to this campaign ({picked.size})
                            </Typography>
                            <Typography className={classes.fine}>
                                A campaign can invite up to{' '}
                                {formatCount(maxSuppliers)} suppliers.
                            </Typography>
                            {searchLimitNote && (
                                <Typography
                                    className={classes.limitNote}
                                    role="status"
                                >
                                    {searchLimitNote}
                                </Typography>
                            )}
                            {picked.size === 0 ? (
                                <Typography className={classes.fine}>
                                    Nothing added yet. Search, then add
                                    suppliers one by one or all at once.
                                </Typography>
                            ) : (
                                <>
                                    <div className={classes.tableWrap}>
                                        <Table>
                                            <TableBody>
                                                {[...picked.values()].map(s => (
                                                    <TableRow key={s.os_id}>
                                                        <TableCell>
                                                            {s.name}
                                                            <span
                                                                className={
                                                                    classes.country
                                                                }
                                                            >
                                                                {s.country_code}
                                                            </span>
                                                        </TableCell>
                                                        <TableCell>
                                                            {s.os_id}
                                                        </TableCell>
                                                        <TableCell>
                                                            {SEARCH_STATUS_LABELS[
                                                                s.claim_status
                                                            ] || s.claim_status}
                                                        </TableCell>
                                                        <TableCell>
                                                            <Button
                                                                size="small"
                                                                onClick={() =>
                                                                    removePicked(
                                                                        s.os_id,
                                                                    )
                                                                }
                                                                aria-label={`Remove ${s.name}`}
                                                            >
                                                                Remove
                                                            </Button>
                                                        </TableCell>
                                                    </TableRow>
                                                ))}
                                            </TableBody>
                                        </Table>
                                    </div>
                                    <Button
                                        size="small"
                                        onClick={() => {
                                            setPicked(new Map());
                                            setSearchLimitNote(null);
                                        }}
                                    >
                                        Remove all
                                    </Button>
                                </>
                            )}
                        </Paper>
                    </>
                )}

                {source === SOURCES.list && listId !== null && (
                    <>
                        <Typography className={classes.stepHeading}>
                            2. Pick suppliers to invite
                        </Typography>
                        {suppliers === null ? (
                            <CircularProgress />
                        ) : (
                            <Paper className={classes.panel}>
                                <div className={classes.toolbar}>
                                    {FILTERS.map(f => (
                                        <Button
                                            key={f.value}
                                            size="small"
                                            variant={
                                                filter === f.value
                                                    ? 'contained'
                                                    : 'outlined'
                                            }
                                            color="primary"
                                            onClick={() => setFilter(f.value)}
                                        >
                                            {f.label} ·{' '}
                                            {f.value === 'all'
                                                ? suppliers.length
                                                : counts[f.value]}
                                        </Button>
                                    ))}
                                    <span className={classes.grow} />
                                    <Typography>
                                        {formatCount(selected.size)} selected
                                    </Typography>
                                    {shownBatches.length > 0 && (
                                        <Select
                                            value=""
                                            displayEmpty
                                            onChange={e =>
                                                selectBatch(e.target.value)
                                            }
                                            inputProps={{
                                                'aria-label':
                                                    'Select a batch of suppliers',
                                            }}
                                        >
                                            <MenuItem value="" disabled>
                                                Select a batch
                                            </MenuItem>
                                            {shownBatches.map(
                                                ({ start, end }, index) => (
                                                    <MenuItem
                                                        key={start}
                                                        value={index}
                                                    >
                                                        {`${formatCount(
                                                            start + 1,
                                                        )}–${formatCount(end)}`}
                                                    </MenuItem>
                                                ),
                                            )}
                                        </Select>
                                    )}
                                    <Button
                                        size="small"
                                        onClick={() =>
                                            setSelected(
                                                defaultSelection(
                                                    suppliers,
                                                    maxSuppliers,
                                                ),
                                            )
                                        }
                                    >
                                        {unclaimedPickableCount > maxSuppliers
                                            ? `Select first ${formatCount(
                                                  maxSuppliers,
                                              )} not started`
                                            : 'Select all not started'}
                                    </Button>
                                    <Button
                                        size="small"
                                        onClick={() => setSelected(new Set())}
                                    >
                                        Clear
                                    </Button>
                                </div>
                                {pickableCount > maxSuppliers && (
                                    <Typography
                                        className={classes.limitNote}
                                        role="status"
                                    >
                                        A campaign can invite up to{' '}
                                        {formatCount(maxSuppliers)} suppliers,
                                        and this list has{' '}
                                        {formatCount(pickableCount)} you can
                                        invite. Bulk selections stop at{' '}
                                        {formatCount(maxSuppliers)}, in the
                                        order shown. To invite the rest, create
                                        this campaign, then start another one
                                        and choose the next batch.
                                    </Typography>
                                )}
                                {atLimit && (
                                    <Typography
                                        className={classes.limitNote}
                                        role="status"
                                    >
                                        {formatCount(maxSuppliers)} selected:
                                        the most one campaign can invite.
                                        Unselect some to choose others.
                                    </Typography>
                                )}
                                <div className={classes.tableWrap}>
                                    <Table>
                                        <TableHead>
                                            <TableRow>
                                                <TableCell padding="checkbox">
                                                    <Checkbox
                                                        checked={
                                                            allShownSelected
                                                        }
                                                        indeterminate={
                                                            shownSelectedCount >
                                                                0 &&
                                                            !allShownSelected
                                                        }
                                                        disabled={
                                                            !shownPickable.length
                                                        }
                                                        onChange={
                                                            toggleAllShown
                                                        }
                                                        inputProps={{
                                                            'aria-label':
                                                                'Select all shown',
                                                        }}
                                                    />
                                                </TableCell>
                                                <TableCell>OS ID</TableCell>
                                                <TableCell>
                                                    Production location
                                                </TableCell>
                                                <TableCell>
                                                    Claim status
                                                </TableCell>
                                            </TableRow>
                                        </TableHead>
                                        <TableBody>
                                            {shown.map(s => (
                                                <TableRow key={s.os_id}>
                                                    <TableCell padding="checkbox">
                                                        <Checkbox
                                                            checked={selected.has(
                                                                s.os_id,
                                                            )}
                                                            disabled={
                                                                !isPickable(
                                                                    s,
                                                                ) ||
                                                                (atLimit &&
                                                                    !selected.has(
                                                                        s.os_id,
                                                                    ))
                                                            }
                                                            onChange={() =>
                                                                toggle(s.os_id)
                                                            }
                                                            inputProps={{
                                                                'aria-label': `Select ${s.name}`,
                                                            }}
                                                        />
                                                    </TableCell>
                                                    <TableCell>
                                                        {s.os_id}
                                                    </TableCell>
                                                    <TableCell>
                                                        {s.name}
                                                        <span
                                                            className={
                                                                classes.country
                                                            }
                                                        >
                                                            {s.country_code}
                                                        </span>
                                                    </TableCell>
                                                    <TableCell>
                                                        {pickerStatusLabel(
                                                            s,
                                                            STATUS_LABELS,
                                                        )}
                                                    </TableCell>
                                                </TableRow>
                                            ))}
                                            {shown.length === 0 && (
                                                <TableRow>
                                                    <TableCell colSpan={4}>
                                                        No suppliers here.
                                                    </TableCell>
                                                </TableRow>
                                            )}
                                        </TableBody>
                                    </Table>
                                </div>
                                <Typography className={classes.fine}>
                                    Claimed suppliers can&apos;t be selected
                                    because they&apos;ve already claimed, and
                                    closed production locations can&apos;t
                                    claim.
                                </Typography>
                            </Paper>
                        )}
                    </>
                )}

                {showSteps && (
                    <>
                        <Typography className={classes.stepHeading}>
                            3. Create the campaign
                        </Typography>
                        <Paper className={classes.panel}>
                            <div className={classes.createRow}>
                                <TextField
                                    id="claim-campaign-name"
                                    label="Campaign name"
                                    value={name}
                                    onChange={e => setName(e.target.value)}
                                    className={classes.nameField}
                                    inputProps={{ maxLength: 100 }}
                                />
                                <Typography>
                                    {selectedCount} supplier
                                    {selectedCount === 1 ? '' : 's'} will get a
                                    claim link
                                </Typography>
                                <Button
                                    variant="contained"
                                    color="primary"
                                    disabled={
                                        creating ||
                                        !selectedCount ||
                                        selectedCount > maxSuppliers ||
                                        !name.trim()
                                    }
                                    onClick={create}
                                >
                                    {creating ? 'Creating…' : 'Create campaign'}
                                </Button>
                            </div>
                            {createError && (
                                <Typography
                                    className={classes.error}
                                    role="alert"
                                >
                                    {createError}
                                </Typography>
                            )}
                        </Paper>
                    </>
                )}
            </div>
        </AppOverflow>
    );
};

NewClaimCampaign.defaultProps = {
    maxSuppliers: MAX_SUPPLIERS_PER_CAMPAIGN,
};

NewClaimCampaign.propTypes = {
    classes: object.isRequired,
    userHasSignedIn: bool.isRequired,
    history: object.isRequired,
    // Overridable so tests needn't render thousands of rows.
    maxSuppliers: number,
};

const mapStateToProps = ({
    auth: {
        user: { user },
    },
}) => ({
    userHasSignedIn: !user.isAnon,
});

export default connect(mapStateToProps)(
    withRouter(withStyles(newClaimCampaignStyles)(NewClaimCampaign)),
);
