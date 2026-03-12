import React from 'react';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import get from 'lodash/get';
import Grid from '@material-ui/core/Grid';

import ClaimFlag from '../Heading/ClaimFlag/ClaimFlag';
import ClosureStatus from '../Heading/ClosureStatus/ClosureStatus';
import LocationTitle from '../Heading/LocationTitle/LocationTitle';
import DataSourcesInfo from '../Heading/DataSourcesInfo/DataSourcesInfo';
import GeneralFields from '../ProductionLocationDetailsGeneralFields/ProductionLocationDetailsGeneralFields';
import ClaimDataContainer from '../ClaimSection/ClaimDataContainer/ClaimDataContainer';
import PartnerDataContainer from '../PartnerSection/PartnerDataContainer/PartnerDataContainer';
import DetailsMap from '../ProductionLocationDetailsMap/ProductionLocationDetailsMap';

import { facilityClaimStatusChoicesEnum } from '../../../util/constants';

import productionLocationDetailsContentStyles from './styles';
import OsIdBadge from '../Heading/OsIdBadge/OsIdBadge';

const ProductionLocationDetailsContent = ({
    classes,
    data,
    embed,
    clearFacility,
    useProductionLocationPage,
    location,
}) => {
    const isPendingClaim =
        data?.properties?.claim_info?.status ===
        facilityClaimStatusChoicesEnum.PENDING;
    const isClaimed = !isPendingClaim && !!data?.properties?.claim_info;
    const osId = get(data, 'properties.os_id', '') || '';

    return (
        <div className={classes.container}>
            <LocationTitle data={data} />
            <ClaimFlag
                osId={data?.properties?.os_id}
                isClaimed={!!isClaimed}
                isPending={!!isPendingClaim}
                claimInfo={data?.properties?.claim_info}
                isEmbed={!!embed}
            />
            <OsIdBadge osId={osId} />
            <ClosureStatus
                data={data}
                clearFacility={clearFacility}
                useProductionLocationPage={useProductionLocationPage}
                search={location?.search || ''}
            />
            <DataSourcesInfo className={classes.containerItem} />
            <Grid container className={classes.containerItem}>
                <Grid item sm={12} md={7}>
                    <GeneralFields data={data} />
                </Grid>
                <Grid item sm={12} md={5}>
                    <DetailsMap />
                </Grid>
            </Grid>
            <ClaimDataContainer
                className={classes.containerItem}
                claimInfo={data?.properties?.claim_info}
                isClaimed={isClaimed}
            />
            <PartnerDataContainer />
        </div>
    );
};

ProductionLocationDetailsContent.propTypes = {
    classes: PropTypes.object.isRequired,
    data: PropTypes.object,
    embed: PropTypes.bool,
    clearFacility: PropTypes.func,
    useProductionLocationPage: PropTypes.bool,
    location: PropTypes.shape({ search: PropTypes.string }),
};

ProductionLocationDetailsContent.defaultProps = {
    data: null,
    embed: false,
    clearFacility: () => {},
    useProductionLocationPage: false,
    location: {},
};

export default withStyles(productionLocationDetailsContentStyles)(
    ProductionLocationDetailsContent,
);
