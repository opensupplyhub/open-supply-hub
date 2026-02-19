import React from 'react';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';

import Map from './../Map';

const productionLocationDetailsMapStyles = () =>
    Object.freeze({
        container: {
            backgroundColor: 'white',
        },
    });

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
