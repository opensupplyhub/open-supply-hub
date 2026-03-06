import COLOURS from '../../../../../util/COLOURS';

export default () =>
    Object.freeze({
        drawerPaper: Object.freeze({
            width: '390px',
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
            marginBottom: '12px',
        }),
        headerLeft: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '8px',
        }),
        titleIcon: Object.freeze({
            fontSize: '1.5rem',
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
            marginTop: '8px',
            marginBottom: '0px',
            fontSize: '1rem',
            lineHeight: 1.4,
            color: COLOURS.DARK_GREY,
            paddingBottom: '16px',
        }),
        closeButton: Object.freeze({
            margin: '-8px',
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
            marginBottom: '8px',
            lineHeight: 1.2,
        }),
        infoBox: Object.freeze({
            backgroundColor: COLOURS.EXTRA_LIGHT_BLUE,
            border: `1px solid #C0DBFE`,
            padding: '16px',
            marginBottom: '16px',
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
        infoText: Object.freeze({
            fontSize: '1rem',
            lineHeight: 1.5,
            color: COLOURS.DARK_GREY,
        }),
        learnMoreLink: Object.freeze({
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
        learnMoreArrow: Object.freeze({
            marginLeft: '4px',
            marginTop: '2px',
        }),
        typeSummary: Object.freeze({
            display: 'flex',
            flexWrap: 'wrap',
            gap: 6,
            marginBottom: '16px',
        }),
        typeChip: Object.freeze({
            display: 'inline-block',
            fontSize: '0.85rem',
            color: COLOURS.NEAR_BLACK,
            backgroundColor: COLOURS.LIGHT_GREY,
            padding: '2px 10px',
        }),
        listScroll: Object.freeze({
            maxHeight: '320px',
            overflowY: 'auto',
        }),
        contributorEntry: Object.freeze({
            backgroundColor: COLOURS.WHITE,
            border: `1px solid ${COLOURS.LIGHT_BORDER_GREY}`,
            padding: '16px',
            marginBottom: '8px',
        }),
        contributorName: Object.freeze({
            display: 'inline-flex',
            alignItems: 'center',
            gap: 4,
            fontSize: '1rem',
            fontWeight: 600,
            color: COLOURS.PURPLE,
            textDecoration: 'none',
            marginBottom: 2,
            overflowWrap: 'break-word',
            '&:hover': Object.freeze({
                textDecoration: 'underline',
            }),
        }),
        contributorType: Object.freeze({
            fontSize: '0.85rem',
            color: COLOURS.DARK_GREY,
            marginBottom: 6,
        }),
        listEntry: Object.freeze({
            border: `1px solid ${COLOURS.LIGHT_BORDER_GREY}`,
            padding: '8px 12px',
            marginBottom: '8px',
            backgroundColor: COLOURS.WHITE,
        }),
        listEntryLabel: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: 4,
            fontSize: '0.75rem',
            color: COLOURS.DARK_GREY,
            marginBottom: 2,
        }),
        listIcon: Object.freeze({
            fontSize: 14,
            color: COLOURS.DARK_GREY,
            flexShrink: 0,
        }),
        listName: Object.freeze({
            fontSize: '0.875rem',
            color: COLOURS.NEAR_BLACK,
            fontWeight: 500,
        }),
        anonymizedType: Object.freeze({
            fontSize: '1rem',
            color: COLOURS.NEAR_BLACK,
            lineHeight: 1.8,
        }),
    });
