import COLOURS from '../../../util/COLOURS';

/**
 * Drawer styles aligned with design:
 * - Header: title + icon left, close right; subtitle below
 * - Section labels: uppercase grey
 * - Info boxes: purple (promoted) / blue (contributions) with left border
 * - Contribution cards: white, value bold, source purple, date + link right
 */
// eslint-disable-next-line no-unused-vars
export default theme =>
    Object.freeze({
        drawerPaper: Object.freeze({
            width: 390,
            boxShadow: '-4px 0 24px rgba(0,0,0,0.12)',
        }),
        drawerContent: Object.freeze({
            padding: '24px',
            overflowY: 'auto',
            height: '100%',
        }),
        header: Object.freeze({
            display: 'flex',
            alignItems: 'flex-start',
            justifyContent: 'space-between',
            marginBottom: 12,
        }),
        headerLeft: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: 8,
        }),
        titleIcon: Object.freeze({
            fontSize: 24,
            color: COLOURS.PURPLE,
        }),
        title: Object.freeze({
            fontWeight: 700,
            fontSize: '1.4rem',
            lineHeight: 1.3,
            color: COLOURS.NEAR_BLACK,
            marginLeft: '10px',
        }),
        subtitle: Object.freeze({
            marginTop: 8,
            marginBottom: 0,
            fontSize: '1rem',
            lineHeight: 1.4,
            color: COLOURS.DARK_GREY,
            paddingBottom: '16px',
        }),
        closeButton: Object.freeze({
            margin: -8,
            color: COLOURS.DARK_GREY,
            '&:hover': Object.freeze({
                backgroundColor: COLOURS.HOVER_GREY,
                color: COLOURS.PURPLE,
            }),
        }),
        sectionLabel: Object.freeze({
            fontSize: '0.9rem',
            color: COLOURS.DARK_GREY,
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
            marginTop: '16px',
            marginBottom: 8,
            lineHeight: 1.2,
        }),
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
        supportLink: Object.freeze({
            color: COLOURS.PURPLE,
            textDecoration: 'none',
            '&:hover': Object.freeze({
                textDecoration: 'underline',
            }),
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
            olor: COLOURS.MATERIAL_BLUE,
            fontSize: '14px',
            fontWeight: 500,
            textDecoration: 'none',
        }),
        learnMoreArrow: Object.freeze({
            marginLeft: 4,
            marginTop: '2px',
        }),
        contributionCard: Object.freeze({
            backgroundColor: COLOURS.WHITE,
            border: `1px solid ${COLOURS.LIGHT_BORDER_GREY}`,
            borderRadius: 6,
            padding: 16,
            marginBottom: 8,
        }),
        contributionCardPromoted: Object.freeze({
            backgroundColor: '#F8F5FB',
        }),
        contributionValueContainer: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
        }),
        contributionValue: Object.freeze({
            fontWeight: 600,
            fontSize: '18px',
            lineHeight: 1.4,
            color: COLOURS.NEAR_BLACK,
            marginBottom: '8px',
        }),
        contributionValuePromoted: Object.freeze({
            fontSize: '1.25rem',
        }),
        contributionSourceContainer: Object.freeze({
            maxWidth: '45%',
        }),
        contributionSource: Object.freeze({
            fontSize: '1rem',
            lineHeight: 1.4,
            color: COLOURS.PURPLE,
        }),
        contributionSourcePromoted: Object.freeze({
            fontSize: '1.1rem',
        }),
        contributionMetaContainer: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'flex-end',
            fontSize: 14,
            color: COLOURS.DARK_GREY,
            gap: 8,
            maxWidth: '45%',
        }),
        contributionLink: Object.freeze({
            padding: 4,
            color: COLOURS.DARK_GREY,
        }),
        dateWithIcon: Object.freeze({
            display: 'inline-flex',
            alignItems: 'center',
            fontSize: '1rem',
        }),
        dateWithIconPromoted: Object.freeze({
            fontSize: '1.1rem',
        }),
        dateIcon: Object.freeze({
            marginRight: 4,
            marginTop: '2px',
            fontSize: '13px',
            color: COLOURS.DARK_GREY,
        }),
        dateIconPromoted: Object.freeze({
            fontSize: '0.9rem',
        }),
    });
