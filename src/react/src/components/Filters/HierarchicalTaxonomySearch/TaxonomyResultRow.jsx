import React from 'react';
import { bool, func, number, object, oneOfType, string } from 'prop-types';
import IconButton from '@material-ui/core/IconButton';
import ChevronRightIcon from '@material-ui/icons/ChevronRight';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';

import { splitLabelForHighlight } from './utils';

function HighlightedLabel({ label, highlightQuery, classes }) {
    const parts = splitLabelForHighlight(label, highlightQuery);
    let textOffset = 0;

    return (
        <span>
            {parts.map(part => {
                const key = `${textOffset}-${part.text}`;
                textOffset += part.text.length;

                return (
                    <span
                        key={key}
                        className={
                            part.highlighted ? classes.highlight : undefined
                        }
                    >
                        {part.text}
                    </span>
                );
            })}
        </span>
    );
}

function TaxonomyResultRow({
    node,
    depth,
    isParent,
    highlightQuery,
    selected,
    active,
    expanded,
    count,
    onToggleExpand,
    onSelect,
    classes,
}) {
    const isParentRow = isParent;
    const paddingLeft = isParentRow
        ? 12 + depth * 22
        : 55 + Math.max(0, depth - 1) * 22;

    const handleChevronClick = event => {
        event.stopPropagation();
        onToggleExpand();
    };

    const handleRowClick = () => {
        onSelect();
    };

    const handleRowKeyDown = event => {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            handleRowClick();
        }
    };

    return (
        <div
            role="option"
            aria-selected={selected}
            tabIndex={0}
            className={`${
                isParentRow ? classes.resultRowParent : classes.resultRowChild
            } ${selected || active ? classes.resultRowSelected : ''}`}
            style={{ paddingLeft: `${paddingLeft}px` }}
            onMouseDown={event => event.preventDefault()}
            onClick={handleRowClick}
            onKeyDown={handleRowKeyDown}
        >
            {isParentRow && (
                <IconButton
                    onClick={handleChevronClick}
                    className={classes.chevronButton}
                    aria-expanded={expanded}
                    aria-label={expanded ? 'Collapse' : 'Expand'}
                >
                    {expanded ? <ExpandMoreIcon /> : <ChevronRightIcon />}
                </IconButton>
            )}
            <span
                className={
                    isParentRow
                        ? classes.resultRowLabelParent
                        : classes.resultRowLabel
                }
            >
                <HighlightedLabel
                    label={node.displayLabel}
                    highlightQuery={highlightQuery}
                    classes={classes}
                />
            </span>
            {count != null && (
                <span className={classes.resultRowCount}>
                    {count.toLocaleString()}
                </span>
            )}
        </div>
    );
}

TaxonomyResultRow.propTypes = {
    node: object.isRequired,
    depth: number.isRequired,
    isParent: bool.isRequired,
    highlightQuery: string.isRequired,
    selected: bool.isRequired,
    active: bool.isRequired,
    expanded: bool,
    count: oneOfType([number, object]),
    onToggleExpand: func,
    onSelect: func.isRequired,
    classes: object.isRequired,
};

TaxonomyResultRow.defaultProps = {
    expanded: false,
    count: null,
    onToggleExpand: null,
};

export default TaxonomyResultRow;
