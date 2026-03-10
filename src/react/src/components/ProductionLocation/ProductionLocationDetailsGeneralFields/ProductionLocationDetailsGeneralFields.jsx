import React, { useMemo } from 'react';
import { arrayOf, bool, object } from 'prop-types';
import { connect } from 'react-redux';
import Typography from '@material-ui/core/Typography';
import Grid from '@material-ui/core/Grid';
import Divider from '@material-ui/core/Divider';
import { withStyles } from '@material-ui/core/styles';
import InfoOutlined from '@material-ui/icons/InfoOutlined';

import IconComponent from '../../Shared/IconComponent/IconComponent';
import LearnMoreLink from '../Shared/LearnMoreLink/LearnMoreLink';
import GeneralInformationIcon from '../../Icons/GeneralInformation';
import DataPoint from '../DataPoint/DataPoint';
import ContributionsDrawer from '../ContributionsDrawer/ContributionsDrawer';
import getVisibleFields from './utils';
import useDrawerState from './hooks';
import { SHOW_ADDITIONAL_IDENTIFIERS } from '../../../util/constants';
import { convertFeatureFlagsObjectToListOfActiveFlags } from '../../../util/util';
import { featureFlagPropType } from '../../../util/propTypes';

import productionLocationDetailsGeneralFieldsStyles from './styles';

const ProductionLocationDetailsGeneralFields = ({
    classes,
    data,
    activeFeatureFlags,
    featureFlagsFetching,
}) => {
    const [openDrawerFieldKey, openDrawer, closeDrawer] = useDrawerState(null);
    const showAdditionalIdentifiers =
        !featureFlagsFetching &&
        activeFeatureFlags.includes(SHOW_ADDITIONAL_IDENTIFIERS);
    const visibleItems = useMemo(
        () => getVisibleFields(data, showAdditionalIdentifiers),
        [data, showAdditionalIdentifiers],
    );

    const renderDataPoints = items =>
        items.map(item => (
            <Grid item key={item.key}>
                <DataPoint
                    label={item.label}
                    value={item.value}
                    tooltipText={item.tooltipText}
                    statusLabel={item.statusLabel}
                    contributorName={item.contributorName}
                    userId={item.userId}
                    date={item.date}
                    drawerData={item.drawerData}
                    onOpenDrawer={
                        item.drawerData ? () => openDrawer(item.key) : undefined
                    }
                    renderDrawer={
                        item.drawerData
                            ? () =>
                                  openDrawerFieldKey === item.key ? (
                                      <ContributionsDrawer
                                          open
                                          onClose={closeDrawer}
                                          fieldName={item.label}
                                          promotedContribution={
                                              item.drawerData
                                                  .promotedContribution
                                          }
                                          contributions={
                                              item.drawerData.contributions ||
                                              []
                                          }
                                      />
                                  ) : null
                            : undefined
                    }
                />
            </Grid>
        ));

    return (
        <Grid id="general-information" container className={classes.container}>
            <Grid item xs={12} className={classes.titleRow}>
                <GeneralInformationIcon width={24} height={24} />
                <Typography
                    variant="title"
                    className={classes.title}
                    component="h3"
                >
                    General Information
                </Typography>
                <IconComponent
                    title={
                        <>
                            Core identifying information about this production
                            location.{' '}
                            <LearnMoreLink href="https://info.opensupplyhub.org/resources/preparing-data">
                                Learn more about each data point.
                            </LearnMoreLink>
                        </>
                    }
                    icon={InfoOutlined}
                    className={classes.infoIcon}
                />
            </Grid>
            <Grid item xs={12}>
                <Divider />
            </Grid>
            <Grid item xs={12} className={classes.dataList}>
                {renderDataPoints(visibleItems)}
            </Grid>
        </Grid>
    );
};

ProductionLocationDetailsGeneralFields.propTypes = {
    classes: object.isRequired,
    data: object,
    activeFeatureFlags: arrayOf(featureFlagPropType).isRequired,
    featureFlagsFetching: bool.isRequired,
};

ProductionLocationDetailsGeneralFields.defaultProps = {
    data: null,
};

const mapStateToProps = ({ featureFlags: { fetching, flags } }) => ({
    activeFeatureFlags: convertFeatureFlagsObjectToListOfActiveFlags(flags),
    featureFlagsFetching: fetching,
});

export default connect(mapStateToProps)(
    withStyles(productionLocationDetailsGeneralFieldsStyles)(
        ProductionLocationDetailsGeneralFields,
    ),
);
