import React, { useState } from 'react';
import Typography from '@material-ui/core/Typography';
import IconButton from '@material-ui/core/IconButton';
import Grid from '@material-ui/core/Grid';
import Switch from '@material-ui/core/Switch';
import { withStyles } from '@material-ui/core/styles';
import InfoIcon from '@material-ui/icons/Info';

import DialogTooltip from '../../../Contribute/DialogTooltip';
import DataSourceItem from './DataSourceItem';
import {
    DATA_SOURCES_TOOLTIP_TEXT,
    DATA_SOURCES_LEARN_MORE_URL,
    DATA_SOURCES_ITEMS,
} from './constants';
import productionLocationDetailsDataSourcesInfoStyles from './styles';

const ProductionLocationDetailsDataSourcesInfo = ({ classes, className }) => {
    const [showSubsectionInfo, setShowSubsectionInfo] = useState(false);

    return (
        <div className={`${classes.container} ${className || ''}`}>
            <div className={classes.titleRow}>
                <Typography
                    component="h3"
                    className={classes.sectionTitle}
                    variant="title"
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
                        <b>{showSubsectionInfo ? 'Close' : 'Open'}</b>
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
            <Grid container className={classes.descriptionList} spacing={16}>
                {DATA_SOURCES_ITEMS.map(item => (
                    <DataSourceItem
                        key={item.title}
                        classes={classes}
                        Icon={item.Icon}
                        iconClassName={classes[item.iconClassNameKey]}
                        labelClassName={
                            item.labelClassNameKey
                                ? classes[item.labelClassNameKey]
                                : classes.label
                        }
                        title={item.title}
                        subsectionText={item.subsectionText}
                        showSubsectionInfo={showSubsectionInfo}
                        showLearnMore={Boolean(item.learnMoreUrl)}
                        learnMoreUrl={item.learnMoreUrl || null}
                    />
                ))}
            </Grid>
        </div>
    );
};

export default withStyles(productionLocationDetailsDataSourcesInfoStyles)(
    ProductionLocationDetailsDataSourcesInfo,
);
