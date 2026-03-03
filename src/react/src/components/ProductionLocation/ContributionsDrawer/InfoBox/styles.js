import COLOURS from '../../../../util/COLOURS';

export default () =>
    Object.freeze({
        infoBox: Object.freeze({
            padding: 16,
            borderRadius: 8,
            marginBottom: 16,
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
            fontSize: 14,
            lineHeight: 1.4,
            color: COLOURS.PURPLE,
            marginBottom: 8,
        }),
        infoTitleBlue: Object.freeze({
            color: COLOURS.MATERIAL_BLUE,
        }),
        infoBoxWithIcon: Object.freeze({
            display: 'flex',
            alignItems: 'flex-start',
            gap: 8,
        }),
        infoIcon: Object.freeze({
            fontSize: 20,
            color: COLOURS.MATERIAL_BLUE,
            flexShrink: 0,
            marginTop: 2,
            marginRight: '8px',
        }),
        infoBoxContent: Object.freeze({
            flex: 1,
        }),
        infoTextPromoted: Object.freeze({
            fontSize: 14,
            lineHeight: 1.5,
            color: COLOURS.DARK_GREY,
        }),
        infoTextContributions: Object.freeze({
            fontSize: '1rem',
            lineHeight: 1.5,
            color: COLOURS.DARK_GREY,
        }),
        learnMoreLinkContributions: Object.freeze({
            marginTop: 8,
            display: 'inline-flex',
            alignItems: 'center',
            color: COLOURS.MATERIAL_BLUE,
            fontSize: '1rem',
            fontWeight: 500,
            textDecoration: 'none',
            '&:hover': Object.freeze({
                textDecoration: 'underline',
            }),
        }),
        learnMoreLinkPromoted: Object.freeze({
            marginTop: 8,
            display: 'inline-flex',
            alignItems: 'center',
            color: COLOURS.MATERIAL_BLUE,
            fontSize: '14px',
            fontWeight: 500,
            textDecoration: 'none',
        }),
        learnMoreArrow: Object.freeze({
            marginLeft: 4,
            marginTop: '2px',
        }),
    });
