import React, {
    useEffect,
    useImperativeHandle,
    useMemo,
    useRef,
    useState,
} from 'react';
import { arrayOf, bool, func, number, object, shape, string } from 'prop-types';
import InputLabel from '@material-ui/core/InputLabel';
import { withStyles } from '@material-ui/core/styles';

import TaxonomySearchControl from '../HierarchicalTaxonomySearch/TaxonomySearchControl';
import { makeSelectOption } from '../HierarchicalTaxonomySearch/utils';
import ProcessingTypeResultRow from './ProcessingTypeResultRow';
import styles from './styles';

const MIN_QUERY_LENGTH = 3;
const SUGGESTION_DEBOUNCE_MS = 250;
const LISTBOX_ID = 'processing-type-suggestions';
// This custom multi-select popup contains rich options that a native select
// cannot represent.
const LISTBOX_ROLE_PROPS = Object.freeze({ role: 'listbox' });
const caseIdentity = value => value.toLowerCase();

const GROUP_TITLES = Object.freeze({
    standard: 'OS Hub Taxonomy',
    contributor: 'Contributor values',
});

const reactSelectOptionPropType = shape({
    value: string.isRequired,
    label: string.isRequired,
    isExact: bool,
});

const suggestionPropType = shape({
    value: string.isRequired,
    label: string,
    count: number,
    in_taxonomy: bool,
    facility_types: arrayOf(string),
    dim: bool,
});

/*
Split the suggestions into the taxonomy and contributor groups, keeping the
order the backend ranked them in and numbering every row across both groups
so that keyboard navigation can walk them as one list.
*/
export function groupSuggestions(suggestions) {
    const standard = [];
    const contributor = [];

    suggestions.forEach(suggestion => {
        if (suggestion.in_taxonomy) {
            standard.push(suggestion);
        } else {
            contributor.push(suggestion);
        }
    });

    let nextIndex = 0;
    const makeGroup = (id, groupSuggestionList) => ({
        id,
        title: GROUP_TITLES[id],
        rows: groupSuggestionList.map(suggestion => {
            const row = { suggestion, index: nextIndex };
            nextIndex += 1;
            return row;
        }),
    });

    return [
        makeGroup('standard', standard),
        makeGroup('contributor', contributor),
    ].filter(group => group.rows.length > 0);
}

