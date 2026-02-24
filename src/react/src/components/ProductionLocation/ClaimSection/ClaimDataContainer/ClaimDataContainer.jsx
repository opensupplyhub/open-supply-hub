import React from 'react';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';

import styles from './styles';

const ClaimDataContainer = ({ classes, className }) => (
    <div className={`${classes.container} ${className || ''}`}>
        <Typography variant="title" className={classes.title} component="h3">
            Claim Data
        </Typography>
    </div>
);

export default withStyles(styles)(ClaimDataContainer);
