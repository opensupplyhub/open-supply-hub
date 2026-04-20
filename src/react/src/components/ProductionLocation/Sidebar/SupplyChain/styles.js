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
            fontWeight: 600,
            fontSize: '1.25rem',
            marginBottom: theme.spacing.unit,
        }),
        subtitle: Object.freeze({
            color: theme.palette.text.secondary,
            fontSize: '1rem',
            marginBottom: theme.spacing.unit * 2,
        }),
        typeCounts: Object.freeze({
            flexWrap: 'wrap',
            gap: '6px',
            marginBottom: theme.spacing.unit * 2,
        }),
        typeCount: Object.freeze({
            display: 'inline-block',
            fontSize: '0.9rem',
            color: theme.palette.text.primary,
            backgroundColor: COLOURS.LIGHT_GREY,
            padding: '2px 10px',
        }),
        contributorList: Object.freeze({
            marginBottom: theme.spacing.unit * 2,
            gap: '8px',
            flexDirection: 'column',
        }),
        contributorLink: Object.freeze({
            display: 'block',
            fontSize: '1rem',
            color: theme.palette.text.primary,
            textDecoration: 'none',
            transition: 'background-color 0.2s ease',
            padding: '8px',
            fontWeight: 500,
            '&:hover': {
                backgroundColor: COLOURS.HOVER_GREY,
                color: theme.palette.primary.main,
            },
        }),
        triggerButton: Object.freeze({
            fontSize: '1rem',
            textTransform: 'none',
            color: COLOURS.PURPLE,
            minHeight: 'auto',
            fontWeight: 500,
            width: '100%',
            padding: '8px 0',
            '&:hover': {
                backgroundColor: COLOURS.HOVER_GREY,
                color: theme.palette.primary.main,
            },
        }),
    });
