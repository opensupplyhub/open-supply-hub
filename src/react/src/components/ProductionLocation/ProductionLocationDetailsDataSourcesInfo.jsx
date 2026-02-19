import React from 'react';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';

const productionLocationDetailsDataSourcesInfoStyles = theme =>
    Object.freeze({
        container: Object.freeze({
            backgroundColor: 'white',
            marginBottom: theme.spacing.unit,
        }),
    });

const ProductionLocationDetailsDataSourcesInfo = ({ classes }) => (
    <div className={classes.container}>
        <Typography variant="title" className={classes.title} component="h3">
            Understanding Data Sources
        </Typography>
    </div>
);

export default withStyles(productionLocationDetailsDataSourcesInfoStyles)(
    ProductionLocationDetailsDataSourcesInfo,
);
