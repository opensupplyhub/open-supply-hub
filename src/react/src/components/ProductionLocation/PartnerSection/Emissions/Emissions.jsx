import React from 'react';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';

import emissionsStyles from './styles';

const Emissions = ({ classes }) => (
    <div className={classes.container}>
        <Typography variant="title" className={classes.title} component="h3">
            Emissions
        </Typography>
    </div>
);

export default withStyles(emissionsStyles)(Emissions);