function ProcessingTypeSearch({
    label,
    placeholder,
    processingType,
    onProcessingTypeChange,
    facilityType,
    suggestions,
    onFetchSuggestions,
    disabled,
    classes,
    processingTypeSearchRef,
}) {
    const [query, setQuery] = useState('');
    const [activeRowIndex, setActiveRowIndex] = useState(-1);
    const [isFocused, setIsFocused] = useState(false);
    const inputRef = useRef(null);
    const lastRequestRef = useRef(null);

    const { data: suggestionData, fetching, error, query: fetchedQuery } =
        suggestions ?? {};

    const trimmedQuery = query.trim();
    const isQueryTooShort =
        trimmedQuery.length > 0 && trimmedQuery.length < MIN_QUERY_LENGTH;
    const validationMessage = isQueryTooShort
        ? `Enter at least ${MIN_QUERY_LENGTH} characters to search processing types`
        : '';
    const showResultsPanel = isFocused || trimmedQuery.length > 0;

    const facilityTypeValues = useMemo(
        () => facilityType.map(option => option.value),
        [facilityType],
    );
    const facilityTypeKey = facilityTypeValues.join('|');

    useEffect(() => {
        if (!onFetchSuggestions || !showResultsPanel || isQueryTooShort) {
            return undefined;
        }

        const requestKey = `${trimmedQuery}::${facilityTypeKey}`;
        if (lastRequestRef.current === requestKey) {
            return undefined;
        }

        const timeoutId = setTimeout(() => {
            lastRequestRef.current = requestKey;
            onFetchSuggestions(trimmedQuery, facilityTypeValues);
        }, SUGGESTION_DEBOUNCE_MS);

        return () => clearTimeout(timeoutId);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [showResultsPanel, isQueryTooShort, trimmedQuery, facilityTypeKey]);

    const groups = useMemo(() => groupSuggestions(suggestionData ?? []), [
        suggestionData,
    ]);
    const rows = useMemo(() => groups.flatMap(group => group.rows), [groups]);

    useEffect(() => {
        setActiveRowIndex(-1);
    }, [suggestionData]);

    const selectedIdentities = useMemo(
        () => new Set(processingType.map(option => caseIdentity(option.value))),
        [processingType],
    );

    const selectedChips = useMemo(
        () =>
            processingType.map(option => ({
                id: option.value,
                label: option.label,
            })),
        [processingType],
    );

    const clearQuery = () => {
        setQuery('');
        setActiveRowIndex(-1);
    };

    const handleToggleSuggestion = suggestion => {
        const { value } = suggestion;
        const identity = caseIdentity(value);
        if (selectedIdentities.has(identity)) {
            onProcessingTypeChange(
                processingType.filter(
                    option => caseIdentity(option.value) !== identity,
                ),
            );
        } else {
            onProcessingTypeChange([
                ...processingType,
                {
                    ...makeSelectOption(value),
                    label: suggestion.label ?? value,
                    isExact: true,
                },
            ]);
        }

        clearQuery();
    };

    const handleRemoveChip = chipId => {
        const identity = caseIdentity(chipId);
        onProcessingTypeChange(
            processingType.filter(
                option => caseIdentity(option.value) !== identity,
            ),
        );
    };

    const commitPendingQuery = () => {
        if (!trimmedQuery) {
            return true;
        }

        if (isQueryTooShort) {
            inputRef.current?.focus();
            return false;
        }

        if (!selectedIdentities.has(caseIdentity(trimmedQuery))) {
            onProcessingTypeChange([
                ...processingType,
                makeSelectOption(trimmedQuery),
            ]);
        }

        clearQuery();
        return true;
    };

    useImperativeHandle(processingTypeSearchRef, () => ({
        commitPendingQuery,
    }));

    const handleInputKeyDown = event => {
        if (event.key === 'Enter') {
            if (
                showResultsPanel &&
                activeRowIndex >= 0 &&
                rows[activeRowIndex]
            ) {
                event.preventDefault();
                handleToggleSuggestion(rows[activeRowIndex].suggestion);
                return;
            }

            // An Enter with nothing pending is left to the search form.
            if (trimmedQuery) {
                event.preventDefault();
                commitPendingQuery();
                return;
            }
        }

        if (event.key === 'Escape') {
            clearQuery();
            inputRef.current?.blur();
            return;
        }

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
        }
    };

    const highlightQuery =
        fetchedQuery == null ? trimmedQuery : fetchedQuery.trim();

    const renderStatusRow = () => {
        if (fetching) {
            return (
                <div className={classes.statusRow}>
                    <output>Loading processing types&hellip;</output>
                </div>
            );
        }

        if (error) {
            return (
                <div className={classes.statusRow}>
                    <span role="alert">
                        Unable to load processing type suggestions. Try again in
                        a moment.
                    </span>
                </div>
            );
        }

        return (
            <div className={classes.statusRow}>
                No matching processing types
                {trimmedQuery ? (
                    <>
                        <br />
                        Press Search to match &ldquo;{trimmedQuery}&rdquo; as
                        free text
                    </>
                ) : null}
            </div>
        );
    };

    const hint = facilityTypeValues.length
        ? 'Facility Type ranks these suggestions. Dimmed values belong to other facility types and can still be selected.'
        : 'Search the standard taxonomy and values contributed by data partners. Counts show how many locations carry each value.';

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
                inputId="processing-type-search"
                inputRef={inputRef}
                query={query}
                onQueryChange={value => {
                    setQuery(value);
                    setActiveRowIndex(-1);
                }}
                placeholder={placeholder}
                disabled={disabled}
                isFocused={isFocused}
                onFocus={() => setIsFocused(true)}
                onBlur={() => setIsFocused(false)}
                onKeyDown={handleInputKeyDown}
                selectedChips={selectedChips}
                onRemoveChip={handleRemoveChip}
                classes={classes}
                listboxId={LISTBOX_ID}
                showResultsPanel={showResultsPanel}
                activeRowIndex={activeRowIndex}
                validationMessage={validationMessage}
            />
            {validationMessage ? (
                <p className={classes.validationMessage} role="alert">
                    {validationMessage}
                </p>
            ) : null}

            {showResultsPanel && (
                <div
                    id={LISTBOX_ID}
                    {...LISTBOX_ROLE_PROPS}
                    className={classes.resultsPanel}
                    aria-label={label}
                    aria-busy={!!fetching}
                >
                    {rows.length === 0
                        ? renderStatusRow()
                        : groups.map(group => (
                              <React.Fragment key={group.id}>
                                  <div
                                      className={classes.groupHeader}
                                      aria-hidden="true"
                                  >
                                      <span
                                          className={classes.groupHeaderLabel}
                                      >
                                          {group.title}
                                      </span>
                                  </div>
                                  {group.rows.map(({ suggestion, index }) => (
                                      <ProcessingTypeResultRow
                                          key={suggestion.value}
                                          id={`${LISTBOX_ID}-option-${index}`}
                                          value={suggestion.value}
                                          label={
                                              suggestion.label ??
                                              suggestion.value
                                          }
                                          count={suggestion.count}
                                          facilityTypes={
                                              suggestion.facility_types ?? []
                                          }
                                          inTaxonomy={!!suggestion.in_taxonomy}
                                          dim={!!suggestion.dim}
                                          highlightQuery={highlightQuery}
                                          selected={selectedIdentities.has(
                                              caseIdentity(suggestion.value),
                                          )}
                                          active={index === activeRowIndex}
                                          onSelect={() =>
                                              handleToggleSuggestion(suggestion)
                                          }
                                          onMouseEnter={() =>
                                              setActiveRowIndex(index)
                                          }
                                          classes={classes}
                                      />
                                  ))}
                              </React.Fragment>
                          ))}
                </div>
            )}

            <p className={classes.hint}>{hint}</p>
        </div>
    );
}

ProcessingTypeSearch.defaultProps = {
    label: 'Processing Type',
    placeholder: 'Search processing types',
    processingType: [],
    facilityType: [],
    suggestions: Object.freeze({
        query: null,
        data: null,
        fetching: false,
        error: null,
    }),
    onFetchSuggestions: null,
    disabled: false,
    processingTypeSearchRef: null,
};

ProcessingTypeSearch.propTypes = {
    label: string,
    placeholder: string,
    processingType: arrayOf(reactSelectOptionPropType),
    onProcessingTypeChange: func.isRequired,
    facilityType: arrayOf(reactSelectOptionPropType),
    suggestions: shape({
        query: string,
        data: arrayOf(suggestionPropType),
        fetching: bool,
        error: arrayOf(string),
    }),
    onFetchSuggestions: func,
    disabled: bool,
    processingTypeSearchRef: object,
};

export default withStyles(styles)(ProcessingTypeSearch);
