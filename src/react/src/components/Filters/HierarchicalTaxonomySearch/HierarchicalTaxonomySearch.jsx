import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
    arrayOf,
    bool,
    func,
    object,
    shape,
    string,
} from 'prop-types';
import InputLabel from '@material-ui/core/InputLabel';
import { withStyles } from '@material-ui/core/styles';

import {
    getFacilityProcessingSearchIndex,
    getFacilityProcessingVisibleRows,
} from '../../../data/facilityProcessingSearchIndex';
import TaxonomySearchControl from './TaxonomySearchControl';
import TaxonomyResultRow from './TaxonomyResultRow';
import {
    filterRowsByExpandedState,
    getExpandedNodeIdsForRows,
    getFacilityProcessingNodeKey,
    getFacilityProcessingParentNodeId,
    isFacilityProcessingNodeSelected,
    removeFacilityProcessingNodeById,
    toggleFacilityProcessingNode,
} from './utils';
import styles from './styles';

const reactSelectOptionPropType = shape({
    value: string.isRequired,
    label: string.isRequired,
});

function HierarchicalTaxonomySearch({
    label,
    placeholder,
    counts,
    facilityType,
    processingType,
    onFacilityTypeChange,
    onProcessingTypeChange,
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

    const searchIndex = useMemo(() => getFacilityProcessingSearchIndex(), []);

    const nodeById = useMemo(() => {
        const map = new Map();
        searchIndex.groups.forEach(({ facilityNode, processingNodes }) => {
            map.set(facilityNode.id, facilityNode);
            processingNodes.forEach(node => map.set(node.id, node));
        });
        return map;
    }, [searchIndex]);

    const { rows, hint } = useMemo(
        () => getFacilityProcessingVisibleRows(searchIndex.groups, query),
        [query, searchIndex],
    );

    const trimmedQuery = query.trim();
    const isSearching = trimmedQuery.length > 0;

    useEffect(() => {
        if (isSearching) {
            setExpandedNodeIds(
                getExpandedNodeIdsForRows(
                    rows,
                    getFacilityProcessingNodeKey,
                    getFacilityProcessingParentNodeId,
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
                getFacilityProcessingParentNodeId,
                nodeById,
                isSearching,
            ),
        [rows, expandedNodeIds, nodeById, isSearching],
    );

    const selectedChips = useMemo(() => {
        const chips = [];

        facilityType.forEach(option => {
            chips.push({
                id: `facility_type:${option.value}`,
                label: option.label,
            });
        });

        processingType.forEach(option => {
            chips.push({
                id: `processing_type:${searchIndex.groups.find(group =>
                    group.processingNodes.some(
                        node => node.label === option.value,
                    ),
                )?.facilityNode.facilityType ?? 'unknown'}:${option.value}`,
                label: option.label,
            });
        });

        return chips;
    }, [facilityType, processingType, searchIndex.groups]);

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
        const nextSelection = toggleFacilityProcessingNode(
            node,
            facilityType,
            processingType,
        );
        onFacilityTypeChange(nextSelection.facilityType);
        onProcessingTypeChange(nextSelection.processingType);
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
        const nextSelection = removeFacilityProcessingNodeById(
            chipId,
            facilityType,
            processingType,
        );
        onFacilityTypeChange(nextSelection.facilityType);
        onProcessingTypeChange(nextSelection.processingType);
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

    const listboxId = 'facility-processing-taxonomy-results';

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
                inputId="facility-processing-taxonomy-search"
                inputRef={inputRef}
                query={query}
                onQueryChange={value => {
                    setQuery(value);
                    setActiveRowIndex(-1);
                    requestCountsIfNeeded();
                }}
                placeholder={placeholder}
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
                <div
                    id={listboxId}
                    className={classes.resultsPanel}
                    role="listbox"
                    aria-label={label}
                    aria-multiselectable="true"
                >
                    {visibleRows.length === 0 ? (
                        <div className={classes.emptyResults}>
                            No matching facility or processing types
                        </div>
                    ) : (
                        visibleRows.map((row, index) => {
                            const { node, depth, isParent, highlightQuery } =
                                row;
                            const selected = isFacilityProcessingNodeSelected(
                                node,
                                facilityType,
                                processingType,
                            );
                            const count = getCountForNode(node);
                            const rowId = getFacilityProcessingNodeKey(node);

                            return (
                                <div
                                    key={rowId}
                                    id={`${listboxId}-option-${index}`}
                                    onMouseEnter={() =>
                                        setActiveRowIndex(index)
                                    }
                                >
                                    <TaxonomyResultRow
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
                                </div>
                            );
                        })
                    )}
                </div>
            )}

            <p className={classes.hint}>
                {showResultsPanel
                    ? hint
                    : 'Click to browse facility types, or type to search both levels at once'}
            </p>
        </div>
    );
}

HierarchicalTaxonomySearch.defaultProps = {
    counts: null,
    facilityType: [],
    processingType: [],
    disabled: false,
    onRequestCounts: null,
};

HierarchicalTaxonomySearch.propTypes = {
    label: string.isRequired,
    placeholder: string.isRequired,
    counts: object,
    facilityType: arrayOf(reactSelectOptionPropType),
    processingType: arrayOf(reactSelectOptionPropType),
    onFacilityTypeChange: func.isRequired,
    onProcessingTypeChange: func.isRequired,
    onRequestCounts: func,
    disabled: bool,
};

export default withStyles(styles)(HierarchicalTaxonomySearch);
