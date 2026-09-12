import React from 'react';
import { arrayOf, bool, func, number, object, shape, string } from 'prop-types';

import FilterMultiValueChip from '../FilterMultiValueChip';
import SearchIcon from '../../SearchIcon';

const chipPropType = shape({
    id: string.isRequired,
    label: string.isRequired,
});

function TaxonomySearchControl({
    inputId,
    inputRef,
    query,
    onQueryChange,
    placeholder,
    disabled,
    isFocused,
    onFocus,
    onBlur,
    onKeyDown,
    selectedChips,
    onRemoveChip,
    classes,
    listboxId,
    showResultsPanel,
    activeRowIndex,
    validationMessage,
}) {
    const showPlaceholder = selectedChips.length === 0 && !query;
    const activeDescendantId =
        showResultsPanel && activeRowIndex >= 0
            ? `${listboxId}-option-${activeRowIndex}`
            : undefined;

    const handleInputKeyDown = event => {
        if (event.key === 'Backspace' && !query && selectedChips.length > 0) {
            event.preventDefault();
            onRemoveChip(selectedChips[selectedChips.length - 1].id);
            return;
        }

        onKeyDown(event);
    };

    return (
        <label
            htmlFor={inputId}
            className={`${classes.searchControl} ${
                isFocused ? classes.searchControlFocused : ''
            }`}
        >
            <span className={classes.searchIcon} aria-hidden="true">
                <SearchIcon />
            </span>
            <div className={classes.searchValueContainer}>
                {selectedChips.map(chip => (
                    <FilterMultiValueChip
                        key={chip.id}
                        label={chip.label}
                        onRemove={() => onRemoveChip(chip.id)}
                        classes={classes}
                    />
                ))}
                <input
                    ref={inputRef}
                    id={inputId}
                    type="text"
                    className={classes.searchInput}
                    value={query}
                    placeholder={showPlaceholder ? placeholder : ''}
                    disabled={disabled}
                    aria-controls={showResultsPanel ? listboxId : undefined}
                    aria-autocomplete="list"
                    aria-expanded={showResultsPanel}
                    aria-activedescendant={activeDescendantId}
                    aria-invalid={!!validationMessage}
                    role="combobox"
                    onFocus={onFocus}
                    onBlur={onBlur}
                    onChange={event => onQueryChange(event.target.value)}
                    onKeyDown={handleInputKeyDown}
                />
            </div>
        </label>
    );
}

TaxonomySearchControl.propTypes = {
    inputId: string.isRequired,
    inputRef: object.isRequired,
    query: string.isRequired,
    onQueryChange: func.isRequired,
    placeholder: string.isRequired,
    disabled: bool,
    isFocused: bool.isRequired,
    onFocus: func.isRequired,
    onBlur: func.isRequired,
    onKeyDown: func.isRequired,
    selectedChips: arrayOf(chipPropType).isRequired,
    onRemoveChip: func.isRequired,
    classes: object.isRequired,
    listboxId: string.isRequired,
    showResultsPanel: bool.isRequired,
    activeRowIndex: number.isRequired,
    validationMessage: string,
};

TaxonomySearchControl.defaultProps = {
    disabled: false,
    validationMessage: '',
};

export default TaxonomySearchControl;
