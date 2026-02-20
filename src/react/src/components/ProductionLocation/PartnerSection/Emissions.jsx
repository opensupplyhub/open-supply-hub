import React from 'react';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';

const emissionsStyles = theme =>
    Object.freeze({
        container: Object.freeze({
            backgroundColor: 'white',
            marginBottom: theme.spacing.unit,
        }),
    });

const Emissions = ({ classes }) => (
    <div className={classes.container}>
        <Typography variant="title" className={classes.title} component="h3">
            Emissions
        </Typography>
    </div>
);

export default withStyles(emissionsStyles)(
    Emissions,
);
