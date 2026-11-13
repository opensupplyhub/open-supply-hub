import React, { useEffect, useState } from 'react';
import { func, number, object, oneOfType, string } from 'prop-types';
import Typography from '@material-ui/core/Typography';
import Checkbox from '@material-ui/core/Checkbox';
import FormControlLabel from '@material-ui/core/FormControlLabel';

import apiRequest from '../util/apiRequest';
import {
    makeEmbedSupplyChainsURL,
    makeOwnFacilitiesSearchURL,
} from '../util/util';
import {
    CHAIN_STAGE_SUGGESTIONS,
    MAX_CHAIN_LOCATIONS,
    addChainLink,
    addChainLocation,
    formatChainForAPI,
    getChainDepths,
    getChainErrorMessages,
    getPossibleCustomers,
    makeEmptyChain,
    removeChainLink,
    removeChainLocation,
    setChainLocationStage,
} from '../util/embeddedMap';

const BORDER = '1px solid rgb(214, 216, 221)';

const styles = {
    section: {
        marginTop: '30px',
    },
    sectionHeader: {
        color: 'rgb(0, 0, 0)',
        fontSize: '24px',
        margin: '10px 0',
    },
    subHeader: {
        color: 'rgb(0, 0, 0)',
        fontSize: '18px',
        fontWeight: 700,
        margin: '24px 0 6px',
    },
    label: {
        display: 'block',
        margin: '14px 0 4px',
        fontSize: '14px',
        fontWeight: 700,
    },
    input: {
        width: '100%',
        padding: '8px',
        fontSize: '14px',
        fontFamily: 'inherit',
        boxSizing: 'border-box',
    },
    row: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '10px',
        padding: '10px 12px',
        marginTop: '8px',
        background: 'white',
        border: BORDER,
    },
    rowName: {
        display: 'flex',
        alignItems: 'center',
        minWidth: 0,
        fontWeight: 700,
    },
    swatch: {
        width: '14px',
        height: '14px',
        borderRadius: '50%',
        marginRight: '10px',
        flex: 'none',
    },
    status: {
        marginLeft: '10px',
        fontSize: '12px',
        fontWeight: 400,
        color: 'rgba(0, 0, 0, 0.6)',
        whiteSpace: 'nowrap',
    },
    actions: {
        display: 'flex',
        gap: '6px',
        flex: 'none',
    },
    button: {
        padding: '6px 12px',
        border: '1px solid rgb(13, 17, 40)',
        background: 'white',
        fontFamily: 'inherit',
        fontSize: '13px',
        fontWeight: 700,
        cursor: 'pointer',
    },
    primaryButton: {
        background: 'rgb(13, 17, 40)',
        color: 'white',
    },
    location: {
        padding: '10px 12px',
        marginTop: '8px',
        background: 'white',
        border: BORDER,
    },
    locationHeader: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        gap: '10px',
    },
    osId: {
        fontSize: '12px',
        color: 'rgba(0, 0, 0, 0.6)',
    },
    chip: {
        display: 'inline-flex',
        alignItems: 'center',
        margin: '4px 6px 0 0',
        padding: '2px 4px 2px 8px',
        background: 'rgb(238, 240, 244)',
        fontSize: '13px',
    },
    chipRemove: {
        marginLeft: '4px',
        border: 0,
        background: 'none',
        fontSize: '15px',
        lineHeight: 1,
        cursor: 'pointer',
    },
    hint: {
        fontSize: '13px',
        color: 'rgba(0, 0, 0, 0.6)',
    },
    error: {
        color: 'rgb(183, 28, 28)',
        marginTop: '10px',
    },
    diagram: {
        marginTop: '8px',
        padding: '10px',
        overflowX: 'auto',
        background: 'white',
        border: BORDER,
    },
    footer: {
        display: 'flex',
        gap: '8px',
        marginTop: '20px',
    },
};

const BOX_WIDTH = 150;
const BOX_HEIGHT = 34;
const COLUMN_GAP = 46;
const ROW_GAP = 12;

const shorten = (text, length = 22) =>
    text.length > length ? `${text.slice(0, length - 1)}…` : text;

