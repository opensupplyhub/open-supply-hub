import React, { useMemo } from 'react';
import { connect } from 'react-redux';
import { withStyles } from '@material-ui/core/styles';

import Typography from '@material-ui/core/Typography';
import Grid from '@material-ui/core/Grid';
import { preparePartnerFields } from '../../../PartnerFields/PartnerFieldsSection/utils.jsx';
import ParentSectionItem from '../ParentSectionItem/ParentSectionItem';

import partnerDataContainerStyles from './styles';

function PartnerDataContainer({ classes, groups, facilityData }) {
    const partnerFields = useMemo(
        () => preparePartnerFields(facilityData) ?? [],
        [facilityData],
    );

    const availableFieldNames = useMemo(
        () => new Set(partnerFields.map(f => f.fieldName)),
        [partnerFields],
    );

    const partnerGroups = useMemo(
        () =>
            groups.filter(group =>
                group.partner_fields.some(name =>
                    availableFieldNames.has(name),
                ),
            ),
        [groups, availableFieldNames],
    );

    return (
        <Grid container className={classes.root}>
            <Grid item xs={12}>
                <Typography
                    variant="title"
                    className={classes.title}
                    component="h3"
                >
                    Partner Data
                </Typography>
            </Grid>
            <Grid item xs={12}>
                <Typography
                    variant="subheading"
                    className={classes.description}
                >
                    The following information is provided by third-party
                    partners who host additional social or environmental data
                    related to this production location, its context, and/or its
                    operations.{' '}
                    <a
                        href="https://info.opensupplyhub.org/data-integrations"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        Learn more.
                    </a>
                </Typography>
            </Grid>
            {partnerGroups.map(group => (
                <Grid item xs={12} key={group.uuid} id={group.uuid}>
                    <ParentSectionItem
                        group={group}
                        partnerFields={partnerFields}
                        facilityData={facilityData}
                    />
                </Grid>
            ))}
        </Grid>
    );
}

const mapStateToProps = ({
    partnerFieldGroups: { data },
    facilities: {
        singleFacility: { data: facilityData },
    },
}) => ({
    groups: data?.results || [],
    facilityData,
});

export default connect(mapStateToProps)(
    withStyles(partnerDataContainerStyles)(PartnerDataContainer),
);
