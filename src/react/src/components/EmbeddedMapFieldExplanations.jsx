import React, { useEffect, useState } from 'react';
import { bool, func, object, string } from 'prop-types';

import apiRequest from '../util/apiRequest';
import { makeEmbedFieldValuesURL } from '../util/util';
import {
    DISPLAY_AS_BLURB,
    MAX_EXPLANATION_LENGTH,
    cleanValueDescriptions,
} from '../util/embeddedMap';

const VALUES_SHOWN_AT_FIRST = 12;

const styles = {
    toggle: {
        marginTop: '6px',
        padding: '4px 10px',
        border: '1px solid rgb(13, 17, 40)',
        background: 'white',
        fontFamily: 'inherit',
        fontSize: '13px',
        fontWeight: 700,
        cursor: 'pointer',
    },
    panel: {
        marginTop: '8px',
        padding: '10px 12px 12px',
        background: 'white',
        border: '1px solid rgb(214, 216, 221)',
    },
    label: {
        display: 'block',
        margin: '8px 0 4px',
        fontSize: '13px',
        fontWeight: 700,
    },
    input: {
        width: '100%',
        padding: '6px 8px',
        fontSize: '14px',
        fontFamily: 'inherit',
        boxSizing: 'border-box',
    },
    hint: {
        fontSize: '13px',
        color: 'rgba(0, 0, 0, 0.6)',
    },
    count: {
        fontWeight: 400,
        color: 'rgba(0, 0, 0, 0.6)',
    },
    more: {
        marginTop: '8px',
        padding: 0,
        border: 0,
        background: 'none',
        fontFamily: 'inherit',
        fontSize: '13px',
        textDecoration: 'underline',
        cursor: 'pointer',
    },
};

/*
Lets a contributor explain one of the fields on their embedded map: what the
field means, and what each of its values means (what an initiative named in
an "initiatives" column is, for example). Both are optional, and are shown
with the field on a location's page.
*/
function EmbeddedMapFieldExplanations({
    columnName,
    displayAs,
    description,
    valueDescriptions,
    onChange,
    disabled,
}) {
    const [open, setOpen] = useState(false);
    const [values, setValues] = useState(null);
    const [showAll, setShowAll] = useState(false);
    // A blurb is free text written for each location, not a set of values.
    const hasValuesToExplain = displayAs !== DISPLAY_AS_BLURB;

    useEffect(() => {
        if (!open || !hasValuesToExplain || values) return;
        apiRequest
            .get(makeEmbedFieldValuesURL(columnName))
            .then(({ data }) => setValues(data))
            .catch(() => setValues([]));
    }, [open, hasValuesToExplain, values, columnName]);

    const written =
        (description.trim() ? 1 : 0) +
        Object.keys(cleanValueDescriptions(valueDescriptions)).length;
    const shownValues = showAll
        ? values || []
        : (values || []).slice(0, VALUES_SHOWN_AT_FIRST);

    return (
        <div>
            <button
                type="button"
                style={styles.toggle}
                aria-expanded={open}
                disabled={disabled}
                onClick={() => setOpen(isOpen => !isOpen)}
            >
                {open ? 'Hide explanations' : 'Add explanations'}
                {written ? ` (${written})` : ''}
            </button>
            {open ? (
                <div style={styles.panel}>
                    <div style={styles.hint}>
                        Optional. Shown with this field on a location&apos;s
                        page on your map.
                    </div>
                    <label
                        style={styles.label}
                        htmlFor={`explain-${columnName}`}
                    >
                        What this field means
                    </label>
                    <input
                        id={`explain-${columnName}`}
                        style={styles.input}
                        maxLength={MAX_EXPLANATION_LENGTH}
                        placeholder="e.g. Programs this facility takes part in"
                        value={description}
                        onChange={event =>
                            onChange({ description: event.target.value })
                        }
                    />
                    {hasValuesToExplain ? (
                        <>
                            <div style={styles.label}>
                                What each value means
                            </div>
                            {values === null ? (
                                <div style={styles.hint}>Loading values…</div>
                            ) : null}
                            {values && !values.length ? (
                                <div style={styles.hint}>
                                    Your data has no values in this field yet.
                                </div>
                            ) : null}
                            {shownValues.map(({ value, count }) => (
                                <div key={value}>
                                    <label
                                        style={styles.label}
                                        htmlFor={`explain-${columnName}-${value}`}
                                    >
                                        {value}{' '}
                                        <span style={styles.count}>
                                            ({count}{' '}
                                            {count === 1
                                                ? 'location'
                                                : 'locations'}
                                            )
                                        </span>
                                    </label>
                                    <input
                                        id={`explain-${columnName}-${value}`}
                                        style={styles.input}
                                        maxLength={MAX_EXPLANATION_LENGTH}
                                        value={valueDescriptions[value] || ''}
                                        onChange={event =>
                                            onChange({
                                                valueDescriptions: {
                                                    ...valueDescriptions,
                                                    [value]: event.target.value,
                                                },
                                            })
                                        }
                                    />
                                </div>
                            ))}
                            {values &&
                            values.length > VALUES_SHOWN_AT_FIRST &&
                            !showAll ? (
                                <button
                                    type="button"
                                    style={styles.more}
                                    onClick={() => setShowAll(true)}
                                >
                                    Show all {values.length} values
                                </button>
                            ) : null}
                        </>
                    ) : null}
                </div>
            ) : null}
        </div>
    );
}

EmbeddedMapFieldExplanations.defaultProps = {
    displayAs: 'text',
    description: '',
    valueDescriptions: {},
    disabled: false,
};

EmbeddedMapFieldExplanations.propTypes = {
    columnName: string.isRequired,
    displayAs: string,
    description: string,
    valueDescriptions: object,
    onChange: func.isRequired,
    disabled: bool,
};

export default EmbeddedMapFieldExplanations;
