import React from 'react';
import { bool, func, number, object, shape, string } from 'prop-types';

import { splitLabelForHighlight } from '../HierarchicalTaxonomySearch/utils';
import { LEVEL_LABELS, REVISION_LABELS, revisionsOf } from './utils';

// Rows are controlled by the combobox through aria-activedescendant.
const OPTION_ROLE_PROPS = Object.freeze({ role: 'option' });

function IsicResultRow({
    id,
    entry,
    count,
    highlightQuery,
    active,
    onSelect,
    onMouseEnter,
    classes,
}) {
    let offset = 0;

    return (
        // Keyboard focus and selection are handled by the controlling
        // combobox through aria-activedescendant.
        // eslint-disable-next-line jsx-a11y/click-events-have-key-events, jsx-a11y/interactive-supports-focus, jsx-a11y/no-static-element-interactions
        <div
            id={id}
            {...OPTION_ROLE_PROPS}
            aria-selected={false}
            className={`${classes.resultRow} ${
                active ? classes.resultRowSelected : ''
            }`}
            onMouseDown={event => event.preventDefault()}
            onClick={onSelect}
            onMouseEnter={onMouseEnter}
        >
            <span className={classes.resultRowBody}>
                <span className={classes.resultRowTerm}>
                    {splitLabelForHighlight(entry.title, highlightQuery).map(
                        part => {
                            const key = `${offset}-${part.text}`;
                            offset += part.text.length;
                            return (
                                <span
                                    key={key}
                                    className={
                                        part.highlighted
                                            ? classes.highlight
                                            : undefined
                                    }
                                >
                                    {part.text}
                                </span>
                            );
                        },
                    )}
                    {revisionsOf(entry).map(revision => (
                        <span key={revision} className={classes.revisionTag}>
                            {REVISION_LABELS[revision]}
                        </span>
                    ))}
                </span>
                <span className={classes.resultRowMeta}>
                    <span className={classes.resultRowBreadcrumb}>
                        {LEVEL_LABELS[entry.level]}
                        {entry.trail ? ` · in ${entry.trail}` : ''}
                    </span>
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

IsicResultRow.defaultProps = {
    count: null,
    highlightQuery: '',
    onMouseEnter: null,
};

IsicResultRow.propTypes = {
    id: string.isRequired,
    entry: shape({
        id: string.isRequired,
        title: string.isRequired,
        level: string.isRequired,
        codes: object.isRequired,
        trail: string,
    }).isRequired,
    count: number,
    highlightQuery: string,
    active: bool.isRequired,
    onSelect: func.isRequired,
    onMouseEnter: func,
    classes: object.isRequired,
};

export default IsicResultRow;
