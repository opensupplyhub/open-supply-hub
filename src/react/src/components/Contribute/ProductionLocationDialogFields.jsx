import React from 'react';
import { object, number } from 'prop-types';
import { map, toPairs, isArray, slice } from 'lodash';
import Typography from '@material-ui/core/Typography';

const ProductionLocationDialogFields = ({
    filteredAdditionalFields,
    startTo,
    startFrom,
    classes,
}) => {
    // TODO: Remove transformLabel usage in scope of https://opensupplyhub.atlassian.net/browse/OSDEV-1657
    const transformLabel = key => {
        switch (key) {
            case 'facility_type':
                return 'location_type';
            default:
                return key;
        }
    };
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
        if (!value || value.length === 0) return null;
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
        return value || null;
    };

    const fieldEntries = toPairs(filteredAdditionalFields);

    const start = startFrom || 0;
    const end = startTo || fieldEntries.length;
    const filteredEntries = slice(fieldEntries, start, end);

    return (
        <>
            {map(filteredEntries, ([key, value]) => {
                const title = transformLabel(key);
                const renderedValue = renderValue(value);
                if (!renderedValue) {
                    return null;
                }
                return (
                    <div key={title}>
                        <Typography className={classes.label}>
                            {formatLabel(title)}
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
    filteredAdditionalFields: object.isRequired,
    startTo: number,
    startFrom: number,
    classes: object.isRequired,
};

ProductionLocationDialogFields.defaultProps = {
    startTo: null,
    startFrom: null,
};

export default ProductionLocationDialogFields;
