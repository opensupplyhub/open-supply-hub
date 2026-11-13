import React from 'react';
import { object } from 'prop-types';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';

import BetaChip from '../../../Shared/BetaChip/BetaChip';
import whyBetaCardStyles from './styles';
import {
    WHY_BETA_TITLE,
    WHY_BETA_BODY,
    WHY_BETA_LINK_TEXT,
    WHY_BETA_LINK_HREF,
} from './constants';

/**
 * Explains the Beta chip once per Spotlight section that holds a
 * beta dataset (OSDEV-3778). The chip above the card is the same one
 * shown beside each beta field's title, so the reader can tie the
 * two together.
 */
const WhyBetaCard = ({ classes }) => (
    <div className={classes.root}>
        <BetaChip className={classes.chip} />
        <div className={classes.card}>
            <Typography component="h4" className={classes.title}>
                {WHY_BETA_TITLE}
            </Typography>
            <Typography component="p" className={classes.body}>
                {WHY_BETA_BODY}
            </Typography>
            <a href={WHY_BETA_LINK_HREF} className={classes.link}>
                {WHY_BETA_LINK_TEXT}
            </a>
        </div>
    </div>
);

WhyBetaCard.propTypes = {
    classes: object.isRequired,
};

export default withStyles(whyBetaCardStyles)(WhyBetaCard);
