import React from 'react';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';

import Map from '../../Map';

import productionLocationDetailsMapStyles from './styles';

const ProductionLocationDetailsMap = ({ classes }) => (
    <div className={classes.container}>
        <Typography variant="title" className={classes.title} component="h3">
            Interactive map
        </Typography>
        <Map height="100%" />
    </div>
);

export default withStyles(productionLocationDetailsMapStyles)(
    ProductionLocationDetailsMap,
);
