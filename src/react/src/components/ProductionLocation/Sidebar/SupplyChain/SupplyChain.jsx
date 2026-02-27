import React from 'react';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';

import productionLocationDetailsSupplyChainStyles from './styles';

const ProductionLocationDetailsSupplyChain = ({ classes }) => (
    <div className={classes.container}>
        <Typography variant="title" className={classes.title} component="h3">
            Supply Chain Network
        </Typography>
        <Typography
            variant="subheading"
            className={classes.title}
            component="h5"
        >
            Organizations contributing data to this production location
        </Typography>
    </div>
);

export default withStyles(productionLocationDetailsSupplyChainStyles)(
    ProductionLocationDetailsSupplyChain,
);
