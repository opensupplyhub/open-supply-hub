import React, { useMemo } from 'react';
import { connect } from 'react-redux';
import { withStyles } from '@material-ui/core/styles';

import Typography from '@material-ui/core/Typography';
import CircularProgress from '@material-ui/core/CircularProgress';
import Grid from '@material-ui/core/Grid';
import InfoOutlined from '@material-ui/icons/InfoOutlined';
import PartnershipIcon from '../../../Icons/Partnership';
import IconComponent from '../../../Shared/IconComponent/IconComponent';
import PartnerSectionItem from '../PartnerSectionItem/PartnerSectionItem';

import { getEnrichedPartnerGroups } from '../../../../selectors/partnerFieldGroupsSelectors';
import partnerDataContainerStyles from './styles';
import LearnMoreLink from '../../Shared/LearnMoreLink/LearnMoreLink';

function PartnerDataContainer({
    classes,
    partnerGroups,
    facilityData,
    fetching,
}) {
    const hasPartnerData = useMemo(() => {
        const fields = facilityData?.properties?.partner_fields;
        if (!fields) return false;

        const fieldsWithValues = Object.keys(fields).filter(key => {
            const values = fields[key];
            return Array.isArray(values) && values.length > 0 && values[0];
        });

        if (fieldsWithValues.length === 0) return false;

        return partnerGroups.some(group =>
            group.partner_fields.some(field =>
                fieldsWithValues.includes(field),
            ),
        );
    }, [facilityData, partnerGroups]);

    return (
        <>
            <Grid
                container
                className={classes.root}
                data-testid="spotlight-section"
            >
                <Grid item xs={12} className={classes.titleRowContainer}>
                    <div className={classes.titleRow}>
                        {!fetching && (
                            <PartnershipIcon
                                className={classes.icon}
                                color="#8428FA"
                            />
                        )}
                        {fetching && <CircularProgress size={24} />}
                        <Typography
                            variant="title"
                            className={classes.title}
                            component="h3"
                        >
                            {!fetching ? 'Spotlight' : 'Loading Spotlight...'}
                        </Typography>
                        {!fetching && (
                            <IconComponent
                                title={
                                    <>
                                        Are you a data provider and want your
                                        data listed here? Looking to access this
                                        data for compliance reporting, risk
                                        analysis, or supplier monitoring?
                                        <LearnMoreLink href="https://info.opensupplyhub.org/data-integrations" />
                                    </>
                                }
                                icon={InfoOutlined}
                                className={classes.infoButton}
                            />
                        )}
                    </div>
                    {!fetching && hasPartnerData && (
                        <Typography
                            variant="subheading"
                            className={classes.description}
                        >
                            The following information is provided by third-party
                            partners who host additional social or environmental
                            data related to this production location, its
                            context, and/or its operations.{' '}
                            <a
                                href="https://info.opensupplyhub.org/data-integrations"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                Learn more.
                            </a>
                        </Typography>
                    )}
                    {!fetching && !hasPartnerData && (
                        <Typography
                            variant="subheading"
                            className={classes.description}
                        >
                            Open Supply Hub works with third-party partners who
                            provide additional social and environmental data
                            related to production locations, their context,
                            and/or their operations.{' '}
                            <b>
                                No partner data is currently available for this
                                facility.
                            </b>{' '}
                            <a
                                href="https://info.opensupplyhub.org/data-integrations"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                Learn more about our data partnerships.
                            </a>
                        </Typography>
                    )}
                </Grid>
                {!fetching &&
                    hasPartnerData &&
                    partnerGroups.map(group => (
                        <PartnerSectionItem group={group} key={group.uuid} />
                    ))}
            </Grid>
        </>
    );
}

const mapStateToProps = state => ({
    partnerGroups: getEnrichedPartnerGroups(state),
    facilityData: state.facilities.singleFacility.data,
    fetching: state.partnerFieldGroups.fetching,
});

export default connect(mapStateToProps)(
    withStyles(partnerDataContainerStyles)(PartnerDataContainer),
);
