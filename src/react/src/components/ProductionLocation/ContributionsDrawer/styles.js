import COLOURS from '../../../util/COLOURS';

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
        supportLink: Object.freeze({
            color: COLOURS.PURPLE,
            textDecoration: 'none',
            '&:hover': Object.freeze({
                textDecoration: 'underline',
            }),
        }),
        listScroll: Object.freeze({
            maxHeight: 320,
            overflowY: 'auto',
        }),
    });
