import COLOURS from '../../../../util/COLOURS';

export default () =>
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
            marginBottom: 4,
        }),
        headerLeft: Object.freeze({
            display: 'flex',
            alignItems: 'center',
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
            marginLeft: '8px',
        }),
        subtitle: Object.freeze({
            fontSize: '0.9rem',
            color: COLOURS.DARK_GREY,
            marginBottom: '16px',
        }),
        closeButton: Object.freeze({
            margin: -8,
            color: COLOURS.DARK_GREY,
            '&:hover': Object.freeze({
                backgroundColor: COLOURS.HOVER_GREY,
                color: COLOURS.PURPLE,
            }),
        }),
        infoBox: Object.freeze({
            backgroundColor: COLOURS.EXTRA_LIGHT_BLUE,
            border: `1px solid #C0DBFE`,
            borderRadius: 8,
            padding: 16,
            marginBottom: 16,
            display: 'flex',
            alignItems: 'flex-start',
            gap: 8,
        }),
        infoIcon: Object.freeze({
            fontSize: 18,
            color: COLOURS.MATERIAL_BLUE,
            flexShrink: 0,
            marginTop: 2,
        }),
        infoText: Object.freeze({
            fontSize: '0.85rem',
            lineHeight: 1.5,
            color: COLOURS.DARK_GREY,
        }),
        learnMoreLink: Object.freeze({
            display: 'block',
            marginTop: 6,
            fontSize: '0.85rem',
            color: COLOURS.MATERIAL_BLUE,
            textDecoration: 'none',
            '&:hover': Object.freeze({
                textDecoration: 'underline',
            }),
        }),
        typeSummary: Object.freeze({
            marginBottom: 16,
        }),
        typeChip: Object.freeze({
            fontSize: '0.9rem',
            color: COLOURS.NEAR_BLACK,
            lineHeight: 1.8,
        }),
        divider: Object.freeze({
            marginBottom: 16,
        }),
        contributorEntry: Object.freeze({
            paddingBottom: 16,
            marginBottom: 8,
            borderBottom: `1px solid ${COLOURS.LIGHT_BORDER_GREY}`,
        }),
        contributorNameRow: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: 4,
            marginBottom: 2,
        }),
        contributorName: Object.freeze({
            fontSize: '1rem',
            fontWeight: 600,
            color: COLOURS.PURPLE,
            textDecoration: 'none',
            '&:hover': Object.freeze({
                textDecoration: 'underline',
            }),
        }),
        externalIcon: Object.freeze({
            fontSize: 14,
            color: COLOURS.PURPLE,
        }),
        contributorType: Object.freeze({
            fontSize: '0.85rem',
            color: COLOURS.DARK_GREY,
            marginBottom: 6,
        }),
        listEntry: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            paddingLeft: 8,
            marginBottom: 4,
        }),
        listIcon: Object.freeze({
            fontSize: 14,
            color: COLOURS.DARK_GREY,
            flexShrink: 0,
        }),
        listName: Object.freeze({
            fontSize: '0.85rem',
            color: COLOURS.DARK_GREY,
        }),
        sectionHeader: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            marginTop: 24,
            marginBottom: 12,
        }),
        sectionHeaderIcon: Object.freeze({
            fontSize: 20,
            color: COLOURS.NEAR_BLACK,
        }),
        sectionTitle: Object.freeze({
            fontWeight: 700,
            fontSize: '1rem',
            color: COLOURS.NEAR_BLACK,
        }),
        anonymizedType: Object.freeze({
            fontSize: '0.95rem',
            color: COLOURS.NEAR_BLACK,
            lineHeight: 1.8,
        }),
    });
