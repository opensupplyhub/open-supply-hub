import React from 'react';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';
import InfoOutlinedIcon from '@material-ui/icons/InfoOutlined';

import { INFO_TEXT, LEARN_MORE_LABEL, LEARN_MORE_URL } from './constants';
import infoBoxSectionStyles from './styles';

const InfoBoxSection = ({ classes }) => (
    <div className={classes.infoBox}>
        <div className={classes.infoBoxWithIcon}>
            <InfoOutlinedIcon className={classes.infoIcon} />
            <div className={classes.infoBoxContent}>
                <Typography className={classes.infoText} component="div">
                    {INFO_TEXT}
                </Typography>
                <a
                    href={LEARN_MORE_URL}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={classes.learnMoreLink}
                >
                    {LEARN_MORE_LABEL}
                    <span className={classes.learnMoreArrow}>→</span>
                </a>
            </div>
        </div>
    </div>
);

export default withStyles(infoBoxSectionStyles)(InfoBoxSection);