/*
A sketch of a chain: its locations in columns, the start of the chain on the
left, with a line from each supplier to each location it supplies.
*/
export function SupplyChainDiagram({ chain }) {
    if (!chain.nodes.length) return null;

    const depths = getChainDepths(chain);
    const maxDepth = Math.max(...Object.values(depths));
    const columns = {};
    const position = {};
    chain.nodes.forEach(node => {
        const column = maxDepth - depths[node.os_id];
        const row = columns[column] || 0;
        columns[column] = row + 1;
        position[node.os_id] = {
            x: column * (BOX_WIDTH + COLUMN_GAP),
            y: row * (BOX_HEIGHT + ROW_GAP),
        };
    });
    const width = maxDepth * (BOX_WIDTH + COLUMN_GAP) - COLUMN_GAP;
    const height =
        Math.max(...Object.values(columns)) * (BOX_HEIGHT + ROW_GAP) - ROW_GAP;

    return (
        <div style={styles.diagram}>
            <svg
                viewBox={`0 0 ${width + 2} ${height + 2}`}
                style={{
                    display: 'block',
                    width: '100%',
                    maxWidth: `${width + 2}px`,
                }}
                role="img"
                aria-label="Diagram of the supply chain"
            >
                <g transform="translate(1, 1)">
                    {chain.links.map(([supplier, customer]) => {
                        const from = position[supplier];
                        const to = position[customer];
                        if (!from || !to) return null;
                        return (
                            <line
                                key={`${supplier}-${customer}`}
                                x1={from.x + BOX_WIDTH}
                                y1={from.y + BOX_HEIGHT / 2}
                                x2={to.x}
                                y2={to.y + BOX_HEIGHT / 2}
                                stroke={chain.color}
                                strokeWidth="2"
                            />
                        );
                    })}
                    {chain.nodes.map(node => (
                        <g
                            key={node.os_id}
                            transform={`translate(${position[node.os_id].x}, ${
                                position[node.os_id].y
                            })`}
                        >
                            <rect
                                width={BOX_WIDTH}
                                height={BOX_HEIGHT}
                                fill="white"
                                stroke={chain.color}
                                strokeWidth="2"
                            />
                            <text
                                x={BOX_WIDTH / 2}
                                y={BOX_HEIGHT / 2 + 4}
                                textAnchor="middle"
                                fontSize="11"
                            >
                                {shorten(node.name || node.os_id)}
                            </text>
                        </g>
                    ))}
                </g>
            </svg>
        </div>
    );
}

SupplyChainDiagram.propTypes = {
    chain: object.isRequired,
};

