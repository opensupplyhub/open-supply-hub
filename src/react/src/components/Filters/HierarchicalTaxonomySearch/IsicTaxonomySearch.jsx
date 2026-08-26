import React, { useEffect, useMemo, useRef, useState } from 'react';
import { arrayOf, bool, func, object, shape, string } from 'prop-types';
import { connect, useDispatch } from 'react-redux';
import CircularProgress from '@material-ui/core/CircularProgress';
import IconButton from '@material-ui/core/IconButton';
import InputLabel from '@material-ui/core/InputLabel';
import Popper from '@material-ui/core/Popper';
import { withStyles } from '@material-ui/core/styles';
import InfoOutlinedIcon from '@material-ui/icons/InfoOutlined';

import {
    getIsic4SearchIndex,
    getIsic4VisibleRows,
} from '../../../data/isic4SearchIndex';
import { fetchIsic4Taxonomy } from '../../../actions/filterOptions';
import TaxonomySearchControl from './TaxonomySearchControl';
import TaxonomyResultRow from './TaxonomyResultRow';
import {
    getIsic4NodeKey,
    isIsic4NodeSelected,
    resolveIsic4FilterLabels,
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

export function IsicTaxonomySearch({
    counts,
    isic4,
    onIsic4Change,
    onRequestCounts,
    disabled,
    classes,
    isic4Taxonomy,
}) {
    const dispatch = useDispatch();
    const [query, setQuery] = useState('');
    const [activeRowIndex, setActiveRowIndex] = useState(-1);
    const [isFocused, setIsFocused] = useState(false);
    const [infoAnchorEl, setInfoAnchorEl] = useState(null);
    const [expandedNodeIds, setExpandedNodeIds] = useState(new Set());
    const countsRequestedRef = useRef(false);
    const inputRef = useRef(null);
    const infoCloseTimerRef = useRef(null);
    const { config: isic4TaxonomyConfig, data: taxonomy, fetching, error } =
        isic4Taxonomy ?? {};
    const taxonomyVersion =
        isic4TaxonomyConfig?.version != null
            ? String(isic4TaxonomyConfig.version)
            : 'unknown';

    useEffect(() => {
        if (!taxonomy && !fetching && !error) {
            dispatch(fetchIsic4Taxonomy());
        }
    }, [dispatch, taxonomy, fetching, error]);

    useEffect(
        () => () => {
            if (infoCloseTimerRef.current) {
                clearTimeout(infoCloseTimerRef.current);
            }
        },
        [],
    );

    const searchIndex = useMemo(() => {
        if (!taxonomy) {
            return null;
        }

        return getIsic4SearchIndex(taxonomy, taxonomyVersion);
    }, [taxonomy, taxonomyVersion]);

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

    useEffect(() => {
        if (!searchIndex || !isic4.length) {
            return;
        }

        const resolved = resolveIsic4FilterLabels(isic4, searchIndex.flatNodes);
        if (
            resolved.some(
                (option, index) => option.label !== isic4[index].label,
            )
        ) {
            onIsic4Change(resolved);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [searchIndex, isic4]);

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
    const infoPopoverId = 'isic4-taxonomy-information';
    const infoPopoverTitleId = 'isic4-taxonomy-information-title';
    const label = 'International Standard Industrial Classification "ISIC"';
    const keepInfoOpen = () => {
        if (infoCloseTimerRef.current) {
            clearTimeout(infoCloseTimerRef.current);
            infoCloseTimerRef.current = null;
        }
    };
    const openInfo = event => {
        keepInfoOpen();
        setInfoAnchorEl(event.currentTarget);
    };
    const closeInfoSoon = () => {
        keepInfoOpen();
        infoCloseTimerRef.current = setTimeout(() => {
            setInfoAnchorEl(null);
        }, 100);
    };
    const renderLabel = () => (
        <InputLabel
            shrink={false}
            component="div"
            className={classes.inputLabelStyle}
        >
            <span className={classes.labelWithInfo}>
                {label}
                <IconButton
                    className={classes.infoButton}
                    aria-label="What is ISIC?"
                    aria-haspopup="dialog"
                    aria-controls={infoAnchorEl ? infoPopoverId : undefined}
                    aria-expanded={Boolean(infoAnchorEl)}
                    onMouseEnter={openInfo}
                    onMouseLeave={closeInfoSoon}
                    onFocus={openInfo}
                    onBlur={closeInfoSoon}
                    onKeyDown={event => {
                        if (event.key === 'Escape') {
                            keepInfoOpen();
                            setInfoAnchorEl(null);
                        }
                    }}
                >
                    <InfoOutlinedIcon fontSize="small" />
                </IconButton>
            </span>
            <Popper
                open={Boolean(infoAnchorEl)}
                anchorEl={infoAnchorEl}
                placement="bottom-start"
                className={classes.infoPopper}
            >
                <div
                    id={infoPopoverId}
                    className={classes.infoPopover}
                    role="dialog"
                    aria-labelledby={infoPopoverTitleId}
                    onMouseEnter={keepInfoOpen}
                    onMouseLeave={closeInfoSoon}
                    onFocus={keepInfoOpen}
                    onBlur={closeInfoSoon}
                >
                    <strong id={infoPopoverTitleId}>What is ISIC?</strong>
                    <p>
                        The International Standard Industrial Classification
                        (ISIC) is the United Nations&apos; system for
                        classifying businesses by the kind of economic activity
                        they perform. It&apos;s used by governments and
                        statistical agencies worldwide, and it covers every
                        industry.
                    </p>
                    <p>
                        Codes run from broad to specific: <strong>C</strong>{' '}
                        Manufacturing → <strong>14</strong> Manufacture of
                        wearing apparel → <strong>1410</strong> Manufacture of
                        wearing apparel, except fur apparel.
                    </p>
                    <a
                        href="https://unstats.un.org/unsd/classifications/Econ/isic"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        Learn more
                    </a>
                    .
                </div>
            </Popper>
        </InputLabel>
    );

    if (!taxonomy && !fetching && !error) {
        return null;
    }

    if (fetching || !taxonomy) {
        return (
            <div className={classes.root}>
                {renderLabel()}
                <CircularProgress size={24} />
            </div>
        );
    }

    if (error) {
        return (
            <div className={classes.root}>
                {renderLabel()}
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
            {renderLabel()}
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
    isic4Taxonomy: Object.freeze({
        config: null,
        data: null,
        fetching: false,
        error: null,
    }),
};

IsicTaxonomySearch.propTypes = {
    counts: object,
    isic4: arrayOf(reactSelectOptionPropType),
    onIsic4Change: func.isRequired,
    onRequestCounts: func,
    disabled: bool,
    isic4Taxonomy: object,
};

function mapStateToProps({
    filterOptions: {
        isic4Taxonomy = Object.freeze({
            config: null,
            data: null,
            fetching: false,
            error: null,
        }),
    } = {},
}) {
    return { isic4Taxonomy };
}

export default connect(mapStateToProps)(withStyles(styles)(IsicTaxonomySearch));
