import React from 'react';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';

import certificationsStyles from './styles';

const Certifications = ({ classes }) => (
    <div className={classes.container}>
        <Typography variant="title" className={classes.title} component="h3">
            Certifications
        </Typography>
    </div>
);

export default withStyles(certificationsStyles)(Certifications);
