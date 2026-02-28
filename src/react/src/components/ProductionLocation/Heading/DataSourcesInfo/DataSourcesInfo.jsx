import React from 'react';
import Typography from '@material-ui/core/Typography';
import IconButton from '@material-ui/core/IconButton';
import Grid from '@material-ui/core/Grid';
import { withStyles } from '@material-ui/core/styles';
import InfoIcon from '@material-ui/icons/Info';
import People from '@material-ui/icons/People';
import CheckCircleOutline from '@material-ui/icons/CheckCircleOutline';
import GroupWork from '@material-ui/icons/GroupWork';

import DialogTooltip from '../../../Contribute/DialogTooltip';
import productionLocationDetailsDataSourcesInfoStyles from './styles';

const DATA_SOURCES_TOOLTIP_TEXT =
    'Data comes from multiple sources: claimed profiles verified by facility owners, crowdsourced contributions from the community, OS Hub team research, and partner integrations.';
const DATA_SOURCES_LEARN_MORE_URL =
    'https://info.opensupplyhub.org/resources/an-open-data-model';

const CROWDSOURCED_DESCRIPTION =
    'Data contributed by the Open Supply Hub community (e.g. researchers, brands, civil society). Crowdsourced data points may have been submitted by various contributors and are not verified by the facility.';
const CLAIMED_DESCRIPTION =
    "Data verified by the production location's owner or manager. Claimed data is considered the most authoritative source for this facility.";
const PARTNER_DATA_DESCRIPTION =
    'Data from partner integrations and external datasets. Partner data is supplied by trusted organizations and may include certifications, assessments, or other verified information.';

const ProductionLocationDetailsDataSourcesInfo = ({ classes, className }) => (
    <div className={`${classes.container} ${className || ''}`}>
        <div className={classes.titleRow}>
            <Typography
                component="h3"
                className={classes.sectionTitle}
                variant="h3"
            >
                Understanding Data Sources
            </Typography>
            <DialogTooltip
                text={DATA_SOURCES_TOOLTIP_TEXT}
                textHref={
                    <p style={{ marginTop: 8, marginBottom: 0 }}>
                        <a
                            href={DATA_SOURCES_LEARN_MORE_URL}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{ color: 'white' }}
                        >
                            Learn more →
                        </a>
                    </p>
                }
                interactive
                childComponent={
                    <IconButton
                        className={classes.infoButton}
                        size="small"
                        aria-label="More information about data sources"
                        disableRipple
                    >
                        <InfoIcon style={{ width: 16, height: 16 }} />
                    </IconButton>
                }
            />
        </div>
        <Grid container className={classes.descriptionList} spacing={2}>
            <Grid item sm={12} md={4} className={classes.descriptionItem}>
                <div className={classes.itemContent}>
                    <CheckCircleOutline
                        className={classes.iconClaimed}
                        aria-hidden
                    />
                    <div className={classes.itemText}>
                        <Typography component="span" className={classes.label}>
                            Claimed
                        </Typography>
                        <Typography
                            component="p"
                            className={classes.description}
                        >
                            {CLAIMED_DESCRIPTION}
                        </Typography>
                    </div>
                </div>
            </Grid>
            <Grid item sm={12} md={4} className={classes.descriptionItem}>
                <div className={classes.itemContent}>
                    <People className={classes.iconCrowdsourced} aria-hidden />
                    <div className={classes.itemText}>
                        <Typography component="span" className={classes.label}>
                            Crowdsourced
                        </Typography>
                        <Typography
                            component="p"
                            className={classes.description}
                        >
                            {CROWDSOURCED_DESCRIPTION}
                        </Typography>
                    </div>
                </div>
            </Grid>
            <Grid item sm={12} md={4} className={classes.descriptionItem}>
                <div className={classes.itemContent}>
                    <GroupWork className={classes.iconPartner} aria-hidden />
                    <div className={classes.itemText}>
                        <Typography component="span" className={classes.label}>
                            Partner Data
                        </Typography>
                        <Typography
                            component="p"
                            className={classes.description}
                        >
                            {PARTNER_DATA_DESCRIPTION}
                        </Typography>
                    </div>
                </div>
            </Grid>
        </Grid>
    </div>
);

export default withStyles(productionLocationDetailsDataSourcesInfoStyles)(
    ProductionLocationDetailsDataSourcesInfo,
);
