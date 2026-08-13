import React, { useEffect, useMemo, useRef, useState } from 'react';
import { arrayOf, bool, func, object, shape, string } from 'prop-types';
import CircularProgress from '@material-ui/core/CircularProgress';
import InputLabel from '@material-ui/core/InputLabel';
import { withStyles } from '@material-ui/core/styles';

import {
    getIsic4SearchIndex,
    getIsic4VisibleRows,
} from '../../../data/isic4SearchIndex';
import { loadIsic4Taxonomy } from '../../../data/loadIsic4Taxonomy';
import env from '../../../util/env';
import TaxonomySearchControl from './TaxonomySearchControl';
import TaxonomyResultRow from './TaxonomyResultRow';
import {
    getIsic4NodeKey,
    isIsic4NodeSelected,
    toggleIsic4Node,
} from './isicUtils';
import {
    filterRowsByExpandedState,
    getExpandedNodeIdsForRows,
    getIsic4ParentNodeId,
} from './utils';
import styles from './styles';

const reactSelectOptionPropType = shape({
    value: string.isRequired,
    label: string.isRequired,
});

function IsicTaxonomySearch({
    counts,
    isic4,
    onIsic4Change,
    onRequestCounts,
    disabled,
    classes,
}) {
    const [query, setQuery] = useState('');
    const [activeRowIndex, setActiveRowIndex] = useState(-1);
    const [isFocused, setIsFocused] = useState(false);
    const [expandedNodeIds, setExpandedNodeIds] = useState(new Set());
    const countsRequestedRef = useRef(false);
    const inputRef = useRef(null);
    const taxonomyVersion = env('ISIC4_TAXONOMY_VERSION') ?? 'unknown';
    const [taxonomyState, setTaxonomyState] = useState({
        status: 'loading',
        taxonomy: null,
        error: null,
    });

    useEffect(() => {
        let cancelled = false;

        loadIsic4Taxonomy()
            .then(taxonomy => {
                if (cancelled) {
                    return;
                }

                setTaxonomyState({
                    status: 'ready',
                    taxonomy,
                    error: null,
                });
            })
            .catch(error => {
                if (cancelled) {
                    return;
                }

                // eslint-disable-next-line no-console
                console.error('Failed to load ISIC taxonomy', error);
                setTaxonomyState({
                    status: 'error',
                    taxonomy: null,
                    error,
                });
            });

        return () => {
            cancelled = true;
        };
    }, [taxonomyVersion]);

    const searchIndex = useMemo(() => {
        if (taxonomyState.status !== 'ready' || !taxonomyState.taxonomy) {
            return null;
        }

        return getIsic4SearchIndex(taxonomyState.taxonomy, taxonomyVersion);
    }, [taxonomyState, taxonomyVersion]);

    const nodeById = useMemo(
        () =>
            searchIndex
                ? new Map(searchIndex.flatNodes.map(node => [node.id, node]))
                : new Map(),
        [searchIndex],
    );

    const trimmedQuery = query.trim();
    const isSearching = trimmedQuery.length > 0;

    const { rows, hint } = useMemo(() => {
        if (!searchIndex) {
            return Object.freeze({
                rows: [],
                hint: '',
            });
        }

        if (isSearching) {
            return getIsic4VisibleRows(searchIndex.flatNodes, query);
        }

        const browseRows = searchIndex.flatNodes.map(node => ({
            node,
            depth: node.depth,
            isParent: node.kind !== 'class',
            highlightQuery: '',
        }));

        return Object.freeze({
            rows: browseRows,
            hint:
                'Type to search all ISIC levels, or select a section to browse',
        });
    }, [isSearching, query, searchIndex]);

    useEffect(() => {
        if (isSearching) {
            setExpandedNodeIds(
                getExpandedNodeIdsForRows(
                    rows,
                    getIsic4NodeKey,
                    getIsic4ParentNodeId,
                    nodeById,
                ),
            );
            return;
        }

        setExpandedNodeIds(new Set());
    }, [isSearching, rows, nodeById]);

    const visibleRows = useMemo(
        () =>
            filterRowsByExpandedState(
                rows,
                expandedNodeIds,
                getIsic4ParentNodeId,
                nodeById,
                isSearching,
            ),
        [rows, expandedNodeIds, nodeById, isSearching],
    );

    const selectedChips = useMemo(
        () =>
            isic4.map(option => ({
                id: option.value,
                label: option.label,
            })),
        [isic4],
    );

    const showResultsPanel = isFocused || query.trim().length > 0;

    const requestCountsIfNeeded = () => {
        if (countsRequestedRef.current || !onRequestCounts) {
            return;
        }

        countsRequestedRef.current = true;
        onRequestCounts();
    };

    const handleFocus = () => {
        setIsFocused(true);
        requestCountsIfNeeded();
    };

    const handleToggleNode = node => {
        onIsic4Change(toggleIsic4Node(node, isic4));
        setQuery('');
        setActiveRowIndex(-1);
    };

    const handleToggleExpand = nodeId => {
        setExpandedNodeIds(current => {
            const next = new Set(current);
            if (next.has(nodeId)) {
                next.delete(nodeId);
            } else {
                next.add(nodeId);
            }
            return next;
        });
    };

    const handleRemoveChip = chipId => {
        onIsic4Change(isic4.filter(option => option.value !== chipId));
    };

    const handleInputKeyDown = event => {
        if (!showResultsPanel || visibleRows.length === 0) {
            return;
        }

        if (event.key === 'ArrowDown') {
            event.preventDefault();
            setActiveRowIndex(current =>
                current >= visibleRows.length - 1 ? 0 : current + 1,
            );
        } else if (event.key === 'ArrowUp') {
            event.preventDefault();
            setActiveRowIndex(current =>
                current <= 0 ? visibleRows.length - 1 : current - 1,
            );
        } else if (event.key === 'Enter' && activeRowIndex >= 0) {
            event.preventDefault();
            handleToggleNode(visibleRows[activeRowIndex].node);
        } else if (event.key === 'Escape') {
            setQuery('');
            setActiveRowIndex(-1);
            inputRef.current?.blur();
        }
    };

    const getCountForNode = node => {
        if (!counts || node.countKey == null) {
            return null;
        }

        const count = counts[node.countKey];
        return count == null ? null : count;
    };

    const listboxId = 'isic4-taxonomy-results';
    const label = 'International Standard Industrial Classification "ISIC"';

    if (taxonomyState.status === 'loading') {
        return (
            <div className={classes.root}>
                <InputLabel
                    shrink={false}
                    component="div"
                    className={classes.inputLabelStyle}
                >
                    {label}
                </InputLabel>
                <CircularProgress size={24} />
            </div>
        );
    }

    if (taxonomyState.status === 'error') {
        return (
            <div className={classes.root}>
                <InputLabel
                    shrink={false}
                    component="div"
                    className={classes.inputLabelStyle}
                >
                    {label}
                </InputLabel>
                <p className={classes.hint}>
                    Unable to load ISIC taxonomy. Try refreshing the page.
                </p>
            </div>
        );
    }

    if (!searchIndex) {
        return null;
    }

    return (
        <div className={classes.root}>
            <InputLabel
                shrink={false}
                component="div"
                className={classes.inputLabelStyle}
            >
                {label}
            </InputLabel>
            <TaxonomySearchControl
                inputId="isic4-taxonomy-search"
                inputRef={inputRef}
                query={query}
                onQueryChange={value => {
                    setQuery(value);
                    setActiveRowIndex(-1);
                    requestCountsIfNeeded();
                }}
                placeholder="Search ISIC section, division, group, or class"
                disabled={disabled}
                isFocused={isFocused}
                onFocus={handleFocus}
                onBlur={() => setIsFocused(false)}
                onKeyDown={handleInputKeyDown}
                selectedChips={selectedChips}
                onRemoveChip={handleRemoveChip}
                classes={classes}
                listboxId={listboxId}
                showResultsPanel={showResultsPanel}
                resultsCount={visibleRows.length}
            />

            {showResultsPanel && (
                <ul
                    id={listboxId}
                    className={classes.resultsPanel}
                    aria-label={label}
                >
                    {visibleRows.length === 0 ? (
                        <li className={classes.emptyResults}>
                            No matching ISIC categories
                        </li>
                    ) : (
                        visibleRows.map((row, index) => {
                            const {
                                node,
                                depth,
                                isParent,
                                highlightQuery,
                            } = row;
                            const selected = isIsic4NodeSelected(node, isic4);
                            const count = getCountForNode(node);
                            const rowId = getIsic4NodeKey(node);

                            return (
                                <TaxonomyResultRow
                                    key={rowId}
                                    id={`${listboxId}-option-${index}`}
                                    onMouseEnter={() =>
                                        setActiveRowIndex(index)
                                    }
                                    node={node}
                                    depth={depth}
                                    isParent={isParent}
                                    highlightQuery={highlightQuery}
                                    selected={selected}
                                    active={index === activeRowIndex}
                                    expanded={expandedNodeIds.has(rowId)}
                                    count={count}
                                    onToggleExpand={() =>
                                        handleToggleExpand(rowId)
                                    }
                                    onSelect={() => handleToggleNode(node)}
                                    classes={classes}
                                />
                            );
                        })
                    )}
                </ul>
            )}

            <p className={classes.hint}>
                {showResultsPanel
                    ? hint
                    : 'Click to browse ISIC sections, or type to search all levels'}
            </p>
        </div>
    );
}

IsicTaxonomySearch.defaultProps = {
    counts: null,
    isic4: [],
    disabled: false,
    onRequestCounts: null,
};

IsicTaxonomySearch.propTypes = {
    counts: object,
    isic4: arrayOf(reactSelectOptionPropType),
    onIsic4Change: func.isRequired,
    onRequestCounts: func,
    disabled: bool,
};

export default withStyles(styles)(IsicTaxonomySearch);
