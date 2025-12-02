import React from 'react';
import { object, shape, oneOfType, oneOf } from 'prop-types';

import ClaimInfoSection from './ClaimInfoSection';
import { getLocationFieldsConfig } from './utils.jsx';

const FacilityDetailsClaimedInfo = ({ data }) => {
    if (!data) {
        return null;
    }

    const { facility: location, contact, office } = data;

    // Get field configuration based on available data.
    const fieldsConfig = getLocationFieldsConfig(location, contact, office);

    return (
        <>
            {fieldsConfig.map(field => (
                <ClaimInfoSection
                    key={field.key}
                    label={field.label}
                    value={field.getValue()}
                    fullWidth={field.fullWidth}
                />
            ))}
        </>
    );
};

FacilityDetailsClaimedInfo.defaultProps = {
    data: null,
};

FacilityDetailsClaimedInfo.propTypes = {
    data: shape({
        facility: object,
        contact: oneOfType([object, oneOf([null])]),
        office: oneOfType([object, oneOf([null])]),
    }),
};

export default FacilityDetailsClaimedInfo;
