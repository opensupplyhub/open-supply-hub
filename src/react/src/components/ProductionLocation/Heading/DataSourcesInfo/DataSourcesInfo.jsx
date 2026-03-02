import React, { useState } from 'react';
import Typography from '@material-ui/core/Typography';
import IconButton from '@material-ui/core/IconButton';
import Grid from '@material-ui/core/Grid';
import Switch from '@material-ui/core/Switch';
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

const CLAIMED_SUBSECTION_TEXT =
    'General information & operational details submitted by production location';
const CROWDSOURCED_SUBSECTION_TEXT =
    "General information shared by supply chain stakeholders & OS Hub's research team";
const PARTNER_SUBSECTION_TEXT =
    'Additional social or environmental information shared by third party platforms';

const ProductionLocationDetailsDataSourcesInfo = ({ classes, className }) => {
    const [showSubsectionInfo, setShowSubsectionInfo] = useState(false);

    return (
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
                <div className={classes.switchWrap}>
                    <Typography
                        component="span"
                        className={classes.switchLabel}
                    >
                        Show more
                    </Typography>
                    <Switch
                        checked={showSubsectionInfo}
                        onChange={e => setShowSubsectionInfo(e.target.checked)}
                        color="primary"
                        size="small"
                        className={classes.switch}
                        inputProps={{
                            'aria-label':
                                'Show extra info under each data source',
                        }}
                    />
                </div>
            </div>
            <Grid container className={classes.descriptionList} spacing={2}>
                <Grid item sm={12} md={4} className={classes.descriptionItem}>
                    <div className={classes.itemContent}>
                        <CheckCircleOutline
                            className={classes.iconClaimed}
                            aria-hidden
                        />
                        <div className={classes.itemText}>
                            <Typography
                                component="span"
                                className={classes.label}
                            >
                                Claimed
                            </Typography>
                            {showSubsectionInfo && (
                                <Typography
                                    component="p"
                                    className={classes.subsectionText}
                                >
                                    {CLAIMED_SUBSECTION_TEXT}
                                </Typography>
                            )}
                        </div>
                    </div>
                </Grid>
                <Grid item sm={12} md={4} className={classes.descriptionItem}>
                    <div className={classes.itemContent}>
                        <People
                            className={classes.iconCrowdsourced}
                            aria-hidden
                        />
                        <div className={classes.itemText}>
                            <Typography
                                component="span"
                                className={classes.label}
                            >
                                Crowdsourced
                            </Typography>
                            {showSubsectionInfo && (
                                <Typography
                                    component="p"
                                    className={classes.subsectionText}
                                >
                                    {CROWDSOURCED_SUBSECTION_TEXT}{' '}
                                    <a
                                        href={DATA_SOURCES_LEARN_MORE_URL}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className={classes.learnMoreLink}
                                    >
                                        Learn more →
                                    </a>
                                </Typography>
                            )}
                        </div>
                    </div>
                </Grid>
                <Grid item sm={12} md={4} className={classes.descriptionItem}>
                    <div className={classes.itemContent}>
                        <GroupWork
                            className={classes.iconPartner}
                            aria-hidden
                        />
                        <div className={classes.itemText}>
                            <Typography
                                component="span"
                                className={classes.label}
                            >
                                Partner Data
                            </Typography>
                            {showSubsectionInfo && (
                                <Typography
                                    component="p"
                                    className={classes.subsectionText}
                                >
                                    {PARTNER_SUBSECTION_TEXT}{' '}
                                    <a
                                        href={DATA_SOURCES_LEARN_MORE_URL}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className={classes.learnMoreLink}
                                    >
                                        Learn more →
                                    </a>
                                </Typography>
                            )}
                        </div>
                    </div>
                </Grid>
            </Grid>
        </div>
    );
};

export default withStyles(productionLocationDetailsDataSourcesInfoStyles)(
    ProductionLocationDetailsDataSourcesInfo,
);
