import React, { useState } from 'react';
import Typography from '@material-ui/core/Typography';
import Grid from '@material-ui/core/Grid';
import { withStyles } from '@material-ui/core/styles';
import ExpandMore from '@material-ui/icons/ExpandMore';
import ExpandLess from '@material-ui/icons/ExpandLess';
import InfoOutlined from '@material-ui/icons/InfoOutlined';

import IconComponent from '../../../Shared/IconComponent/IconComponent';
import LearnMoreLink from '../../Shared/LearnMoreLink/LearnMoreLink';
import DataSourceItem from './DataSourceItem';
import {
    DATA_SOURCES_TOOLTIP_TEXT,
    DATA_SOURCES_LEARN_MORE_URL,
    DATA_SOURCES_ITEMS,
} from './constants';
import productionLocationDetailsDataSourcesInfoStyles from './styles';

const ProductionLocationDetailsDataSourcesInfo = ({ classes, className }) => {
    const [showSubsectionInfo, setShowSubsectionInfo] = useState(false);

    const handleToggle = () => setShowSubsectionInfo(prev => !prev);

    const handleKeyDown = event => {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            handleToggle();
        }
    };

    return (
        <div className={`${classes.container} ${className || ''}`}>
            <div
                className={classes.titleRow}
                role="button"
                tabIndex={0}
                aria-expanded={showSubsectionInfo}
                onClick={handleToggle}
                onKeyDown={handleKeyDown}
            >
                <Typography
                    component="h3"
                    className={classes.sectionTitle}
                    variant="title"
                >
                    Understanding Data Sources
                </Typography>
                <IconComponent
                    title={
                        <>
                            {DATA_SOURCES_TOOLTIP_TEXT}
                            <LearnMoreLink href={DATA_SOURCES_LEARN_MORE_URL} />
                        </>
                    }
                    icon={InfoOutlined}
                    className={classes.infoButton}
                    data-testid="data-sources-info-tooltip"
                />
                <div className={classes.toggleWrap}>
                    {showSubsectionInfo ? (
                        <ExpandLess
                            className={classes.chevron}
                            data-testid="data-sources-expand-less"
                        />
                    ) : (
                        <ExpandMore
                            className={classes.chevron}
                            data-testid="data-sources-expand-more"
                        />
                    )}
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
