import React from 'react';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Divider from '@material-ui/core/Divider';

import ClaimFlag from '../Heading/ClaimFlag/ClaimFlag';
import LocationTitle from '../Heading/LocationTitle/LocationTitle';
import DataSourcesInfo from '../Heading/DataSourcesInfo/DataSourcesInfo';
import GeneralFields from '../ProductionLocationDetailsGeneralFields/ProductionLocationDetailsGeneralFields';
import ClaimDataContainer from '../ClaimSection/ClaimDataContainer/ClaimDataContainer';
import PartnerDataContainer from '../PartnerSection/PartnerDataContainer/PartnerDataContainer';
import DetailsMap from '../ProductionLocationDetailsMap/ProductionLocationDetailsMap';

import productionLocationDetailsContentStyles from './styles';

const ProductionLocationDetailsContent = ({ classes }) => (
    <div className={classes.container}>
        <LocationTitle />
        <ClaimFlag />
        <DataSourcesInfo className={classes.containerItem} />
        <Grid container xs={12} className={classes.containerItem}>
            <Grid item sm={12} md={7}>
                <GeneralFields />
            </Grid>
            <Grid item sm={12} md={5}>
                <DetailsMap />
            </Grid>
        </Grid>
        <ClaimDataContainer className={classes.containerItem} />
        <Divider variant="middle" className={classes.containerItem} />
        <PartnerDataContainer />
    </div>
);

ProductionLocationDetailsContent.propTypes = {
    classes: PropTypes.object.isRequired,
};

export default withStyles(productionLocationDetailsContentStyles)(
    ProductionLocationDetailsContent,
);
