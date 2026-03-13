import COLOURS from '../../../../util/COLOURS';
import commonStyles from '../../commonStyles';

export default theme =>
    Object.freeze({
        container: Object.freeze({
            ...commonStyles(theme).container,
            padding: '12px',
            marginBottom: theme.spacing.unit,
            minWidth: 0,
            wordBreak: 'break-word',
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
            display: 'flex',
            flexWrap: 'wrap',
            gap: '6px',
            marginBottom: theme.spacing.unit * 2,
        }),
        typeCount: Object.freeze({
            display: 'inline-block',
            fontSize: '0.85rem',
            color: COLOURS.NEAR_BLACK,
            backgroundColor: COLOURS.LIGHT_GREY,
            padding: '2px 10px',
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
