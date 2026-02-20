import React from 'react';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';

const productionLocationDetailsDataSourcesInfoStyles = () =>
    Object.freeze({
        container: Object.freeze({
            backgroundColor: 'white',
        }),
    });

const ProductionLocationDetailsDataSourcesInfo = ({ classes, className }) => (
    <div className={`${classes.container} ${className || ''}`}>
        <Typography variant="title" className={classes.title} component="h3">
            Understanding Data Sources
        </Typography>
    </div>
);

export default withStyles(productionLocationDetailsDataSourcesInfoStyles)(
    ProductionLocationDetailsDataSourcesInfo,
);
