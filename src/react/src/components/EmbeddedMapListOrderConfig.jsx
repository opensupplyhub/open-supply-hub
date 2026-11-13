import React from 'react';
import { arrayOf, bool, func, object, string } from 'prop-types';
import Typography from '@material-ui/core/Typography';
import Checkbox from '@material-ui/core/Checkbox';
import FormControlLabel from '@material-ui/core/FormControlLabel';

import { getDefaultSortOptions } from '../util/embeddedMap';

const styles = {
    section: {
        marginTop: '30px',
    },
    sectionHeader: {
        color: 'rgb(0, 0, 0)',
        fontSize: '24px',
        margin: '10px 0',
    },
    select: {
        marginTop: '10px',
        padding: '8px',
        width: '100%',
        fontSize: '14px',
    },
    checkbox: {
        color: 'rgb(0, 0, 0)',
    },
};

/*
Lets a contributor choose the order of the facility list on their embedded
map (by name, or by any field they show) and whether visitors can change it.
*/
function EmbeddedMapListOrderConfig({
    fields,
    defaultSort,
    setDefaultSort,
    allowVisitorSort,
    setAllowVisitorSort,
    errors,
}) {
    const options = getDefaultSortOptions(fields);
    // A field that is no longer shown can no longer order the list.
    const value = options.some(option => option.value === defaultSort)
        ? defaultSort
        : '';

    return (
        <div style={styles.section}>
            <Typography style={styles.sectionHeader}>List order</Typography>
            <Typography>
                Choose the order facilities appear in on your map&apos;s list.
                Facilities with no value for the chosen field are listed last.
            </Typography>
            {errors?.default_sort && (
                <Typography style={{ color: 'red' }}>
                    Error: {errors.default_sort.join(', ')}
                </Typography>
            )}
            <select
                aria-label="List order"
                value={value}
                onChange={e => setDefaultSort(e.target.value)}
                style={styles.select}
            >
                {options.map(option => (
                    <option key={option.value} value={option.value}>
                        {option.label}
                    </option>
                ))}
            </select>
            <FormControlLabel
                label="Let visitors change the order"
                control={
                    <Checkbox
                        checked={allowVisitorSort}
                        onChange={e => setAllowVisitorSort(e.target.checked)}
                        style={styles.checkbox}
                    />
                }
            />
        </div>
    );
}

EmbeddedMapListOrderConfig.propTypes = {
    fields: arrayOf(object),
    defaultSort: string,
    setDefaultSort: func.isRequired,
    allowVisitorSort: bool,
    setAllowVisitorSort: func.isRequired,
    errors: object,
};

EmbeddedMapListOrderConfig.defaultProps = {
    fields: [],
    defaultSort: '',
    allowVisitorSort: false,
    errors: null,
};

export default EmbeddedMapListOrderConfig;
