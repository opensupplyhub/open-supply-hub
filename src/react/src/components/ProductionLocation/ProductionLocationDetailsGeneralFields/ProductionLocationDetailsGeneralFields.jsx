import React from 'react';
import PropTypes from 'prop-types';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';

import productionLocationDetailsGeneralFieldsStyles from './styles';

/**
 * Render extended fields, activity reports.
 * Show FacilityDetailsClaimedInfo in <FeatureFlag flag={CLAIM_A_FACILITY}>
 */
const ProductionLocationDetailsGeneralFields = ({ classes }) => (
    <div className={classes.container}>
        <Typography variant="title" className={classes.title} component="h3">
            Location Identity
        </Typography>
    </div>
);

ProductionLocationDetailsGeneralFields.propTypes = {
    classes: PropTypes.object.isRequired,
};

export default withStyles(productionLocationDetailsGeneralFieldsStyles)(
    ProductionLocationDetailsGeneralFields,
);
