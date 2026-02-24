import React from 'react';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';

import styles from './styles';

const ProductionLocationDetailsTitle = ({ classes }) => (
    <div className={classes.container}>
        <Typography variant="title" className={classes.title} component="h1">
            Production location title
        </Typography>
        <Typography>OS ID: xxxxxxxxxxxxxxx</Typography>
    </div>
);

export default withStyles(styles)(ProductionLocationDetailsTitle);
