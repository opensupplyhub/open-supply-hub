import React, { useEffect, useMemo, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { bool, func, number, object, oneOfType, string } from 'prop-types';
import Typography from '@material-ui/core/Typography';
import Checkbox from '@material-ui/core/Checkbox';
import FormControlLabel from '@material-ui/core/FormControlLabel';

import EmbeddedMapSupplyChainMap from './EmbeddedMapSupplyChainMap';
import EmbedSupplyChainSchematic from './EmbedSupplyChainSchematic';
import apiRequest from '../util/apiRequest';
import {
    makeEmbedSupplyChainsURL,
    makeEmbedSupplyChainLocationsURL,
    makeOwnFacilitiesSearchURL,
} from '../util/util';
import {
    CHAIN_STAGE_SUGGESTIONS,
    MAX_CHAIN_LOCATIONS,
    addChainLink,
    chainHasChanges,
    chainStructureKey,
    clickChainLocation,
    formatChainForAPI,
    getChainErrorMessages,
    getPossibleCustomers,
    makeEmptyChain,
    moveChain,
    removeChainLink,
    reverseChainLink,
    removeChainLocation,
    restoreChainStructure,
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
    locationSelected: {
        border: '2px solid rgb(13, 17, 40)',
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
    mapTools: {
        display: 'flex',
        justifyContent: 'flex-end',
        marginTop: '8px',
    },
    moveButton: {
        padding: '6px 8px',
        border: '1px solid rgb(13, 17, 40)',
        background: 'white',
        fontFamily: 'inherit',
        fontSize: '13px',
        fontWeight: 700,
        cursor: 'pointer',
    },
    schematicPanel: {
        marginTop: '16px',
        padding: '16px 20px 20px',
        background: 'rgb(255, 255, 255)',
        border: BORDER,
    },
    schematicHeader: {
        color: 'rgb(0, 0, 0)',
        fontSize: '18px',
        fontWeight: 700,
        marginBottom: '2px',
    },
    footer: {
        display: 'flex',
        gap: '8px',
        marginTop: '20px',
    },
};

/*
Lets a contributor put together supply chains from their own facilities, to
show on their embedded map: which locations are in a chain, which supplies
which, and whether visitors can see it yet.
*/
function EmbeddedMapSupplyChainsConfig({
    contributorId,
    onSaved,
    onUnsavedChange,
    active,
    schematicContainer,
}) {
    const [chains, setChains] = useState([]);
    const [loadError, setLoadError] = useState('');
    const [draft, setDraft] = useState(null);
    // The chain as it was when opened, to tell whether there is unsaved work.
    const [original, setOriginal] = useState(null);
    const [confirmingDiscard, setConfirmingDiscard] = useState(false);
    const [errors, setErrors] = useState([]);
    const [saving, setSaving] = useState(false);
    const [confirmingDelete, setConfirmingDelete] = useState(null);
    const [searchText, setSearchText] = useState('');
    const [searchResults, setSearchResults] = useState(null);
    // The contributor's facilities, for the map; and the location in the
    // chain that the next click will be linked to.
    const [locations, setLocations] = useState([]);
    const [selectedId, setSelectedId] = useState(null);
    const [clickMessage, setClickMessage] = useState('');

    useEffect(() => {
        apiRequest
            .get(makeEmbedSupplyChainLocationsURL())
            .then(({ data }) => setLocations(data))
            .catch(() => setLocations([]));
    }, []);

    const [tiers, countries] = useMemo(() => {
        const tierLookup = {};
        const countryLookup = {};
        locations.forEach(location => {
            tierLookup[location.os_id] = location.tier;
            countryLookup[location.os_id] = location.country_name;
        });
        return [tierLookup, countryLookup];
    }, [locations]);

    const hasUnsavedWork = !!draft && chainHasChanges(draft, original);

    // Unsaved work is kept while the other settings are open (this section
    // stays mounted), flagged on the section's tab, and the browser asks
    // before the page is closed or reloaded.
    useEffect(() => {
        onUnsavedChange(hasUnsavedWork);
    }, [hasUnsavedWork]);
    useEffect(() => {
        if (!hasUnsavedWork) return undefined;
        const warn = event => {
            event.preventDefault();
            // eslint-disable-next-line no-param-reassign
            event.returnValue = '';
        };
        window.addEventListener('beforeunload', warn);
        return () => window.removeEventListener('beforeunload', warn);
    }, [hasUnsavedWork]);

    // Each change to the chain's locations or links can be undone. The step
    // before the latest change is remembered whenever the structure changes.
    const [undoSteps, setUndoSteps] = useState([]);
    const lastStructure = useRef(null);
    const undoing = useRef(false);
    useEffect(() => {
        if (!draft) {
            lastStructure.current = null;
            setUndoSteps([]);
            return;
        }
        const key = chainStructureKey(draft);
        const last = lastStructure.current;
        if (last && last.key !== key && !undoing.current) {
            setUndoSteps(steps => [...steps.slice(-49), last]);
        }
        undoing.current = false;
        lastStructure.current = {
            key,
            nodes: draft.nodes,
            links: draft.links,
            selectedId,
        };
    }, [draft, selectedId]);

    const undo = () => {
        const step = undoSteps[undoSteps.length - 1];
        if (!step) return;
        undoing.current = true;
        setUndoSteps(steps => steps.slice(0, -1));
        setDraft(chain => restoreChainStructure(chain, step));
        setSelectedId(step.selectedId);
        setClickMessage('');
    };

    const openEditor = chain => {
        setConfirmingDelete(null);
        setConfirmingDiscard(false);
        setOriginal(chain);
        setDraft(chain);
    };

    // Clicking a facility, on the map or in the search results, adds it to
    // the chain and links it to the selected location.
    const pickLocation = ({ osId, name }) => {
        const result = clickChainLocation(
            draft,
            selectedId,
            { osId, name },
            tiers,
        );
        setDraft(result.chain);
        setSelectedId(result.selectedId);
        setClickMessage(result.message);
    };

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
        setOriginal(null);
        setConfirmingDiscard(false);
        setSelectedId(null);
        setClickMessage('');
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
            : apiRequest.post(makeEmbedSupplyChainsURL(), {
                  ...formatChainForAPI(draft),
                  // A new chain goes last.
                  order: chains.length,
              });
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

    // Move a chain up or down the list visitors see, and save the new order.
    const move = (id, direction) => {
        const moved = moveChain(chains, id, direction);
        if (moved === chains) return;
        setChains(moved.map((chain, order) => ({ ...chain, order })));
        Promise.all(
            moved
                .map((chain, order) => ({ chain, order }))
                .filter(({ chain, order }) => chain.order !== order)
                .map(({ chain, order }) =>
                    apiRequest.patch(makeEmbedSupplyChainsURL(chain.id), {
                        order,
                    }),
                ),
        )
            .then(() => {
                setLoadError('');
                onSaved();
            })
            .catch(() => {
                setLoadError('The new order could not be saved.');
                loadChains();
            });
    };

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
                {chains.length > 1 && (
                    <Typography style={styles.hint}>
                        Visitors see your published supply chains in this order.
                    </Typography>
                )}
                {chains.map((chain, index) => (
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
                                style={styles.moveButton}
                                aria-label={`Move ${chain.name} up`}
                                title="Move up"
                                disabled={index === 0}
                                onClick={() => move(chain.id, -1)}
                            >
                                ↑
                            </button>
                            <button
                                type="button"
                                style={styles.moveButton}
                                aria-label={`Move ${chain.name} down`}
                                title="Move down"
                                disabled={index === chains.length - 1}
                                onClick={() => move(chain.id, 1)}
                            >
                                ↓
                            </button>
                            <button
                                type="button"
                                style={styles.button}
                                onClick={() => openEditor(chain)}
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
                        onClick={() => openEditor(makeEmptyChain())}
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
    const selectedName = draft.nodes.some(node => node.os_id === selectedId)
        ? nameOf(selectedId)
        : '';
    const schematicChain = {
        ...draft,
        nodes: draft.nodes.map(node => ({
            ...node,
            tier: tiers[node.os_id],
            country_name: countries[node.os_id],
        })),
    };
    const toggleSelected = osId => {
        setClickMessage('');
        setSelectedId(osId === selectedId ? null : osId);
    };
    let locationsHint =
        'Click a dot, or search below, to add the first location. Starting with the final factory works well.';
    if (selectedName) {
        locationsHint = `${selectedName} is selected. Click another facility to link it to this one, or click it again to deselect it.`;
    } else if (draft.nodes.length) {
        locationsHint =
            'Click a location in the chain to select it, then click another facility to link the two.';
    }

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
            <Typography style={styles.hint}>{locationsHint}</Typography>
            {clickMessage && (
                <Typography style={styles.error}>{clickMessage}</Typography>
            )}
            <div style={styles.mapTools}>
                <button
                    type="button"
                    style={styles.button}
                    disabled={!undoSteps.length}
                    title="Undo the last change to the locations or links"
                    onClick={undo}
                >
                    ↶ Undo
                </button>
            </div>
            <EmbeddedMapSupplyChainMap
                chain={draft}
                locations={locations}
                selectedId={selectedId}
                onLocationClick={location =>
                    pickLocation({ osId: location.os_id, name: location.name })
                }
            />
            <div style={{ height: '10px' }} />
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
                            onClick={() => pickLocation(result)}
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
                    <div
                        key={node.os_id}
                        style={
                            node.os_id === selectedId
                                ? {
                                      ...styles.location,
                                      ...styles.locationSelected,
                                  }
                                : styles.location
                        }
                    >
                        <div style={styles.locationHeader}>
                            <span style={{ minWidth: 0 }}>
                                <strong>{node.name || node.os_id}</strong>
                                <div style={styles.osId}>{node.os_id}</div>
                            </span>
                            <span style={styles.actions}>
                                <button
                                    type="button"
                                    style={styles.button}
                                    aria-pressed={node.os_id === selectedId}
                                    onClick={() => {
                                        setClickMessage('');
                                        setSelectedId(
                                            node.os_id === selectedId
                                                ? null
                                                : node.os_id,
                                        );
                                    }}
                                >
                                    {node.os_id === selectedId
                                        ? 'Selected'
                                        : 'Select'}
                                </button>
                                <button
                                    type="button"
                                    style={styles.button}
                                    onClick={() => {
                                        if (node.os_id === selectedId) {
                                            setSelectedId(null);
                                        }
                                        setDraft(chain =>
                                            removeChainLocation(
                                                chain,
                                                node.os_id,
                                            ),
                                        );
                                    }}
                                >
                                    Remove
                                </button>
                            </span>
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
                                    title="Reverse this link"
                                    aria-label={`Reverse the link to ${nameOf(
                                        customer,
                                    )}`}
                                    onClick={() =>
                                        setDraft(chain =>
                                            reverseChainLink(
                                                chain,
                                                node.os_id,
                                                customer,
                                            ),
                                        )
                                    }
                                >
                                    ⇄
                                </button>
                                <button
                                    type="button"
                                    style={styles.chipRemove}
                                    title="Remove this link"
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
                    onClick={() =>
                        hasUnsavedWork && !confirmingDiscard
                            ? setConfirmingDiscard(true)
                            : closeEditor()
                    }
                >
                    {confirmingDiscard ? 'Discard changes' : 'Cancel'}
                </button>
            </div>
            {confirmingDiscard && (
                <Typography style={styles.hint}>
                    This supply chain has changes that are not saved.
                </Typography>
            )}
            {active &&
                schematicContainer &&
                createPortal(
                    <div style={styles.schematicPanel}>
                        <Typography style={styles.schematicHeader}>
                            Schematic view
                        </Typography>
                        <Typography
                            style={{ ...styles.hint, marginBottom: '8px' }}
                        >
                            The same supply chain without the geography, read
                            left to right. Click a location to select it.
                        </Typography>
                        <EmbedSupplyChainSchematic
                            chain={schematicChain}
                            selectedId={selectedId}
                            onSelect={toggleSelected}
                        />
                    </div>,
                    schematicContainer,
                )}
        </div>
    );
}

EmbeddedMapSupplyChainsConfig.defaultProps = {
    contributorId: null,
    onSaved: () => {},
    onUnsavedChange: () => {},
    active: true,
    schematicContainer: null,
};

EmbeddedMapSupplyChainsConfig.propTypes = {
    contributorId: oneOfType([number, string]),
    onSaved: func,
    onUnsavedChange: func,
    active: bool,
    schematicContainer: object,
};

export default EmbeddedMapSupplyChainsConfig;
