import React from 'react';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';

import Map from '../../Map';

import productionLocationDetailsMapStyles from './styles';

/**
 * Interactive map for the redesigned production location page.
 * Uses the shared Map component so the same route and Google Maps loading
 * flow as the facility details page is used, avoiding "google is not defined" errors.
 */
const ProductionLocationDetailsMap = ({ classes }) => (
    <div className={classes.root}>
        <Typography variant="title" className={classes.title} component="h3">
            Interactive map
        </Typography>
        <Typography component="p" className={classes.dragHint}>
            Drag to pan
        </Typography>
        <div className={classes.contentContainer}>
            <Map height="100%" />
        </div>
    </div>
);

export default withStyles(productionLocationDetailsMapStyles)(
    ProductionLocationDetailsMap,
);
