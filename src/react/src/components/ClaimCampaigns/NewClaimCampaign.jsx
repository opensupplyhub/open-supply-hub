import React, { useEffect, useMemo, useState } from 'react';
import { bool, object } from 'prop-types';
import { connect } from 'react-redux';
import { Link, withRouter } from 'react-router-dom';
import { withStyles } from '@material-ui/core/styles';
import moment from 'moment';
import Button from '@material-ui/core/Button';
import Checkbox from '@material-ui/core/Checkbox';
import Chip from '@material-ui/core/Chip';
import CircularProgress from '@material-ui/core/CircularProgress';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Paper from '@material-ui/core/Paper';
import Radio from '@material-ui/core/Radio';
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

const defaultSelection = suppliers =>
    new Set(
        suppliers
            .filter(s => s.claim_status === 'unclaimed' && !s.is_closed)
            .map(s => s.os_id),
    );

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
export const isSelectableList = list =>
    !(list.pending && list.supplier_count === 0);

export const describeListCount = list => {
    if (typeof list.supplier_count !== 'number') {
        return null;
    }
    if (list.pending && list.supplier_count === 0) {
        return 'No suppliers matched yet';
    }
    const count = `${list.supplier_count} supplier${
        list.supplier_count === 1 ? '' : 's'
    }`;
    return list.pending ? `${count} matched so far` : count;
};

export const NewClaimCampaign = ({ classes, userHasSignedIn, history }) => {
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
                setSelected(defaultSelection(data.suppliers));
                setFilter('unclaimed');
            })
            .catch(() => setSuppliers([]));
    }, [listId]);

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
    const allShownSelected =
        shownPickable.length > 0 &&
        shownPickable.every(s => selected.has(s.os_id));

    const toggle = osID => {
        const next = new Set(selected);
        if (next.has(osID)) {
            next.delete(osID);
        } else {
            next.add(osID);
        }
        setSelected(next);
    };

    const toggleAllShown = () => {
        const next = new Set(selected);
        shownPickable.forEach(s =>
            allShownSelected ? next.delete(s.os_id) : next.add(s.os_id),
        );
        setSelected(next);
    };

    const addPicked = toAdd => {
        const next = new Map(picked);
        toAdd.forEach(s => next.set(s.os_id, s));
        setPicked(next);
    };

    const removePicked = osID => {
        const next = new Map(picked);
        next.delete(osID);
        setPicked(next);
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
            .then(({ data }) =>
                history.push(`${claimCampaignsRoute}?new=${data.id}`),
            )
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
                            label="From one of my lists"
                            classes={{ label: classes.listName }}
                        />
                        <Typography className={classes.sourceHint}>
                            Invite suppliers you&apos;ve already uploaded.
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
                            Choose a list
                        </Typography>
                        {lists.length === 0 ? (
                            <Paper className={classes.panel}>
                                <Typography>
                                    You have no lists yet.{' '}
                                    <Link to={contributeRoute}>
                                        Upload a list
                                    </Link>{' '}
                                    first, or choose suppliers from a search
                                    instead. If you don&apos;t want OS Hub to
                                    show you as connected to these suppliers,
                                    ask the OS Hub team to make the list
                                    private.
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
                                    Inviting suppliers from a private list
                                    doesn&apos;t publish your connection to
                                    them.
                                    {lists.some(list => list.pending) &&
                                        ' A pending list is still being reviewed or matched by OS Hub. Its suppliers appear here once they are matched.'}
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
                            />
                            <Typography className={classes.pickedHeading}>
                                Added to this campaign ({picked.size})
                            </Typography>
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
                                        onClick={() => setPicked(new Map())}
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
                                        {selected.size} selected
                                    </Typography>
                                    <Button
                                        size="small"
                                        onClick={() =>
                                            setSelected(
                                                defaultSelection(suppliers),
                                            )
                                        }
                                    >
                                        Select all not started
                                    </Button>
                                    <Button
                                        size="small"
                                        onClick={() => setSelected(new Set())}
                                    >
                                        Clear
                                    </Button>
                                </div>
                                <div className={classes.tableWrap}>
                                    <Table>
                                        <TableHead>
                                            <TableRow>
                                                <TableCell padding="checkbox">
                                                    <Checkbox
                                                        checked={
                                                            allShownSelected
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
                                                                !isPickable(s)
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
                                                        {s.is_closed
                                                            ? 'Closed'
                                                            : STATUS_LABELS[
                                                                  s.claim_status
                                                              ]}
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

NewClaimCampaign.propTypes = {
    classes: object.isRequired,
    userHasSignedIn: bool.isRequired,
    history: object.isRequired,
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
