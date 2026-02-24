import React from 'react';
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';

import BackToSearch from '../Sidebar/BackToSearch';
import NavBar from '../Sidebar/NavBar';
import SupplyChain from '../Sidebar/SupplyChain';
import ContributeFields from '../Sidebar/ContributeFields';
import ProductionLocationDetailsContent from '../ProductionLocationDetailsContent';

import styles from './styles';

function ProductionLocationDetailsContainer({ classes, history }) {
    return (
        <Grid container className={classes.root} spacing={8} xs={12}>
            <Grid item xs={12} md={2}>
                <BackToSearch history={history} />
                <NavBar />
                <ContributeFields />
                <SupplyChain />
            </Grid>
            <Grid item xs={12} md={10}>
                <ProductionLocationDetailsContent />
            </Grid>
        </Grid>
    );
}

export default withStyles(styles)(ProductionLocationDetailsContainer);
