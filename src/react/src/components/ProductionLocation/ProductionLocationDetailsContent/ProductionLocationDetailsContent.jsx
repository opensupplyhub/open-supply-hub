import React from 'react';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Divider from '@material-ui/core/Divider';

import ClaimFlag from '../Heading/ClaimFlag/ClaimFlag';
import ClosureStatus from '../Heading/ClosureStatus/ClosureStatus';
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
          <ClaimFlag
            osId={data.properties.os_id}
            isClaimed={isClaimed}
            isPending={isPendingClaim}
            claimInfo={data?.properties?.claim_info}
            isEmbed={!!embed}
        />
        <ClosureStatus
            data={data}
            clearFacility={clearFacility}
            useProductionLocationPage={useProductionLocationPage}
            search={location?.search || ''}
        />
        <DataSourcesInfo className={classes.containerItem} />
        <Grid container className={classes.containerItem}>
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
