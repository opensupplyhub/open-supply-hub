import React, { useMemo } from 'react';
import { connect } from 'react-redux';
import { withStyles } from '@material-ui/core/styles';

import Typography from '@material-ui/core/Typography';
import CircularProgress from '@material-ui/core/CircularProgress';
import Grid from '@material-ui/core/Grid';
import InfoOutlined from '@material-ui/icons/InfoOutlined';
import PartnershipIcon from '../../../Icons/Partnership';
import IconComponent from '../../../Shared/IconComponent/IconComponent';
import PartnerSectionItem from '../ParentSectionItem/PartnerSectionItem';

import partnerDataContainerStyles from './styles';
import getPartnerFieldsAndGroups from './utils';

function PartnerDataContainer({ classes, groups, facilityData, fetching }) {
    const { partnerFields, partnerGroups } = useMemo(
        () => getPartnerFieldsAndGroups(facilityData, groups),
        [facilityData, groups],
    );

    return (
        <Grid container className={classes.root}>
            <Grid item xs={12}>
                <div className={classes.titleRow}>
                    {!fetching && <PartnershipIcon className={classes.icon} />}
                    {fetching && <CircularProgress size={24} />}
                    <Typography
                        variant="title"
                        className={classes.title}
                        component="h3"
                    >
                        {!fetching ? 'Partner Data' : 'Loading Partner Data...'}
                    </Typography>
                    {!fetching && (
                        <IconComponent
                            title="Information provided by third-party partners who host additional social or environmental data."
                            icon={InfoOutlined}
                            className={classes.infoButton}
                        />
                    )}
                </div>
                {!fetching && (
                    <Typography
                        variant="subheading"
                        className={classes.description}
                    >
                        The following information is provided by third-party
                        partners who host additional social or environmental
                        data related to this production location, its context,
                        and/or its operations.{' '}
                        <a
                            href="https://info.opensupplyhub.org/data-integrations"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            Learn more.
                        </a>
                    </Typography>
                )}
            </Grid>
            {!fetching &&
                partnerGroups.map(group => (
                    <Grid item xs={12} key={group.uuid} id={group.uuid}>
                        <PartnerSectionItem
                            group={group}
                            partnerFields={partnerFields}
                        />
                    </Grid>
                ))}
        </Grid>
    );
}

const mapStateToProps = ({
    partnerFieldGroups: { data, fetching },
    facilities: {
        singleFacility: { data: facilityData },
    },
}) => ({
    groups: data?.results || [],
    facilityData,
    fetching,
});

export default connect(mapStateToProps)(
    withStyles(partnerDataContainerStyles)(PartnerDataContainer),
);
