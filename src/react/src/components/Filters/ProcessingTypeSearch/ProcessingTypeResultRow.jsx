import React from 'react';
import { arrayOf, bool, func, number, object, string } from 'prop-types';

import { splitLabelForHighlight } from '../HierarchicalTaxonomySearch/utils';

const BREADCRUMB_SEPARATOR = ' \u00b7 ';
// These rich options are controlled by the combobox through
// aria-activedescendant and cannot be represented by native option elements.
const OPTION_ROLE_PROPS = Object.freeze({ role: 'option' });

function HighlightedTerm({ value, highlightQuery, classes }) {
    const parts = splitLabelForHighlight(value, highlightQuery);
    let textOffset = 0;

    return (
        <span className={classes.resultRowTerm}>
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

function ProcessingTypeResultRow({
    id,
    label,
    count,
    facilityTypes,
    inTaxonomy,
    dim,
    highlightQuery,
    selected,
    active,
    onSelect,
    onMouseEnter,
    classes,
}) {
    const rowClassName = [
        classes.resultRow,
        selected || active ? classes.resultRowSelected : '',
        dim ? classes.resultRowDim : '',
    ]
        .filter(Boolean)
        .join(' ');

    return (
        // Keyboard focus and selection are handled by the controlling
        // combobox through aria-activedescendant.
        // eslint-disable-next-line jsx-a11y/click-events-have-key-events, jsx-a11y/interactive-supports-focus, jsx-a11y/no-static-element-interactions
        <div
            id={id}
            {...OPTION_ROLE_PROPS}
            aria-selected={selected}
            className={rowClassName}
            onMouseDown={event => event.preventDefault()}
            onClick={onSelect}
            onMouseEnter={onMouseEnter}
        >
            <span className={classes.resultRowBody}>
                <HighlightedTerm
                    value={label}
                    highlightQuery={highlightQuery}
                    classes={classes}
                />
                <span className={classes.resultRowMeta}>
                    {facilityTypes.length > 0 ? (
                        <span className={classes.resultRowBreadcrumb}>
                            {facilityTypes.join(BREADCRUMB_SEPARATOR)}
                        </span>
                    ) : (
                        <span className={classes.notInTaxonomyBadge}>
                            {inTaxonomy
                                ? 'No facility type'
                                : 'Not in taxonomy'}
                        </span>
                    )}
                </span>
            </span>
            {count != null && (
                <span className={classes.resultRowCount}>
                    {count.toLocaleString()}
                </span>
            )}
        </div>
    );
}

ProcessingTypeResultRow.defaultProps = {
    id: undefined,
    count: null,
    facilityTypes: [],
    inTaxonomy: false,
    dim: false,
    highlightQuery: '',
    onMouseEnter: null,
};

ProcessingTypeResultRow.propTypes = {
    id: string,
    label: string.isRequired,
    count: number,
    facilityTypes: arrayOf(string),
    inTaxonomy: bool,
    dim: bool,
    highlightQuery: string,
    selected: bool.isRequired,
    active: bool.isRequired,
    onSelect: func.isRequired,
    onMouseEnter: func,
    classes: object.isRequired,
};

export default ProcessingTypeResultRow;
