/* eslint no-unused-vars: 0 */
import React from 'react';
import PropTypes from 'prop-types';
import { map, toPairs, slice, isEmpty } from 'lodash';
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
        if (Array.isArray(value)) {
            return value.join(', ');
        }
        if (typeof value === 'object' && value !== null) {
            if (value.min !== undefined && value.max !== undefined) {
                return `${value.min.toLocaleString()} - ${value.max.toLocaleString()}`;
            }
            if (value.processed_values) {
                return value.processed_values.join(', ');
            }
            return JSON.stringify(value);
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
            {map(filteredEntries, ([key, value]) => (
                <div key={key}>
                    {renderValue(value) ? (
                        <Typography className={classes.label}>
                            {formatLabel(key)}
                        </Typography>
                    ) : null}
                    <Typography className={classes.primaryText}>
                        {renderValue(value)}
                    </Typography>
                </div>
            ))}
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
