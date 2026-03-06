import COLOURS from '../../../../util/COLOURS';

export default () =>
    Object.freeze({
        infoBox: Object.freeze({
            padding: '16px',
            marginBottom: '16px',
        }),
        infoBoxPromoted: Object.freeze({
            backgroundColor: '#F8F5FB',
            border: `1px solid #E2D1F0`,
        }),
        infoBoxContributions: Object.freeze({
            backgroundColor: COLOURS.EXTRA_LIGHT_BLUE,
            border: `1px solid #C0DBFE`,
        }),
        infoTitle: Object.freeze({
            fontSize: '0.875rem',
            lineHeight: 1.4,
            color: COLOURS.PURPLE,
            marginBottom: '8px',
        }),
        infoTitleBlue: Object.freeze({
            color: COLOURS.MATERIAL_BLUE,
        }),
        infoBoxWithIcon: Object.freeze({
            display: 'flex',
            alignItems: 'flex-start',
            gap: '8px',
        }),
        infoIcon: Object.freeze({
            fontSize: '1.25rem',
            color: COLOURS.MATERIAL_BLUE,
            flexShrink: 0,
            marginTop: '2px',
            marginRight: '8px',
        }),
        infoBoxContent: Object.freeze({
            flex: 1,
        }),
        infoTextPromoted: Object.freeze({
            fontSize: '0.875rem',
            lineHeight: 1.5,
            color: COLOURS.DARK_GREY,
        }),
        infoTextContributions: Object.freeze({
            fontSize: '1rem',
            lineHeight: 1.5,
            color: COLOURS.DARK_GREY,
        }),
        learnMoreLinkContributions: Object.freeze({
            marginTop: '8px',
            display: 'inline-flex',
            alignItems: 'center',
            color: COLOURS.MATERIAL_BLUE,
            fontSize: '1rem',
            textDecoration: 'none',
            '&:hover': Object.freeze({
                textDecoration: 'underline',
            }),
        }),
        learnMoreLinkPromoted: Object.freeze({
            marginTop: '8px',
            display: 'inline-flex',
            alignItems: 'center',
            color: COLOURS.MATERIAL_BLUE,
            fontSize: '0.875rem',
            textDecoration: 'none',
        }),
    });
