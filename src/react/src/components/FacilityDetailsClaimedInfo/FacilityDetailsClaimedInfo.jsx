import React from 'react';
import { object } from 'prop-types';

import ClaimInfoSection from './ClaimInfoSection';
import { getLocationFieldsConfig } from './utils';

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
    data: object,
};

export default FacilityDetailsClaimedInfo;
