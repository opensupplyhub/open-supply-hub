import React, { useMemo, useRef, useState } from 'react';
import { arrayOf, bool, func, object, shape, string } from 'prop-types';
import InputLabel from '@material-ui/core/InputLabel';
import CheckBoxIcon from '@material-ui/icons/CheckBox';
import CheckBoxOutlineBlankIcon from '@material-ui/icons/CheckBoxOutlineBlank';
import { withStyles } from '@material-ui/core/styles';

import SearchIcon from '../../SearchIcon';
import {
    getIsic4SearchIndex,
    getIsic4VisibleRows,
} from '../../../data/isic4SearchIndex';
import {
    getIsic4NodeKey,
    isIsic4NodeSelected,
    toggleIsic4Node,
} from './isicUtils';
import { splitLabelForHighlight } from './utils';
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
    const countsRequestedRef = useRef(false);
    const inputRef = useRef(null);

    const searchIndex = useMemo(() => getIsic4SearchIndex(), []);

    const { rows, hint } = useMemo(
        () => getIsic4VisibleRows(searchIndex.flatNodes, query),
        [query, searchIndex],
    );

    const selectedChips = useMemo(
        () =>
            isic4.map(option => ({
                id: option.value,
                label: option.label,
                context: option.value.split(':')[0],
            })),
        [isic4],
    );

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
        onIsic4Change(toggleIsic4Node(node, isic4));
    };

    const handleRemoveChip = chipId => {
        onIsic4Change(isic4.filter(option => option.value !== chipId));
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

    const listboxId = 'isic4-taxonomy-results';
    const label = 'ISIC Rev 4';

    return (
        <div className={classes.root}>
            <InputLabel
                shrink={false}
                htmlFor="isic4-taxonomy-search"
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
                    id="isic4-taxonomy-search"
                    type="text"
                    className={classes.searchInput}
                    value={query}
                    placeholder="Search ISIC section, division, group, or class"
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
                            No matching ISIC categories
                        </div>
                    ) : (
                        rows.map((row, index) => {
                            const { node, depth, isParent, highlightQuery } =
                                row;
                            const selected = isIsic4NodeSelected(node, isic4);
                            const count = getCountForNode(node);
                            const rowId = getIsic4NodeKey(node);
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
