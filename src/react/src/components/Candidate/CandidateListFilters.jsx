import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import Checkbox from '@material-ui/core/Checkbox';
import Chip from '@material-ui/core/Chip';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import MenuItem from '@material-ui/core/MenuItem';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';

import {
    CANDIDATE_LIST_COPY,
    CANDIDATE_STATES,
    CANDIDATE_STATE_LABELS,
} from '../../util/candidateCopy';
import { DEFAULT_CANDIDATE_LIST_QUERY } from '../../util/candidates';
import { candidateListFiltersStyles } from './styles';

const STATE_ORDER = [
    CANDIDATE_STATES.UNVERIFIED,
    CANDIDATE_STATES.DISPUTED,
    CANDIDATE_STATES.CONFIRMED,
    CANDIDATE_STATES.RETIREMENT_PENDING,
];

const NEARBY_OPTIONS = [
    { value: 'any', label: CANDIDATE_LIST_COPY.filterNearbyAny },
    { value: 'true', label: CANDIDATE_LIST_COPY.filterNearbyYes },
    { value: 'false', label: CANDIDATE_LIST_COPY.filterNearbyNo },
];

const toPercentText = value =>
    typeof value === 'number' ? String(Math.round(value * 100)) : '';

const fromPercentText = text => {
    if (text === '' || text === null || text === undefined) return null;
    const number = Number(text);
    if (!Number.isFinite(number)) return null;
    return Math.min(100, Math.max(0, number)) / 100;
};

/**
 * Text inputs commit on blur or Enter rather than on every keystroke, so a
 * half-typed value is never sent as a filter.
 */
const CommittedTextField = ({ value, onCommit, ...props }) => {
    const [text, setText] = useState(value);
    useEffect(() => setText(value), [value]);
    const commit = () => {
        if (text !== value) onCommit(text);
    };
    return (
        <TextField
            {...props}
            value={text}
            onChange={event => setText(event.target.value)}
            onBlur={commit}
            onKeyDown={event => {
                if (event.key === 'Enter') {
                    event.preventDefault();
                    commit();
                }
            }}
        />
    );
};

CommittedTextField.propTypes = {
    value: PropTypes.string.isRequired,
    onCommit: PropTypes.func.isRequired,
};

/**
 * Filter rail of the candidate review page (OSDEV-3755). Every change is
 * reported through `onChange(partialQuery)`; the page owns the query and
 * resets the page number.
 */
