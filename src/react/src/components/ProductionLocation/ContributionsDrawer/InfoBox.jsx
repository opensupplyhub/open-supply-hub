import React from 'react';
import PropTypes from 'prop-types';
import Typography from '@material-ui/core/Typography';
import InfoIcon from '@material-ui/icons/InfoOutlined';
import { withStyles } from '@material-ui/core/styles';

import styles from './styles';

const InfoBox = ({
    classes,
    title,
    children,
    variant,
    learnMoreUrl,
    learnMoreLabel,
}) => {
    const isPromoted = variant === 'promoted';
    const boxClass = isPromoted
        ? classes.infoBoxPromoted
        : classes.infoBoxContributions;
    const titleClass = isPromoted
        ? classes.infoTitle
        : `${classes.infoTitle} ${classes.infoTitleBlue}`;
    const infoTextClass = isPromoted
        ? classes.infoTextPromoted
        : classes.infoTextContributions;
    const learnMoreLinkClass = isPromoted
        ? classes.learnMoreLinkPromoted
        : classes.learnMoreLinkContributions;
    const showInfoIcon = !isPromoted;

    const content = (
        <>
            {title ? (
                <Typography className={titleClass} component="p">
                    {title}
                </Typography>
            ) : null}
            <Typography className={infoTextClass} component="div">
                {children}
            </Typography>
            {learnMoreUrl && learnMoreLabel ? (
                <a
                    href={learnMoreUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={learnMoreLinkClass}
                >
                    {learnMoreLabel}
                    <span className={classes.learnMoreArrow}>→</span>
                </a>
            ) : null}
        </>
    );

    return (
        <div className={`${classes.infoBox} ${boxClass}`}>
            {showInfoIcon ? (
                <div className={classes.infoBoxWithIcon}>
                    <InfoIcon className={classes.infoIcon} />
                    <div className={classes.infoBoxContent}>{content}</div>
                </div>
            ) : (
                content
            )}
        </div>
    );
};

InfoBox.propTypes = {
    classes: PropTypes.object.isRequired,
    title: PropTypes.string,
    children: PropTypes.node.isRequired,
    variant: PropTypes.oneOf(['promoted', 'contributions']),
    learnMoreUrl: PropTypes.string,
    learnMoreLabel: PropTypes.string,
};

InfoBox.defaultProps = {
    title: null,
    variant: 'contributions',
    learnMoreUrl: null,
    learnMoreLabel: null,
};

export default withStyles(styles)(InfoBox);
