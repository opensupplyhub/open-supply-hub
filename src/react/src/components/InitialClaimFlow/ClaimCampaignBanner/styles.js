import COLOURS from '../../../util/COLOURS';

export const claimCampaignBannerStyles = () =>
    Object.freeze({
        banner: Object.freeze({
            backgroundColor: COLOURS.PURPLE_TINT,
            border: `1px solid ${COLOURS.PURPLE}`,
            borderRadius: '4px',
            padding: '12px 16px',
            marginBottom: '24px',
        }),
        code: Object.freeze({
            fontWeight: 600,
            color: COLOURS.PURPLE_TEXT,
        }),
    });

export default claimCampaignBannerStyles;
