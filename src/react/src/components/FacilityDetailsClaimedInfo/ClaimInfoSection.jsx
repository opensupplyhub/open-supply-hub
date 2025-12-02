import React from 'react';
import { string, bool, node, oneOfType } from 'prop-types';
import Grid from '@material-ui/core/Grid';
import FacilityDetailsItem from '../FacilityDetailsItem';
import { hasDisplayableValue } from './utils';

const ClaimInfoSection = ({ label, value, fullWidth }) => {
    if (!hasDisplayableValue(value)) {
        return null;
    }

    return (
        <Grid item xs={12} md={fullWidth ? 12 : 6}>
            <FacilityDetailsItem label={label} primary={value} isFromClaim />
        </Grid>
    );
};

ClaimInfoSection.propTypes = {
    label: string.isRequired,
    value: oneOfType([string, node]),
    fullWidth: bool,
};

ClaimInfoSection.defaultProps = {
    value: null,
    fullWidth: false,
};

export default ClaimInfoSection;
