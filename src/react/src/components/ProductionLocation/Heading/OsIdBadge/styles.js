import COLOURS from '../../../../util/COLOURS';

export default theme => {
    const spacing = theme.spacing.unit ?? 8;
    return Object.freeze({
        /*
        The OS ID shares a row with the data labels legend (OSDEV-3239), so the
        copy actions sit under the ID rather than beside it. That keeps the
        column tidy at any width and leaves the ID as the dominant element.
        */
        osIdRow: {
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            gap: `${spacing}px`,
            padding: '14px 20px',
            backgroundColor: COLOURS.LIGHT_LAVENDER,
            [theme.breakpoints.down(450)]: {
                padding: '12px 14px',
            },
        },
        osIdValueWithTooltip: Object.freeze({
            display: 'inline-flex',
            alignItems: 'center',
            gap: spacing * 0.5,
        }),
        osIdLabel: Object.freeze({
            fontWeight: 600,
            fontSize: '1rem',
        }),
        osIdValue: {
            fontWeight: 'bold',
            fontSize: '1.5rem',
            [theme.breakpoints.down(450)]: {
                fontSize: '1.25rem',
                wordBreak: 'break-all',
            },
        },
        osIdInfoButton: Object.freeze({
            padding: spacing * 0.5,
            color: theme.palette.text.secondary,
            '&:hover': {
                color: theme.palette.text.primary,
                backgroundColor: theme.palette.action.hover,
            },
        }),
        osIdActions: {
            display: 'inline-flex',
            flexWrap: 'wrap',
            gap: `${spacing}px`,
            [theme.breakpoints.down(450)]: {
                width: '100%',
            },
        },
        copyButtonWrap: {
            backgroundColor: COLOURS.WHITE,
            display: 'inline-flex',
            [theme.breakpoints.down(450)]: {
                flex: 1,
            },
        },
        copyButton: {
            textTransform: 'none',
            minWidth: 'auto',
            padding: '4px 10px',
            [theme.breakpoints.down(450)]: {
                flex: 1,
                width: '100%',
            },
        },
        buttonText: Object.freeze({
            marginLeft: spacing * 0.5,
            fontSize: '12px',
        }),
    });
};
