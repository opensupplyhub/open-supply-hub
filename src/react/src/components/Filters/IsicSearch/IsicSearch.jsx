import React, { useMemo, useRef, useState } from 'react';
import { arrayOf, bool, func, object, shape, string } from 'prop-types';
import { connect } from 'react-redux';
import InputLabel from '@material-ui/core/InputLabel';
import { withStyles } from '@material-ui/core/styles';

import TaxonomySearchControl from '../HierarchicalTaxonomySearch/TaxonomySearchControl';
import IsicResultRow from './IsicResultRow';
import {
    fetchIsicTaxonomyIfNeeded,
    fetchTaxonomyCountsIfNeeded,
} from '../../../actions/filterOptions';
import { updateIsic4Filter, updateIsic5Filter } from '../../../actions/filters';
import { isEmpty, searchEntries, selectedEntries, withEntry } from './utils';
import styles from './styles';

const LABEL = 'Industry Classification';
const LISTBOX_ID = 'isic-suggestions';
const LISTBOX_ROLE_PROPS = Object.freeze({ role: 'listbox' });

/*
Industry Classification (OSDEV-3340): one field over the titles of every
ISIC revision OS Hub holds. A category picked here filters on its code in
each revision it exists in; the API adds values uploaded under the other
revision through the UN correspondence. Codes are never shown. Once the
counts load, categories without locations are grayed out, listed last and
can't be picked; until then every category can be.
*/
export function IsicSearch({
    entries,
    fetching,
    counts,
    isic4,
    isic5,
    disabled,
    onLoad,
    onChange,
    classes,
}) {
    const [query, setQuery] = useState('');
    const [activeRowIndex, setActiveRowIndex] = useState(-1);
    const [isFocused, setIsFocused] = useState(false);
    const inputRef = useRef(null);

    const selections = useMemo(() => ({ 4: isic4, 5: isic5 }), [isic4, isic5]);
    const selected = useMemo(() => selectedEntries(entries, selections), [
        entries,
        selections,
    ]);
    const rows = useMemo(
        () =>
            searchEntries(
                entries,
                query,
                new Set(selected.map(entry => entry.id)),
                counts,
            ),
        [entries, query, selected, counts],
    );

    const trimmedQuery = query.trim();
    const showResultsPanel = isFocused && trimmedQuery.length > 0;

    const pick = entry => {
        if (isEmpty(entry, counts)) return;
        onChange(withEntry(selections, entry, true));
        setQuery('');
        setActiveRowIndex(-1);
    };

    const handleKeyDown = event => {
        if (event.key === 'Enter' && rows[activeRowIndex]) {
            event.preventDefault();
            pick(rows[activeRowIndex]);
        } else if (event.key === 'Escape') {
            setQuery('');
            inputRef.current?.blur();
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

    const renderStatusRow = () => (
        <div className={classes.statusRow}>
            {fetching ? (
                <output>Loading industry categories&hellip;</output>
            ) : (
                <>
                    No ISIC category matches {'\u201D'}
                    {trimmedQuery}
                    {'\u201C'}. Try a shorter or more general word.
                </>
            )}
        </div>
    );

    return (
        <div className={classes.root}>
            <InputLabel
                shrink={false}
                component="div"
                className={classes.inputLabelStyle}
            >
                {LABEL}
            </InputLabel>
            <TaxonomySearchControl
                inputId="isic-search"
                inputRef={inputRef}
                query={query}
                onQueryChange={value => {
                    setQuery(value);
                    setActiveRowIndex(-1);
                }}
                placeholder="Search industry categories"
                disabled={disabled}
                isFocused={isFocused}
                onFocus={() => {
                    setIsFocused(true);
                    onLoad();
                }}
                onBlur={() => setIsFocused(false)}
                onKeyDown={handleKeyDown}
                selectedChips={selected.map(entry => ({
                    id: entry.id,
                    label: entry.title,
                }))}
                onRemoveChip={id =>
                    onChange(
                        withEntry(
                            selections,
                            selected.find(entry => entry.id === id),
                            false,
                        ),
                    )
                }
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
                    aria-label={LABEL}
                    aria-busy={fetching}
                >
                    {rows.length === 0
                        ? renderStatusRow()
                        : rows.map((entry, index) => (
                              <IsicResultRow
                                  key={entry.id}
                                  id={`${LISTBOX_ID}-option-${index}`}
                                  entry={entry}
                                  count={counts ? counts[entry.id] ?? 0 : null}
                                  empty={isEmpty(entry, counts)}
                                  highlightQuery={trimmedQuery}
                                  active={index === activeRowIndex}
                                  onSelect={() => pick(entry)}
                                  onMouseEnter={() => setActiveRowIndex(index)}
                                  classes={classes}
                              />
                          ))}
                    {rows.length > 0 && (
                        <div className={classes.hint}>
                            Tags show which ISIC revisions a category belongs
                            to. Counts include everything within the category;
                            categories with no locations are grayed out.
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

const optionsPropType = arrayOf(shape({ value: string, label: string }));

IsicSearch.defaultProps = {
    counts: null,
    disabled: false,
};

IsicSearch.propTypes = {
    entries: arrayOf(object).isRequired,
    fetching: bool.isRequired,
    counts: object,
    isic4: optionsPropType.isRequired,
    isic5: optionsPropType.isRequired,
    disabled: bool,
    onLoad: func.isRequired,
    onChange: func.isRequired,
    classes: object.isRequired,
};

const mapStateToProps = ({
    filterOptions: { isicTaxonomy, taxonomyCounts },
    filters: { isic4, isic5 },
}) => ({
    entries: isicTaxonomy.data ?? [],
    fetching: isicTaxonomy.fetching,
    counts: taxonomyCounts.isic.data,
    isic4,
    isic5,
});

const mapDispatchToProps = dispatch => ({
    onLoad: () => {
        dispatch(fetchIsicTaxonomyIfNeeded());
        dispatch(fetchTaxonomyCountsIfNeeded());
    },
    onChange: ({ 4: isic4, 5: isic5 }) => {
        dispatch(updateIsic4Filter(isic4));
        dispatch(updateIsic5Filter(isic5));
    },
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(styles)(IsicSearch));
