import COLOURS from '../../../util/COLOURS';

export default theme =>
    Object.freeze({
        container: Object.freeze({
            borderTop: `2px solid ${COLOURS.LIGHT_GREY}`,
            paddingTop: theme.spacing.unit * 3,
            paddingBottom: theme.spacing.unit * 3,
        }),
        title: Object.freeze({
            fontWeight: 700,
            fontSize: '1rem',
            color: COLOURS.NEAR_BLACK,
            marginBottom: theme.spacing.unit,
        }),
        subtitle: Object.freeze({
            fontSize: '0.9rem',
            color: COLOURS.DARK_GREY,
            marginBottom: theme.spacing.unit * 2,
        }),
        typeCounts: Object.freeze({
            marginBottom: theme.spacing.unit * 2,
        }),
        typeCount: Object.freeze({
            fontSize: '0.9rem',
            color: COLOURS.NEAR_BLACK,
            lineHeight: 1.8,
        }),
        typeCountNumber: Object.freeze({
            fontWeight: 700,
        }),
        contributorList: Object.freeze({
            marginBottom: theme.spacing.unit * 2,
        }),
        contributorLink: Object.freeze({
            display: 'block',
            fontSize: '0.9rem',
            color: COLOURS.NEAR_BLACK,
            textDecoration: 'none',
            lineHeight: 1.8,
            '&:hover': Object.freeze({
                textDecoration: 'underline',
            }),
        }),
        triggerButton: Object.freeze({
            fontWeight: 400,
            fontSize: '0.9rem',
            textTransform: 'none',
            color: COLOURS.PURPLE,
            padding: 0,
            minHeight: 'auto',
            '&:hover': Object.freeze({
                backgroundColor: 'transparent',
                textDecoration: 'underline',
            }),
        }),
    });
