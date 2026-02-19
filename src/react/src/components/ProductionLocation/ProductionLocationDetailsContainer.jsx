import React from 'react';
import { withStyles } from '@material-ui/core/styles';

import Grid from '@material-ui/core/Grid';

import ProductionLocationDetailsBackToSearch from './ProductionLocationDetailsBackToSearch';
import ProductionLocationDetailsNavBar from './ProductionLocationDetailsNavBar';
import ProductionLocationDetailsContent from './ProductionLocationDetailsContent';
import ProductionLocationDetailsSupplyChain from './ProductionLocationDetailsSupplyChain';
import ProductionLocationDetailsContributeFields from './ProductionLocationDetailsContributeFields';

const productionLocationDetailsStyles = theme =>
    Object.freeze({
        root: Object.freeze({
            background: theme.palette.background.grey,
            padding: '48px 5% 120px 5%',
        }),
    });

function ProductionLocationDetailsContainer({ classes, history }) {
    return (
        <Grid container className={classes.root} spacing={8} xs={12}>
            <Grid item sm={12} md={2}>
                <ProductionLocationDetailsBackToSearch history={history} />
                <ProductionLocationDetailsNavBar />
                <ProductionLocationDetailsContributeFields />
                <ProductionLocationDetailsSupplyChain />
            </Grid>
            <Grid item sm={12} md={10}>
                <ProductionLocationDetailsContent />
            </Grid>
        </Grid>
    );
}

export default withStyles(productionLocationDetailsStyles)(
    ProductionLocationDetailsContainer,
);
