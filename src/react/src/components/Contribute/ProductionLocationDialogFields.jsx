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

    const hasMinMaxEqual = value =>
        'min' in value && 'max' in value && value.min === value.max;
    const hasMinOnly = value =>
        'min' in value && Object.keys(value).length === 1;
    const hasMinMax = value =>
        value?.min !== undefined && value?.max !== undefined;
    const hasProcessedValues = value =>
        isArray(value.processed_values) && value.processed_values.length > 0;

    const renderArray = value => {
        if (value.length === 0) return null;
        return value.join(', ');
    };

    const renderObject = value => {
        if (hasMinMaxEqual(value)) {
            return value.min;
        }
        if (hasMinOnly(value)) {
            return value.min.toLocaleString();
        }
        if (hasMinMax(value)) {
            return `${value.min.toLocaleString()} - ${value.max.toLocaleString()}`;
        }
        if (hasProcessedValues(value)) {
            return renderArray(value.processed_values);
        }
        return JSON.stringify(value, (_, v) =>
            typeof v === 'string' ? v.replace(/</g, '&lt;') : v,
        );
    };

    const renderValue = value => {
        if (isArray(value)) {
            return renderArray(value);
        }

        if (typeof value === 'object' && value !== null) {
            return renderObject(value);
        }

        return value;
    };

    const fieldEntries = toPairs(fields);

    const start = startFrom || 0;
    const end = startTo || fieldEntries.length;
    const filteredEntries = slice(fieldEntries, start, end);

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
