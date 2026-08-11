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
    id,
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
    onMouseEnter,
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

    const handleSelectClick = () => {
        onSelect();
    };

    const rowClassName = `${
        isParentRow ? classes.resultRowParent : classes.resultRowChild
    } ${selected || active ? classes.resultRowSelected : ''}`;

    return (
        <li
            id={id}
            className={classes.resultRowItem}
            onMouseEnter={onMouseEnter}
        >
            <div
                className={rowClassName}
                style={{ paddingLeft: `${paddingLeft}px` }}
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
                <button
                    type="button"
                    className={
                        isParentRow
                            ? classes.resultRowLabelParent
                            : classes.resultRowLabel
                    }
                    aria-pressed={selected}
                    onMouseDown={event => event.preventDefault()}
                    onClick={handleSelectClick}
                >
                    <HighlightedLabel
                        label={node.displayLabel}
                        highlightQuery={highlightQuery}
                        classes={classes}
                    />
                </button>
                {count != null && (
                    <span className={classes.resultRowCount}>
                        {count.toLocaleString()}
                    </span>
                )}
            </div>
        </li>
    );
}

TaxonomyResultRow.propTypes = {
    id: string,
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
    onMouseEnter: func,
    classes: object.isRequired,
};

TaxonomyResultRow.defaultProps = {
    id: undefined,
    expanded: false,
    count: null,
    onToggleExpand: null,
    onMouseEnter: null,
};

export default TaxonomyResultRow;