/*
Lets a contributor put together supply chains from their own facilities, to
show on their embedded map: which locations are in a chain, which supplies
which, and whether visitors can see it yet.
*/
function EmbeddedMapSupplyChainsConfig({ contributorId, onSaved }) {
    const [chains, setChains] = useState([]);
    const [loadError, setLoadError] = useState('');
    const [draft, setDraft] = useState(null);
    const [errors, setErrors] = useState([]);
    const [saving, setSaving] = useState(false);
    const [confirmingDelete, setConfirmingDelete] = useState(null);
    const [searchText, setSearchText] = useState('');
    const [searchResults, setSearchResults] = useState(null);

    const loadChains = () =>
        apiRequest
            .get(makeEmbedSupplyChainsURL())
            .then(({ data }) => {
                setChains(data);
                setLoadError('');
            })
            .catch(() =>
                setLoadError('Your supply chains could not be loaded.'),
            );

    useEffect(() => {
        loadChains();
    }, []);

    // Look up the contributor's own facilities as they type.
    useEffect(() => {
        const text = searchText.trim();
        if (text.length < 2 || !contributorId) {
            setSearchResults(null);
            return undefined;
        }
        let current = true;
        const timer = setTimeout(() => {
            apiRequest
                .get(makeOwnFacilitiesSearchURL(contributorId, text))
                .then(({ data }) => {
                    if (!current) return;
                    setSearchResults(
                        (data.features || []).map(({ id, properties }) => ({
                            osId: properties.os_id || id,
                            name: properties.name,
                            countryName: properties.country_name,
                        })),
                    );
                })
                .catch(() => current && setSearchResults([]));
        }, 300);
        return () => {
            current = false;
            clearTimeout(timer);
        };
    }, [searchText, contributorId]);

    const closeEditor = () => {
        setDraft(null);
        setErrors([]);
        setSearchText('');
    };

    const save = () => {
        if (!draft.name.trim()) {
            setErrors(['Give the supply chain a name.']);
            return;
        }
        setSaving(true);
        const request = draft.id
            ? apiRequest.put(
                  makeEmbedSupplyChainsURL(draft.id),
                  formatChainForAPI(draft),
              )
            : apiRequest.post(
                  makeEmbedSupplyChainsURL(),
                  formatChainForAPI(draft),
              );
        request
            .then(() => {
                closeEditor();
                onSaved();
                return loadChains();
            })
            .catch(error =>
                setErrors(getChainErrorMessages(error?.response?.data)),
            )
            .then(() => setSaving(false));
    };

    const remove = id =>
        apiRequest
            .delete(makeEmbedSupplyChainsURL(id))
            .then(() => {
                setConfirmingDelete(null);
                onSaved();
                return loadChains();
            })
            .catch(() =>
                setLoadError('The supply chain could not be deleted.'),
            );

    if (!draft) {
        return (
            <div style={styles.section}>
                <Typography style={styles.sectionHeader}>
                    Supply chains
                </Typography>
                <Typography>
                    Show visitors how a product is made. Pick the facilities
                    involved and say which supplies which; visitors can then
                    follow the chain on your map.
                </Typography>
                {loadError && (
                    <Typography style={styles.error}>{loadError}</Typography>
                )}
                {chains.map(chain => (
                    <div key={chain.id} style={styles.row}>
                        <span style={styles.rowName}>
                            <span
                                style={{
                                    ...styles.swatch,
                                    background: chain.color,
                                }}
                            />
                            {chain.name}
                            <span style={styles.status}>
                                {chain.is_published ? 'Published' : 'Draft'} ·{' '}
                                {chain.nodes.length}{' '}
                                {chain.nodes.length === 1
                                    ? 'location'
                                    : 'locations'}
                            </span>
                        </span>
                        <span style={styles.actions}>
                            <button
                                type="button"
                                style={styles.button}
                                onClick={() => {
                                    setConfirmingDelete(null);
                                    setDraft(chain);
                                }}
                            >
                                Edit
                            </button>
                            <button
                                type="button"
                                style={styles.button}
                                onClick={() =>
                                    confirmingDelete === chain.id
                                        ? remove(chain.id)
                                        : setConfirmingDelete(chain.id)
                                }
                            >
                                {confirmingDelete === chain.id
                                    ? 'Confirm delete'
                                    : 'Delete'}
                            </button>
                        </span>
                    </div>
                ))}
                <div style={styles.footer}>
                    <button
                        type="button"
                        style={{ ...styles.button, ...styles.primaryButton }}
                        onClick={() => setDraft(makeEmptyChain())}
                    >
                        New supply chain
                    </button>
                </div>
            </div>
        );
    }

    const update = field => event => {
        const { value } = event.target;
        setDraft(chain => ({ ...chain, [field]: value }));
    };
    const nameOf = osId =>
        (draft.nodes.find(node => node.os_id === osId) || {}).name || osId;
    const isFull = draft.nodes.length >= MAX_CHAIN_LOCATIONS;

    return (
        <div style={styles.section}>
            <Typography style={styles.sectionHeader}>
                {draft.id ? 'Edit supply chain' : 'New supply chain'}
            </Typography>

            <label style={styles.label} htmlFor="chain-name">
                Name
            </label>
            <input
                id="chain-name"
                style={styles.input}
                maxLength={200}
                placeholder="e.g. Trail Rain Jacket"
                value={draft.name}
                onChange={update('name')}
            />
            <label style={styles.label} htmlFor="chain-description">
                Description
            </label>
            <textarea
                id="chain-description"
                style={styles.input}
                rows={3}
                maxLength={600}
                value={draft.description}
                onChange={update('description')}
            />
            <label style={styles.label} htmlFor="chain-product-url">
                Product link
            </label>
            <input
                id="chain-product-url"
                style={styles.input}
                maxLength={500}
                placeholder="https://"
                value={draft.product_url}
                onChange={update('product_url')}
            />
            <label style={styles.label} htmlFor="chain-color">
                Color on the map
            </label>
            <input
                id="chain-color"
                type="color"
                value={draft.color}
                onChange={update('color')}
            />

            <Typography style={styles.subHeader}>Locations</Typography>
            <input
                aria-label="Search your facilities"
                style={styles.input}
                placeholder="Search your facilities by name or OS ID"
                value={searchText}
                disabled={isFull}
                onChange={event => setSearchText(event.target.value)}
            />
            {isFull && (
                <Typography style={styles.hint}>
                    A supply chain can have at most {MAX_CHAIN_LOCATIONS}{' '}
                    locations.
                </Typography>
            )}
            {searchResults && !searchResults.length && (
                <Typography style={styles.hint}>
                    None of your facilities match.
                </Typography>
            )}
            {(searchResults || []).map(result => {
                const added = draft.nodes.some(
                    node => node.os_id === result.osId,
                );
                return (
                    <div key={result.osId} style={styles.row}>
                        <span style={{ minWidth: 0 }}>
                            {result.name}
                            <div style={styles.osId}>
                                {result.countryName} · {result.osId}
                            </div>
                        </span>
                        <button
                            type="button"
                            style={styles.button}
                            disabled={added || isFull}
                            onClick={() =>
                                setDraft(chain =>
                                    addChainLocation(chain, result),
                                )
                            }
                        >
                            {added ? 'Added' : 'Add'}
                        </button>
                    </div>
                );
            })}

            {draft.nodes.length ? (
                <Typography style={styles.subHeader}>
                    In this supply chain
                </Typography>
            ) : (
                <Typography style={styles.hint}>
                    No locations yet. Search above to add the first.
                </Typography>
            )}
            <datalist id="chain-stage-suggestions">
                {CHAIN_STAGE_SUGGESTIONS.map(stage => (
                    <option key={stage} value={stage}>
                        {stage}
                    </option>
                ))}
            </datalist>
            {draft.nodes.map(node => {
                const customers = draft.links
                    .filter(([supplier]) => supplier === node.os_id)
                    .map(([, customer]) => customer);
                const possible = getPossibleCustomers(draft, node.os_id);
                return (
                    <div key={node.os_id} style={styles.location}>
                        <div style={styles.locationHeader}>
                            <span style={{ minWidth: 0 }}>
                                <strong>{node.name || node.os_id}</strong>
                                <div style={styles.osId}>{node.os_id}</div>
                            </span>
                            <button
                                type="button"
                                style={styles.button}
                                onClick={() =>
                                    setDraft(chain =>
                                        removeChainLocation(chain, node.os_id),
                                    )
                                }
                            >
                                Remove
                            </button>
                        </div>
                        <label
                            style={styles.label}
                            htmlFor={`stage-${node.os_id}`}
                        >
                            What happens here
                        </label>
                        <input
                            id={`stage-${node.os_id}`}
                            style={styles.input}
                            list="chain-stage-suggestions"
                            maxLength={60}
                            placeholder="e.g. Final assembly"
                            value={node.stage || ''}
                            onChange={event => {
                                const { value } = event.target;
                                setDraft(chain =>
                                    setChainLocationStage(
                                        chain,
                                        node.os_id,
                                        value,
                                    ),
                                );
                            }}
                        />
                        <div style={styles.label}>Supplies</div>
                        {customers.map(customer => (
                            <span key={customer} style={styles.chip}>
                                {nameOf(customer)}
                                <button
                                    type="button"
                                    style={styles.chipRemove}
                                    aria-label={`Stop supplying ${nameOf(
                                        customer,
                                    )}`}
                                    onClick={() =>
                                        setDraft(chain =>
                                            removeChainLink(
                                                chain,
                                                node.os_id,
                                                customer,
                                            ),
                                        )
                                    }
                                >
                                    ×
                                </button>
                            </span>
                        ))}
                        {possible.length ? (
                            <select
                                aria-label={`Add a location ${
                                    node.name || node.os_id
                                } supplies`}
                                style={{ ...styles.input, marginTop: '6px' }}
                                value=""
                                onChange={event => {
                                    const { value } = event.target;
                                    if (!value) return;
                                    setDraft(chain =>
                                        addChainLink(chain, node.os_id, value),
                                    );
                                }}
                            >
                                <option value="">
                                    Add a location it supplies…
                                </option>
                                {possible.map(option => (
                                    <option
                                        key={option.os_id}
                                        value={option.os_id}
                                    >
                                        {option.name || option.os_id}
                                    </option>
                                ))}
                            </select>
                        ) : (
                            !customers.length && (
                                <Typography style={styles.hint}>
                                    {draft.nodes.length > 1
                                        ? 'The chain ends here: every other location already leads to this one.'
                                        : 'Add another location to link this one to.'}
                                </Typography>
                            )
                        )}
                    </div>
                );
            })}

            {draft.nodes.length > 1 && (
                <>
                    <Typography style={styles.subHeader}>
                        How it fits together
                    </Typography>
                    <SupplyChainDiagram chain={draft} />
                </>
            )}

            <div style={{ marginTop: '16px' }}>
                <FormControlLabel
                    control={
                        <Checkbox
                            checked={draft.is_published}
                            onChange={event => {
                                const { checked } = event.target;
                                setDraft(chain => ({
                                    ...chain,
                                    is_published: checked,
                                }));
                            }}
                            style={{ color: 'rgb(0, 0, 0)' }}
                        />
                    }
                    label="Published: visitors can follow this supply chain"
                />
            </div>

            {errors.map(message => (
                <Typography key={message} style={styles.error}>
                    {message}
                </Typography>
            ))}
            <div style={styles.footer}>
                <button
                    type="button"
                    style={{ ...styles.button, ...styles.primaryButton }}
                    disabled={saving}
                    onClick={save}
                >
                    {saving ? 'Saving…' : 'Save supply chain'}
                </button>
                <button
                    type="button"
                    style={styles.button}
                    disabled={saving}
                    onClick={closeEditor}
                >
                    Cancel
                </button>
            </div>
        </div>
    );
}

EmbeddedMapSupplyChainsConfig.defaultProps = {
    contributorId: null,
    onSaved: () => {},
};

EmbeddedMapSupplyChainsConfig.propTypes = {
    contributorId: oneOfType([number, string]),
    onSaved: func,
};

export default EmbeddedMapSupplyChainsConfig;
