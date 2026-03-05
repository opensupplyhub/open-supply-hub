import COLOURS from '../../../../../util/COLOURS';

export default theme =>
    Object.freeze({
        drawerPaper: Object.freeze({
            maxWidth: '560px',
            minWidth: '33%',
            boxShadow: '-4px 0 24px rgba(0,0,0,0.12)',
        }),
        drawerContent: Object.freeze({
            padding: '1rem 4.5rem',
            overflowY: 'auto',
            height: '100%',
        }),
        header: Object.freeze({
            display: 'flex',
            justifyContent: 'flex-end',
            alignItems: 'center',
        }),
        closeButton: Object.freeze({}),
        title: Object.freeze({
            fontWeight: 900,
            fontSize: '2rem',
            color: COLOURS.NEAR_BLACK,
            marginBottom: theme.spacing.unit,
        }),
        subtitle: Object.freeze({
            fontWeight: 600,
            fontSize: '1rem',
            color: COLOURS.DARK_GREY,
            marginBottom: '2rem',
        }),
        infoBox: Object.freeze({
            backgroundColor: COLOURS.EXTRA_LIGHT_BLUE,
            border: `1px solid ${COLOURS.LIGHT_BLUE_BORDER}`,
            padding: theme.spacing.unit * 2,
            marginBottom: theme.spacing.unit * 2,
            display: 'flex',
            alignItems: 'flex-start',
            gap: theme.spacing.unit,
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
            display: 'flex',
            flexWrap: 'wrap',
            gap: 6,
            marginBottom: theme.spacing.unit * 2,
        }),
        typeChip: Object.freeze({
            display: 'inline-block',
            fontSize: '0.85rem',
            color: COLOURS.NEAR_BLACK,
            backgroundColor: COLOURS.LIGHT_GREY,
            padding: '2px 10px',
        }),
        divider: Object.freeze({
            marginBottom: theme.spacing.unit * 2,
        }),
        contributorEntry: Object.freeze({
            boxShadow: '0px 1px 0px 0px rgb(240, 240, 240)',
            paddingTop: theme.spacing.unit,
            paddingBottom: theme.spacing.unit,
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
        externalLinkIcon: Object.freeze({
            fontSize: 14,
            verticalAlign: 'middle',
            flexShrink: 0,
        }),
        contributorType: Object.freeze({
            fontSize: '0.85rem',
            color: COLOURS.DARK_GREY,
            marginBottom: 6,
        }),
        listEntry: Object.freeze({
            border: `1px solid ${COLOURS.LIGHT_BORDER_GREY}`,
            padding: `${theme.spacing.unit}px ${theme.spacing.unit * 1.5}px`,
            marginBottom: theme.spacing.unit,
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
        sectionHeader: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: theme.spacing.unit,
            marginTop: theme.spacing.unit * 3,
            marginBottom: theme.spacing.unit * 1.5,
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
