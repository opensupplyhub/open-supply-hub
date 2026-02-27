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
            maxWidth: 560,
            minWidth: '33%',
            boxShadow: '-4px 0 24px rgba(0,0,0,0.12)',
        }),
        drawerContent: Object.freeze({
            padding: '16px 72px 24px 72px',
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
            color: COLOURS.DARK_GREY,
        }),
        title: Object.freeze({
            fontWeight: 700,
            fontSize: 20,
            lineHeight: 1.3,
            color: COLOURS.NEAR_BLACK,
        }),
        subtitle: Object.freeze({
            marginTop: 8,
            marginBottom: 0,
            fontSize: 14,
            lineHeight: 1.4,
            color: COLOURS.DARK_GREY,
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
            fontSize: 11,
            fontWeight: 700,
            color: COLOURS.DARK_GREY,
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
            marginTop: 24,
            marginBottom: 8,
            lineHeight: 1.2,
        }),
        infoBox: Object.freeze({
            padding: 16,
            borderRadius: 8,
            marginBottom: 16,
        }),
        infoBoxPromoted: Object.freeze({
            backgroundColor: COLOURS.LIGHT_PURPLE_BG,
            borderLeft: `4px solid ${COLOURS.PURPLE}`,
        }),
        infoBoxContributions: Object.freeze({
            backgroundColor: COLOURS.EXTRA_LIGHT_BLUE,
            borderLeft: `4px solid ${COLOURS.MATERIAL_BLUE}`,
        }),
        infoTitle: Object.freeze({
            fontWeight: 700,
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
        }),
        infoBoxContent: Object.freeze({
            flex: 1,
        }),
        infoText: Object.freeze({
            fontSize: 14,
            lineHeight: 1.5,
            color: COLOURS.DARK_GREY,
        }),
        learnMoreLink: Object.freeze({
            marginTop: 8,
            display: 'inline-flex',
            alignItems: 'center',
            color: COLOURS.MATERIAL_BLUE,
            fontSize: 14,
            fontWeight: 500,
            textDecoration: 'none',
            '&:hover': Object.freeze({
                textDecoration: 'underline',
            }),
        }),
        learnMoreArrow: Object.freeze({
            marginLeft: 4,
        }),
        contributionCard: Object.freeze({
            backgroundColor: COLOURS.WHITE,
            border: `1px solid ${COLOURS.LIGHT_BORDER_GREY}`,
            borderRadius: 6,
            padding: 16,
            marginBottom: 8,
        }),
        contributionValue: Object.freeze({
            fontWeight: 700,
            fontSize: 16,
            lineHeight: 1.4,
            color: COLOURS.NEAR_BLACK,
        }),
        contributionSource: Object.freeze({
            fontSize: 14,
            lineHeight: 1.4,
            color: COLOURS.PURPLE,
            marginTop: 4,
        }),
        contributionMeta: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'flex-end',
            marginTop: 8,
            fontSize: 14,
            color: COLOURS.DARK_GREY,
            gap: 8,
        }),
        contributionLink: Object.freeze({
            padding: 4,
            color: COLOURS.DARK_GREY,
        }),
        dateWithIcon: Object.freeze({
            display: 'inline-flex',
            alignItems: 'center',
        }),
        dateIcon: Object.freeze({
            marginRight: 4,
            fontSize: 18,
            color: COLOURS.DARK_GREY,
        }),
        listScroll: Object.freeze({
            maxHeight: 320,
            overflowY: 'auto',
        }),
    });
