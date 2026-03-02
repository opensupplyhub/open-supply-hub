import React from 'react';
import PropTypes from 'prop-types';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';

const DataSourceItem = ({
    classes,
    Icon,
    iconClassName,
    title,
    subsectionText,
    showSubsectionInfo,
    showLearnMore,
    learnMoreUrl,
}) => (
    <Grid item sm={12} md={4} className={classes.descriptionItem}>
        <div className={classes.itemContent}>
            <Icon className={iconClassName} aria-hidden />
            <div className={classes.itemText}>
                <Typography
                    component="span"
                    className={classes.label}
                    variant="body1"
                >
                    {title}
                </Typography>
                {showSubsectionInfo && (
                    <Typography
                        component="p"
                        variant="body1"
                        className={classes.subsectionText}
                    >
                        {subsectionText}
                        {showLearnMore && learnMoreUrl && (
                            <>
                                {' '}
                                <a
                                    href={learnMoreUrl}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className={classes.learnMoreLink}
                                >
                                    Learn more →
                                </a>
                            </>
                        )}
                    </Typography>
                )}
            </div>
        </div>
    </Grid>
);

DataSourceItem.propTypes = {
    classes: PropTypes.object.isRequired,
    Icon: PropTypes.func.isRequired,
    iconClassName: PropTypes.string.isRequired,
    title: PropTypes.string.isRequired,
    subsectionText: PropTypes.string.isRequired,
    showSubsectionInfo: PropTypes.bool.isRequired,
    showLearnMore: PropTypes.bool,
    learnMoreUrl: PropTypes.string,
};

DataSourceItem.defaultProps = {
    showLearnMore: false,
    learnMoreUrl: null,
};

export default DataSourceItem;
