import React from 'react';
import Grid from '@material-ui/core/Grid';
import get from 'lodash/get';

import FacilityDetailsItem from '../../FacilityDetailsItem';
import {
    formatExtendedField,
    formatPartnerFieldValue,
} from '../../../util/util';

export const renderPartnerField = ({
    label,
    fieldName,
    formatValue,
    partnerConfigFields,
    data,
}) => {
    const values = get(data, `properties.partner_fields.${fieldName}`, []);

    if (!values.length || !values[0]) return null;

    const formatField = item =>
        formatExtendedField({
            ...item,
            formatValue,
        });

    const topValue = formatField(values[0]);

    return (
        <Grid item xs={12} md={6} key={`partner-${label}`}>
            <FacilityDetailsItem
                {...topValue}
                label={topValue.label ? topValue.label : label}
                additionalContent={values.slice(1).map(formatField)}
                partnerConfigFields={partnerConfigFields}
            />
        </Grid>
    );
};

export const preparePartnerFields = data => {
    const partnerFieldNames = Object.keys(
        get(data, 'properties.partner_fields', {}),
    );

    return partnerFieldNames.map(fieldName => {
        /*
        We have to rely on the first element of the partner-field list
        because the backend isn't configured to store partner-specific
        settings in a separate metadata object.
        */
        const firstEntry =
            get(data, `properties.partner_fields.${fieldName}[0]`) || {};
        const {
            base_url: baseUrl, // eslint-disable-line camelcase
            display_text: displayText, // eslint-disable-line camelcase
        } = firstEntry;

        const partnerConfigFields = { baseUrl, displayText };

        return {
            fieldName,
            label: fieldName
                .replace(/_/g, ' ')
                .replace(/\b\w/g, l => l.toUpperCase()),
            formatValue: formatPartnerFieldValue,
            partnerConfigFields,
        };
    });
};

export const hasVisiblePartnerFields = (partnerFields, data) => {
    if (!partnerFields.length) return false;

    const renderedFields = partnerFields.map(field =>
        renderPartnerField({ ...field, data }),
    );

    return renderedFields.some(field => field !== null);
};
