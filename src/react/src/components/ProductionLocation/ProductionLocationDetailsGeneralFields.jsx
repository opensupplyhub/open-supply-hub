import React from 'react';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';

const locationFieldsStyles = theme =>
    Object.freeze({
        container: Object.freeze({
            backgroundColor: 'white',
            [theme.breakpoints.up('md')]: {
                marginRight: theme.spacing.unit,
            },
        }),
    });

/**
    Render extended fields, activity reports.
    Show FacilityDetailsClaimedInfo in <FeatureFlag flag={CLAIM_A_FACILITY}>
 */
const ProductionLocationDetailsGeneralFields = ({ classes }) => (
    <div className={classes.container}>
        <Typography variant="title" className={classes.title} component="h3">
            Location Identity
        </Typography>
    </div>
);

export default withStyles(locationFieldsStyles)(
    ProductionLocationDetailsGeneralFields,
);
