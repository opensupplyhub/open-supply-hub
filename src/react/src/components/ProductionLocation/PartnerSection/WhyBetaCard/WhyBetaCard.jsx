import React from 'react';
import { object, shape, string } from 'prop-types';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';

import BetaChip from '../../../Shared/BetaChip/BetaChip';
import {
    GA_LINK_PLACEMENT,
    sendLocationPartnerBetaFeedbackLinkClick,
} from '../../../../util/analytics/gaCustomEvents';
import useViewerUserIdForAnalytics from '../../../../util/analytics/hooks';
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
 *
 * A click on the suggestions link sends the
 * LOCATION_PARTNER_BETA_FEEDBACK_LINK_CLICK analytics event when
 * `gaSpotlightContext` names the section (partner group, OS ID and
 * the beta field label(s)), as the other Spotlight links do.
 */
const WhyBetaCard = ({ classes, gaSpotlightContext }) => {
    const viewerUserId = useViewerUserIdForAnalytics();

    const handleSuggestionsClick = () => {
        if (!gaSpotlightContext) {
            return;
        }
        sendLocationPartnerBetaFeedbackLinkClick({
            partnerGroup: gaSpotlightContext.partner_group,
            linkPlacement: GA_LINK_PLACEMENT.WHY_BETA_CARD,
            destinationUrl: WHY_BETA_LINK_HREF,
            osId: gaSpotlightContext.os_id,
            partnerFieldName: gaSpotlightContext.partner_field_name,
            viewerUserId,
        });
    };

    return (
        <div className={classes.root}>
            <BetaChip className={classes.chip} />
            <div className={classes.card}>
                <Typography component="h4" className={classes.title}>
                    {WHY_BETA_TITLE}
                </Typography>
                <Typography component="p" className={classes.body}>
                    {WHY_BETA_BODY}
                </Typography>
                <a
                    href={WHY_BETA_LINK_HREF}
                    className={classes.link}
                    onClick={handleSuggestionsClick}
                >
                    {WHY_BETA_LINK_TEXT}
                </a>
            </div>
        </div>
    );
};

WhyBetaCard.propTypes = {
    classes: object.isRequired,
    gaSpotlightContext: shape({
        partner_group: string,
        os_id: string,
        partner_field_name: string,
    }),
};

WhyBetaCard.defaultProps = {
    gaSpotlightContext: null,
};

export default withStyles(whyBetaCardStyles)(WhyBetaCard);
