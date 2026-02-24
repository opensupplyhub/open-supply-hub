import React from 'react';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';

import styles from './styles';

const AssessmentsAndAudits = ({ classes }) => (
    <div className={classes.container}>
        <Typography variant="title" className={classes.title} component="h3">
            Assessments and Audits
        </Typography>
    </div>
);

export default withStyles(styles)(AssessmentsAndAudits);
