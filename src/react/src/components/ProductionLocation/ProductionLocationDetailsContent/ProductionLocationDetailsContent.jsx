import React, { useMemo, useState } from 'react';
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
import IndustryClassificationSection from '../IndustryClassificationSection/IndustryClassificationSection';
import DetailsMap from '../ProductionLocationDetailsMap/ProductionLocationDetailsMap';
import CandidateHeading from '../../Candidate/CandidateHeading';
import CandidateValidationPanel, {
    PANEL_VARIANTS,
} from '../../Candidate/CandidateValidationPanel';

import { facilityClaimStatusChoicesEnum } from '../../../util/constants';
import { getCandidateFromFacilityPayload } from '../../../util/candidates';

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
    const candidate = useMemo(() => getCandidateFromFacilityPayload(data), [
        data,
    ]);
    // Suggested match the voter is comparing on the map (OSDEV-3247).
    const [highlightedMatchOsId, setHighlightedMatchOsId] = useState(null);

    // Satellite-detected candidate (OSDEV-3247): no contributors, claims
    // or extended fields exist yet, so those sections are replaced by the
    // provenance line and the inline validation panel.
    if (candidate) {
        return (
            <div
                className={classes.container}
                data-testid="candidate-details-content"
            >
                <LocationTitle data={data} />
                <CandidateHeading candidate={candidate} />
                <OsIdBadge osId={osId} />
                <Grid container className={classes.containerItem} spacing={16}>
                    <Grid
                        item
                        md={12}
                        lg={7}
                        className={classes.containerItemInner}
                    >
                        <CandidateValidationPanel
                            candidate={candidate}
                            variant={PANEL_VARIANTS.INLINE}
                            highlightedMatchOsId={highlightedMatchOsId}
                            onShowMatch={setHighlightedMatchOsId}
                        />
                    </Grid>
                    <Grid
                        item
                        md={12}
                        lg={5}
                        className={classes.containerItemInner}
                    >
                        <DetailsMap
                            highlightedMatchOsId={highlightedMatchOsId}
                        />
                    </Grid>
                </Grid>
            </div>
        );
    }

    return (
        <div className={classes.container}>
            <LocationTitle data={data} />
            <ClaimFlag
                osId={data?.properties?.os_id}
                isClaimed={!!isClaimed}
                isPending={!!isPendingClaim}
                claimInfo={data?.properties?.claim_info}
                isEmbed={!!embed}
                facilityName={data?.properties?.name}
                isClosed={!!data?.properties?.is_closed}
            />
            <Grid container className={classes.containerItem} spacing={16}>
                <Grid item xs={12} lg={7} className={classes.identityRowItem}>
                    <OsIdBadge osId={osId} />
                </Grid>
                <Grid item xs={12} lg={5} className={classes.identityRowItem}>
                    <DataSourcesInfo />
                </Grid>
            </Grid>
            <ClosureStatus
                data={data}
                clearFacility={clearFacility}
                useProductionLocationPage={useProductionLocationPage}
                search={location?.search || ''}
            />
            <Grid container className={classes.containerItem} spacing={16}>
                <Grid
                    item
                    md={12}
                    lg={7}
                    className={classes.containerItemInner}
                >
                    <GeneralFields data={data} />
                </Grid>
                <Grid
                    item
                    md={12}
                    lg={5}
                    className={classes.containerItemInner}
                >
                    <DetailsMap />
                </Grid>
            </Grid>
            <ClaimDataContainer className={classes.containerItem} />
            <IndustryClassificationSection
                className={classes.containerItem}
                data={data}
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
