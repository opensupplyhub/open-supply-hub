import React, { useMemo, useRef, useState } from 'react';
import {
    arrayOf,
    bool,
    func,
    object,
    shape,
    string,
} from 'prop-types';
import InputLabel from '@material-ui/core/InputLabel';
import CheckBoxIcon from '@material-ui/icons/CheckBox';
import CheckBoxOutlineBlankIcon from '@material-ui/icons/CheckBoxOutlineBlank';
import { withStyles } from '@material-ui/core/styles';

import SearchIcon from '../../SearchIcon';
import {
    getFacilityProcessingSearchIndex,
    getFacilityProcessingVisibleRows,
} from '../../../data/facilityProcessingSearchIndex';
import {
    getFacilityProcessingNodeKey,
    isFacilityProcessingNodeSelected,
    removeFacilityProcessingNodeById,
    splitLabelForHighlight,
    toggleFacilityProcessingNode,
} from './utils';
import styles from './styles';

const reactSelectOptionPropType = shape({
    value: string.isRequired,
    label: string.isRequired,
});

function HighlightedLabel({ label, highlightQuery, classes }) {
    const parts = splitLabelForHighlight(label, highlightQuery);

    return (
        <span>
            {parts.map((part, index) => (
                <span
                    key={`${index}-${part.text}`}
                    className={part.highlighted ? classes.highlight : undefined}
                >
                    {part.text}
                </span>
            ))}
        </span>
    );
}

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
    const countsRequestedRef = useRef(false);
    const inputRef = useRef(null);

    const searchIndex = useMemo(() => getFacilityProcessingSearchIndex(), []);

    const { rows, hint } = useMemo(
        () => getFacilityProcessingVisibleRows(searchIndex.groups, query),
        [query, searchIndex],
    );

    const selectedChips = useMemo(() => {
        const chips = [];

        facilityType.forEach(option => {
            chips.push({
                id: `facility_type:${option.value}`,
                label: option.label,
                context: 'facility',
            });
        });

        processingType.forEach(option => {
            const parentGroup = searchIndex.groups.find(group =>
                group.processingNodes.some(
                    node => node.label === option.value,
                ),
            );

            chips.push({
                id: `processing_type:${parentGroup?.facilityNode.facilityType}:${option.value}`,
                label: option.label,
                context: parentGroup?.facilityNode.facilityType ?? 'processing',
            });
        });

        return chips;
    }, [facilityType, processingType, searchIndex.groups]);

    const showResultsPanel =
        isFocused || query.trim().length > 0 || selectedChips.length > 0;

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
        if (!showResultsPanel || rows.length === 0) {
            return;
        }

        if (event.key === 'ArrowDown') {
            event.preventDefault();
            setActiveRowIndex(current =>
                current >= rows.length - 1 ? 0 : current + 1,
            );
        } else if (event.key === 'ArrowUp') {
            event.preventDefault();
            setActiveRowIndex(current =>
                current <= 0 ? rows.length - 1 : current - 1,
            );
        } else if (event.key === 'Enter' && activeRowIndex >= 0) {
            event.preventDefault();
            handleToggleNode(rows[activeRowIndex].node);
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
                htmlFor="facility-processing-taxonomy-search"
                className={classes.inputLabelStyle}
            >
                {label}
            </InputLabel>
            <div className={classes.searchInputWrapper}>
                <span className={classes.searchIcon} aria-hidden="true">
                    <SearchIcon />
                </span>
                <input
                    ref={inputRef}
                    id="facility-processing-taxonomy-search"
                    type="text"
                    className={classes.searchInput}
                    value={query}
                    placeholder={placeholder}
                    disabled={disabled}
                    aria-controls={showResultsPanel ? listboxId : undefined}
                    aria-autocomplete="list"
                    aria-expanded={showResultsPanel && rows.length > 0}
                    role="combobox"
                    onFocus={handleFocus}
                    onBlur={() => setIsFocused(false)}
                    onChange={event => {
                        setQuery(event.target.value);
                        setActiveRowIndex(-1);
                        requestCountsIfNeeded();
                    }}
                    onKeyDown={handleInputKeyDown}
                />
            </div>

            {selectedChips.length > 0 && (
                <div className={classes.chips}>
                    {selectedChips.map(chip => (
                        <span key={chip.id} className={classes.chip}>
                            <span className={classes.chipLabel}>
                                {chip.label}
                            </span>
                            <span className={classes.chipContext}>
                                · {chip.context}
                            </span>
                            <button
                                type="button"
                                className={classes.chipRemove}
                                aria-label={`Remove ${chip.label}`}
                                onClick={() => handleRemoveChip(chip.id)}
                            >
                                ×
                            </button>
                        </span>
                    ))}
                </div>
            )}

            {showResultsPanel && (
                <div
                    id={listboxId}
                    className={classes.resultsPanel}
                    role="listbox"
                    aria-label={label}
                    aria-multiselectable="true"
                >
                    {rows.length === 0 ? (
                        <div className={classes.emptyResults}>
                            No matching facility or processing types
                        </div>
                    ) : (
                        rows.map((row, index) => {
                            const { node, depth, isParent, highlightQuery } =
                                row;
                            const selected = isFacilityProcessingNodeSelected(
                                node,
                                facilityType,
                                processingType,
                            );
                            const count = getCountForNode(node);
                            const rowId = getFacilityProcessingNodeKey(node);
                            const indentStyle = {
                                paddingLeft: `${12 + depth * 22}px`,
                            };

                            return (
                                <div
                                    key={rowId}
                                    id={`${listboxId}-option-${index}`}
                                    role="option"
                                    aria-selected={selected}
                                    className={`${classes.resultRow} ${
                                        selected || index === activeRowIndex
                                            ? classes.resultRowSelected
                                            : ''
                                    }`}
                                    style={indentStyle}
                                    onMouseDown={event =>
                                        event.preventDefault()
                                    }
                                    onMouseEnter={() =>
                                        setActiveRowIndex(index)
                                    }
                                    onClick={() => handleToggleNode(node)}
                                >
                                    {selected ? (
                                        <CheckBoxIcon
                                            className={`${classes.resultRowIcon} ${classes.resultRowIconSelected}`}
                                            aria-hidden="true"
                                        />
                                    ) : (
                                        <CheckBoxOutlineBlankIcon
                                            className={classes.resultRowIcon}
                                            aria-hidden="true"
                                        />
                                    )}
                                    <span
                                        className={`${classes.resultRowLabel} ${
                                            isParent
                                                ? classes.resultRowLabelParent
                                                : ''
                                        }`}
                                    >
                                        <HighlightedLabel
                                            label={node.displayLabel}
                                            highlightQuery={highlightQuery}
                                            classes={classes}
                                        />
                                    </span>
                                    {count != null && (
                                        <span
                                            className={classes.resultRowCount}
                                        >
                                            {count.toLocaleString()}
                                        </span>
                                    )}
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