const CandidateListFilters = ({ classes, query, onChange }) => {
    const toggleState = state => {
        const states = query.states.includes(state)
            ? query.states.filter(item => item !== state)
            : [...query.states, state];
        onChange({ states });
    };

    const nearbyValue =
        typeof query.hasNearby === 'boolean' ? String(query.hasNearby) : 'any';

    const isDefault =
        !query.states.length &&
        query.confidenceMin === null &&
        query.confidenceMax === null &&
        query.hasNearby === null &&
        !query.country &&
        !query.bbox;

    return (
        <aside
            className={classes.root}
            aria-label={CANDIDATE_LIST_COPY.filtersTitle}
            data-testid="candidate-list-filters"
        >
            <h2 className={classes.title}>
                {CANDIDATE_LIST_COPY.filtersTitle}
            </h2>

            <div className={classes.group} role="group">
                <Typography component="span" className={classes.groupLabel}>
                    {CANDIDATE_LIST_COPY.filterState}
                </Typography>
                {STATE_ORDER.map(state => (
                    <FormControlLabel
                        key={state}
                        className={classes.checkboxLabel}
                        classes={{ label: classes.checkboxLabelText }}
                        control={
                            <Checkbox
                                className={classes.checkbox}
                                color="primary"
                                checked={query.states.includes(state)}
                                onChange={() => toggleState(state)}
                                inputProps={{
                                    'data-testid': `candidate-filter-state-${state}`,
                                }}
                            />
                        }
                        label={CANDIDATE_STATE_LABELS[state]}
                    />
                ))}
            </div>

            <div className={classes.group}>
                <Typography component="span" className={classes.groupLabel}>
                    {CANDIDATE_LIST_COPY.filterConfidence}
                </Typography>
                <div className={classes.range}>
                    <CommittedTextField
                        className={classes.rangeField}
                        label={CANDIDATE_LIST_COPY.filterConfidenceMin}
                        type="number"
                        inputProps={{
                            min: 0,
                            max: 100,
                            'data-testid': 'candidate-filter-confidence-min',
                        }}
                        value={toPercentText(query.confidenceMin)}
                        onCommit={text =>
                            onChange({ confidenceMin: fromPercentText(text) })
                        }
                    />
                    <CommittedTextField
                        className={classes.rangeField}
                        label={CANDIDATE_LIST_COPY.filterConfidenceMax}
                        type="number"
                        inputProps={{
                            min: 0,
                            max: 100,
                            'data-testid': 'candidate-filter-confidence-max',
                        }}
                        value={toPercentText(query.confidenceMax)}
                        onCommit={text =>
                            onChange({ confidenceMax: fromPercentText(text) })
                        }
                    />
                </div>
            </div>

            <div className={classes.group}>
                <TextField
                    select
                    label={CANDIDATE_LIST_COPY.filterNearby}
                    value={nearbyValue}
                    onChange={event =>
                        onChange({
                            hasNearby:
                                event.target.value === 'any'
                                    ? null
                                    : event.target.value === 'true',
                        })
                    }
                    SelectProps={{
                        SelectDisplayProps: {
                            'data-testid': 'candidate-filter-nearby',
                        },
                    }}
                >
                    {NEARBY_OPTIONS.map(option => (
                        <MenuItem key={option.value} value={option.value}>
                            {option.label}
                        </MenuItem>
                    ))}
                </TextField>
            </div>

            <div className={classes.group}>
                <CommittedTextField
                    label={CANDIDATE_LIST_COPY.filterCountry}
                    helperText={CANDIDATE_LIST_COPY.filterCountryHint}
                    FormHelperTextProps={{ className: classes.helperText }}
                    inputProps={{ 'data-testid': 'candidate-filter-country' }}
                    value={query.country}
                    onCommit={text =>
                        onChange({
                            country: text
                                .split(',')
                                .map(part => part.trim().toUpperCase())
                                .filter(Boolean)
                                .join(','),
                        })
                    }
                />
            </div>

            <div className={classes.group}>
                <Typography component="span" className={classes.groupLabel}>
                    {CANDIDATE_LIST_COPY.filterArea}
                </Typography>
                {query.bbox ? (
                    <div className={classes.areaRow}>
                        <Chip
                            className={classes.chip}
                            label={CANDIDATE_LIST_COPY.filterAreaSet}
                            onDelete={() => onChange({ bbox: null })}
                            data-testid="candidate-filter-area-chip"
                        />
                    </div>
                ) : (
                    <Typography className={classes.hint}>
                        {CANDIDATE_LIST_COPY.filterAreaNone}
                    </Typography>
                )}
            </div>

            <Button
                size="small"
                variant="outlined"
                className={classes.resetButton}
                disabled={isDefault}
                onClick={() =>
                    onChange({
                        states: [],
                        confidenceMin: null,
                        confidenceMax: null,
                        hasNearby: null,
                        country: '',
                        bbox: null,
                    })
                }
                data-testid="candidate-filter-reset"
            >
                {CANDIDATE_LIST_COPY.resetFilters}
            </Button>
        </aside>
    );
};

CandidateListFilters.propTypes = {
    classes: PropTypes.object.isRequired,
    query: PropTypes.shape({
        states: PropTypes.arrayOf(PropTypes.string).isRequired,
        confidenceMin: PropTypes.number,
        confidenceMax: PropTypes.number,
        hasNearby: PropTypes.bool,
        country: PropTypes.string.isRequired,
        bbox: PropTypes.string,
    }),
    onChange: PropTypes.func.isRequired,
};

CandidateListFilters.defaultProps = {
    query: DEFAULT_CANDIDATE_LIST_QUERY,
};

export default withStyles(candidateListFiltersStyles)(CandidateListFilters);
