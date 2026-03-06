import React from 'react';
import { connect } from 'react-redux';
import { withStyles } from '@material-ui/core/styles';

import Typography from '@material-ui/core/Typography';
import Grid from '@material-ui/core/Grid';
import ParentSectionItem from '../ParentSectionItem/ParentSectionItem';

import partnerDataContainerStyles from './styles';

function PartnerDataContainer({ classes, groups }) {
    return (
        <Grid container className={classes.root}>
            <Grid item md={12}>
                <Typography
                    variant="title"
                    className={classes.title}
                    component="h3"
                >
                    Partner Data
                </Typography>
            </Grid>
            <Grid item md={12}>
                <Typography variant="subheading" component="h3">
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
            {groups.map(group => (
                <Grid item md={12} key={group.uuid} id={group.uuid}>
                    <ParentSectionItem
                        title={group.name}
                        tooltipText={group.description}
                        disclaimer={group.helper_text}
                    />
                </Grid>
            ))}
        </Grid>
    );
}

const mapStateToProps = ({ partnerFieldGroups: { data } }) => ({
    groups: data?.results || [],
});

export default connect(mapStateToProps)(
    withStyles(partnerDataContainerStyles)(PartnerDataContainer),
);
