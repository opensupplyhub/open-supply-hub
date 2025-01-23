import React from 'react';
import PropTypes from 'prop-types';
import { map, toPairs, isArray, slice } from 'lodash';
import Typography from '@material-ui/core/Typography';

const ProductionLocationDialogFields = ({
    fields,
    startTo,
    startFrom,
    classes,
}) => {
    const formatLabel = key =>
        key.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());

    const renderValue = value => {
        if (isArray(value)) {
            if (value.length === 0) return 'None';
            return value.join(', ');
        }
        if (typeof value === 'object' && value !== null) {
            if ('min' in value && 'max' in value && value.min === value.max) {
                return value.min;
            }
            if ('min' in value && Object.keys(value).length === 1) {
                return value.min.toLocaleString();
            }
            if (value?.min !== undefined && value?.max !== undefined) {
                return `${value.min.toLocaleString()} - ${value.max.toLocaleString()}`;
            }
            if (isArray(value.processed_values)) {
                if (value.processed_values.length === 0) return 'None';
                return value.processed_values.join(', ');
            }
            return JSON.stringify(value, (_, v) =>
                typeof v === 'string' ? v.replace(/</g, '&lt;') : v,
            );
        }
        return value;
    };

    const fieldEntries = toPairs(fields);

    let filteredEntries;

    if (startTo) {
        filteredEntries = slice(fieldEntries, 0, startTo);
    } else if (startFrom) {
        filteredEntries = slice(fieldEntries, startFrom);
    } else {
        filteredEntries = fieldEntries;
    }

    return (
        <>
            {map(filteredEntries, ([key, value]) => {
                const renderedValue = renderValue(value);
                if (!renderedValue) {
                    return null;
                }
                return (
                    <div key={key}>
                        <Typography className={classes.label}>
                            {formatLabel(key)}
                        </Typography>
                        <Typography className={classes.primaryText}>
                            {renderedValue}
                        </Typography>
                    </div>
                );
            })}
        </>
    );
};

ProductionLocationDialogFields.propTypes = {
    fields: PropTypes.object.isRequired,
    startTo: PropTypes.number,
    startFrom: PropTypes.number,
    classes: PropTypes.object.isRequired,
};

ProductionLocationDialogFields.defaultProps = {
    startTo: null,
    startFrom: null,
};

export default ProductionLocationDialogFields;
