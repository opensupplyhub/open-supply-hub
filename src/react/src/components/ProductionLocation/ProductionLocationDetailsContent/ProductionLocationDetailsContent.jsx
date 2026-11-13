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

import EmbedLocationFields from '../../EmbedLocationFields';
import PlainDataPointContext from '../DataPoint/PlainDataPointContext';
import {
    facilityClaimStatusChoicesEnum,
    facilityDetailsActions,
} from '../../../util/constants';
import { hasPartnerData, withoutHiddenSector } from '../../../util/embeddedMap';
import { makeProductionLocationPageLink } from '../../../util/util';
import { getCandidateFromFacilityPayload } from '../../../util/candidates';

import productionLocationDetailsContentStyles from './styles';
import OsIdBadge from '../Heading/OsIdBadge/OsIdBadge';

const ProductionLocationDetailsContent = ({
    classes,
    data,
    embed,
    embedConfig,
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

    // An embedded map whose contributor hides sector data leaves it out.
    const shownData = withoutHiddenSector(data, embed ? embedConfig : null);

    return (
        <PlainDataPointContext.Provider value={!!embed}>
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
                    <Grid
                        item
                        xs={12}
                        lg={7}
                        className={classes.identityRowItem}
                    >
                        <OsIdBadge osId={osId} />
                    </Grid>
                    {/* An embedded map only carries its own contributor's data,
                    so there are no other sources to explain. */}
                    {!embed && (
                        <Grid
                            item
                            xs={12}
                            lg={5}
                            className={classes.identityRowItem}
                        >
                            <DataSourcesInfo />
                        </Grid>
                    )}
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
                        <GeneralFields data={shownData} />
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
                {embed ? (
                    <>
                        {/* The contributor's own fields, then whatever else
                        they have chosen to show. */}
                        <EmbedLocationFields
                            data={data}
                            embedConfig={embedConfig}
                        />
                        {!embedConfig?.hide_sector_data && (
                            <IndustryClassificationSection
                                className={classes.containerItem}
                                data={data}
                            />
                        )}
                        {!!embedConfig?.spotlight && hasPartnerData(data) && (
                            <PartnerDataContainer />
                        )}
                        <div
                            className={classes.containerItem}
                            style={{ marginTop: '16px', fontSize: '16px' }}
                        >
                            <a
                                href={makeProductionLocationPageLink(osId)}
                                target="_blank"
                                rel="noreferrer"
                                className="inline-link"
                            >
                                {facilityDetailsActions.VIEW_ON_OAR}
                            </a>
                        </div>
                    </>
                ) : (
                    <>
                        <ClaimDataContainer className={classes.containerItem} />
                        <IndustryClassificationSection
                            className={classes.containerItem}
                            data={data}
                        />
                        <PartnerDataContainer />
                    </>
                )}
            </div>
        </PlainDataPointContext.Provider>
    );
};

ProductionLocationDetailsContent.propTypes = {
    classes: PropTypes.object.isRequired,
    data: PropTypes.object,
    embed: PropTypes.bool,
    embedConfig: PropTypes.object,
    clearFacility: PropTypes.func,
    useProductionLocationPage: PropTypes.bool,
    location: PropTypes.shape({ search: PropTypes.string }),
};

ProductionLocationDetailsContent.defaultProps = {
    data: null,
    embed: false,
    embedConfig: null,
    clearFacility: () => {},
    useProductionLocationPage: false,
    location: {},
};

export default withStyles(productionLocationDetailsContentStyles)(
    ProductionLocationDetailsContent,
);
