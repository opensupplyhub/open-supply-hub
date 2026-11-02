import React, { useMemo, useRef, useState } from 'react';
import { arrayOf, bool, func, object, shape, string } from 'prop-types';
import { connect } from 'react-redux';
import Button from '@material-ui/core/Button';
import { withStyles } from '@material-ui/core/styles';

import TaxonomySearchControl from '../HierarchicalTaxonomySearch/TaxonomySearchControl';
import IsicResultRow from './IsicResultRow';
import { fetchIsicTaxonomyIfNeeded } from '../../../actions/filterOptions';
import {
    REVISION_LABELS,
    filterValue,
    findByCode,
    searchEntries,
} from './utils';
import styles from './styles';

const LISTBOX_ID = 'isic-value-suggestions';
const LISTBOX_ROLE_PROPS = Object.freeze({ role: 'listbox' });

/*
ISIC values for one location, as the claim and single-location forms take
them (OSDEV-2974): the contributor picks ISIC 4 or ISIC 5, then a category
by title or code within it. The value is { 4: [option], 5: [option] }, each
option { value: 'level:code', label: title }, as the search filters use.
*/
export function IsicValuePicker({
    entries,
    value,
    disabled,
    onLoad,
    onChange,
    classes,
}) {
    const [revision, setRevision] = useState('4');
    const [query, setQuery] = useState('');
    const [activeRowIndex, setActiveRowIndex] = useState(-1);
    const [isFocused, setIsFocused] = useState(false);
    const inputRef = useRef(null);

    const revisionEntries = useMemo(
        () => entries.filter(entry => entry.codes[revision]),
        [entries, revision],
    );
    const rows = useMemo(() => {
        const byCode = findByCode(revisionEntries, revision, query);
        const byTitle = searchEntries(revisionEntries, query, new Set());
        return byCode
            ? [byCode, ...byTitle.filter(entry => entry !== byCode)]
            : byTitle;
    }, [revisionEntries, revision, query]);

    const pick = entry => {
        const option = {
            value: filterValue(entry, revision),
            label: entry.title,
        };
        const current = value[revision] || [];
        if (!current.some(item => item.value === option.value)) {
            onChange({ ...value, [revision]: [...current, option] });
        }
        setQuery('');
        setActiveRowIndex(-1);
    };

    const remove = chipId => {
        const [chipRevision, chipValue] = chipId.split('|');
        onChange({
            ...value,
            [chipRevision]: (value[chipRevision] || []).filter(
                item => item.value !== chipValue,
            ),
        });
    };

    const handleKeyDown = event => {
        if (event.key === 'Enter' && rows[activeRowIndex]) {
            event.preventDefault();
            pick(rows[activeRowIndex]);
        } else if (event.key === 'ArrowDown' && rows.length) {
            event.preventDefault();
            setActiveRowIndex(current => (current + 1) % rows.length);
        } else if (event.key === 'ArrowUp' && rows.length) {
            event.preventDefault();
            setActiveRowIndex(current =>
                current <= 0 ? rows.length - 1 : current - 1,
            );
        }
    };

    const chips = ['4', '5'].flatMap(chipRevision =>
        (value[chipRevision] || []).map(item => ({
            id: `${chipRevision}|${item.value}`,
            label: `${REVISION_LABELS[chipRevision]} · ${
                item.value.split(':')[1]
            } · ${item.label}`,
        })),
    );
    const showResultsPanel = isFocused && query.trim().length > 0;

    return (
        <div className={classes.root}>
            <div role="group" aria-label="ISIC revision">
                {['4', '5'].map(option => (
                    <Button
                        key={option}
                        size="small"
                        variant={option === revision ? 'contained' : 'text'}
                        color={option === revision ? 'primary' : 'default'}
                        onClick={() => setRevision(option)}
                        disabled={disabled}
                        aria-pressed={option === revision}
                    >
                        {REVISION_LABELS[option]}
                    </Button>
                ))}
            </div>
            <TaxonomySearchControl
                inputId="isic-value-picker"
                inputRef={inputRef}
                query={query}
                onQueryChange={text => {
                    setQuery(text);
                    setActiveRowIndex(-1);
                }}
                placeholder={`Type an ${REVISION_LABELS[revision]} title or code`}
                disabled={disabled}
                isFocused={isFocused}
                onFocus={() => {
                    setIsFocused(true);
                    onLoad();
                }}
                onBlur={() => setIsFocused(false)}
                onKeyDown={handleKeyDown}
                selectedChips={chips}
                onRemoveChip={remove}
                classes={classes}
                listboxId={LISTBOX_ID}
                showResultsPanel={showResultsPanel}
                activeRowIndex={activeRowIndex}
            />
            {showResultsPanel && (
                <div
                    id={LISTBOX_ID}
                    {...LISTBOX_ROLE_PROPS}
                    className={classes.resultsPanel}
                    aria-label={`${REVISION_LABELS[revision]} categories`}
                >
                    {rows.length === 0 ? (
                        <div className={classes.statusRow}>
                            No {REVISION_LABELS[revision]} category matches. Try
                            a shorter word or another code.
                        </div>
                    ) : (
                        rows.map((entry, index) => (
                            <IsicResultRow
                                key={entry.id}
                                id={`${LISTBOX_ID}-option-${index}`}
                                entry={{
                                    ...entry,
                                    codes: {
                                        [revision]: entry.codes[revision],
                                    },
                                }}
                                highlightQuery={query.trim()}
                                active={index === activeRowIndex}
                                onSelect={() => pick(entry)}
                                onMouseEnter={() => setActiveRowIndex(index)}
                                classes={classes}
                            />
                        ))
                    )}
                </div>
            )}
        </div>
    );
}

const optionsPropType = arrayOf(shape({ value: string, label: string }));

IsicValuePicker.defaultProps = {
    disabled: false,
};

IsicValuePicker.propTypes = {
    entries: arrayOf(object).isRequired,
    value: shape({ 4: optionsPropType, 5: optionsPropType }).isRequired,
    disabled: bool,
    onLoad: func.isRequired,
    onChange: func.isRequired,
    classes: object.isRequired,
};

const mapStateToProps = ({ filterOptions: { isicTaxonomy } }) => ({
    entries: isicTaxonomy.data ?? [],
});

const mapDispatchToProps = dispatch => ({
    onLoad: () => dispatch(fetchIsicTaxonomyIfNeeded()),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(styles)(IsicValuePicker));
