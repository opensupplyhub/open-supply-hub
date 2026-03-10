import React from 'react';
import get from 'lodash/get';
import { formatExtendedField } from '../../../../util/util.js';
import FacilityDetailsItem from '../../../../components/FacilityDetailsItem.jsx';

export default function PartnerFieldItem({
    field: { fieldName, formatValue, label, partnerConfigFields },
    facilityData,
}) {
    const values = get(
        facilityData,
        `properties.partner_fields.${fieldName}`,
        [],
    );

    if (!values.length || !values[0]) return null;

    const formatField = item =>
        formatExtendedField({
            ...item,
            formatValue,
        });

    const topValue = formatField(values[0]);

    return (
        <FacilityDetailsItem
            {...topValue}
            label={topValue.label ? topValue.label : label}
            additionalContent={values.slice(1).map(formatField)}
            partnerConfigFields={partnerConfigFields}
        />
    );
}
