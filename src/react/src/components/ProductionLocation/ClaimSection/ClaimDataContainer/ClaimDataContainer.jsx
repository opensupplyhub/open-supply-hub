import React from 'react';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';

import DataPoint, { STATUS_CLAIMED } from '../../DataPoint/DataPoint';

import styles from './styles';

const ClaimDataContainer = ({ classes, className }) => (
    <div className={`${classes.container} ${className || ''}`}>
        <Typography variant="title" className={classes.title} component="h3">
            Claim Data
        </Typography>
        <DataPoint
            label="Claimed field (testing)"
            value="Sample claimed value"
            tooltipText="Data confirmed by production location owner or manager."
            statusLabel={STATUS_CLAIMED}
            contributorName="Facility Owner"
            date="2023-06-01"
        />
    </div>
);

export default withStyles(styles)(ClaimDataContainer);
